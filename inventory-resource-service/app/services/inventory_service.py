"""Inventory service with stock management and threshold detection."""
import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.inventory import InventoryItem, StockTransaction, TransactionType, ItemCategory
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate, StockAdjustment, LowStockAlert
from app.events.publisher import event_publisher

logger = logging.getLogger(__name__)


class InventoryService:
    """Manages inventory items and stock levels with automatic threshold detection."""
    
    def create_item(self, db: Session, item_data: InventoryItemCreate) -> InventoryItem:
        """Create a new inventory item."""
        item = InventoryItem(**item_data.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info(f"Created inventory item: {item.sku}")
        return item
    
    def get_item(self, db: Session, item_id: UUID) -> Optional[InventoryItem]:
        """Get inventory item by ID."""
        return db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    
    def get_item_by_sku(self, db: Session, sku: str) -> Optional[InventoryItem]:
        """Get inventory item by SKU."""
        return db.query(InventoryItem).filter(InventoryItem.sku == sku).first()
    
    def list_items(
        self, db: Session, venue_id: Optional[UUID] = None, category: Optional[ItemCategory] = None
    ) -> List[InventoryItem]:
        """List inventory items with optional filters."""
        query = db.query(InventoryItem)
        if venue_id:
            query = query.filter(InventoryItem.venue_id == venue_id)
        if category:
            query = query.filter(InventoryItem.category == category)
        return query.all()
    
    def update_item(self, db: Session, item_id: UUID, update_data: InventoryItemUpdate) -> Optional[InventoryItem]:
        """Update inventory item details (not stock level)."""
        item = self.get_item(db, item_id)
        if not item:
            return None
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item
    
    def adjust_stock(
        self,
        db: Session,
        item_id: UUID,
        quantity_change: int,
        transaction_type: TransactionType,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None,
        notes: Optional[str] = None,
        created_by: Optional[UUID] = None,
    ) -> Optional[StockTransaction]:
        """
        Adjust stock level and check thresholds.
        This is the core method that maintains inventory state deterministically.
        """
        item = self.get_item(db, item_id)
        if not item:
            return None
        
        # Calculate new quantity
        new_quantity = item.quantity + quantity_change
        if new_quantity < 0:
            logger.warning(f"Stock adjustment would result in negative quantity for {item.sku}")
            new_quantity = 0
        
        # Track previous state for threshold detection
        was_low = item.is_low_stock
        was_critical = item.is_critical_stock
        
        # Update stock level
        item.quantity = new_quantity
        
        # Create transaction record
        transaction = StockTransaction(
            item_id=item_id,
            transaction_type=transaction_type,
            quantity_change=quantity_change,
            quantity_after=new_quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            created_by=created_by,
        )
        db.add(transaction)
        db.commit()
        db.refresh(item)
        
        # Emit stock update event
        event_publisher.publish_stock_updated(item_id, {
            "sku": item.sku,
            "quantity_change": quantity_change,
            "quantity_after": new_quantity,
            "transaction_type": transaction_type.value,
        })
        
        # Check thresholds and emit alerts
        self._check_thresholds(item, was_low, was_critical)
        
        return transaction
    
    def _check_thresholds(self, item: InventoryItem, was_low: bool, was_critical: bool) -> None:
        """Check stock thresholds and emit alerts when crossed."""
        alert_data = {
            "item_id": str(item.id),
            "sku": item.sku,
            "name": item.name,
            "current_quantity": item.quantity,
            "low_threshold": item.low_threshold,
            "critical_threshold": item.critical_threshold,
            "reorder_quantity": item.reorder_quantity,
        }
        
        # Critical threshold crossed (going down)
        if item.is_critical_stock and not was_critical:
            logger.warning(f"Critical stock level reached for {item.sku}: {item.quantity}")
            event_publisher.publish_critical_stock_alert(alert_data)
            event_publisher.publish_restock_required(alert_data)
        # Low threshold crossed (going down)
        elif item.is_low_stock and not was_low:
            logger.info(f"Low stock level reached for {item.sku}: {item.quantity}")
            event_publisher.publish_low_stock_alert(alert_data)
    
    def get_low_stock_items(self, db: Session, venue_id: Optional[UUID] = None) -> List[LowStockAlert]:
        """Get all items below low stock threshold."""
        query = db.query(InventoryItem).filter(InventoryItem.quantity <= InventoryItem.low_threshold)
        if venue_id:
            query = query.filter(InventoryItem.venue_id == venue_id)
        
        items = query.all()
        return [
            LowStockAlert(
                item_id=item.id,
                sku=item.sku,
                name=item.name,
                current_quantity=item.quantity,
                low_threshold=item.low_threshold,
                critical_threshold=item.critical_threshold,
                is_critical=item.is_critical_stock,
                reorder_quantity=item.reorder_quantity,
            )
            for item in items
        ]
    
    def get_transactions(self, db: Session, item_id: UUID, limit: int = 50) -> List[StockTransaction]:
        """Get transaction history for an item."""
        return (
            db.query(StockTransaction)
            .filter(StockTransaction.item_id == item_id)
            .order_by(StockTransaction.created_at.desc())
            .limit(limit)
            .all()
        )


inventory_service = InventoryService()


