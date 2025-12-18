"""Inventory API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.services.inventory_service import inventory_service
from app.models.inventory import ItemCategory, TransactionType
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    StockAdjustment, StockTransactionResponse, LowStockAlert
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/items", response_model=InventoryItemResponse, status_code=201)
def create_item(item_data: InventoryItemCreate, db: Session = Depends(get_db)):
    """Create a new inventory item."""
    existing = inventory_service.get_item_by_sku(db, item_data.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    return inventory_service.create_item(db, item_data)


@router.get("/items", response_model=List[InventoryItemResponse])
def list_items(
    venue_id: Optional[UUID] = None,
    category: Optional[ItemCategory] = None,
    db: Session = Depends(get_db)
):
    """List inventory items with optional filters."""
    return inventory_service.list_items(db, venue_id, category)


@router.get("/items/{item_id}", response_model=InventoryItemResponse)
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    """Get inventory item by ID."""
    item = inventory_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/items/{item_id}", response_model=InventoryItemResponse)
def update_item(item_id: UUID, update_data: InventoryItemUpdate, db: Session = Depends(get_db)):
    """Update inventory item details."""
    item = inventory_service.update_item(db, item_id, update_data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/items/{item_id}/adjust", response_model=StockTransactionResponse)
def adjust_stock(item_id: UUID, adjustment: StockAdjustment, db: Session = Depends(get_db)):
    """Adjust stock level for an item. Emits alerts if thresholds are crossed."""
    transaction = inventory_service.adjust_stock(
        db=db,
        item_id=item_id,
        quantity_change=adjustment.quantity_change,
        transaction_type=adjustment.transaction_type,
        reference_type=adjustment.reference_type,
        reference_id=adjustment.reference_id,
        notes=adjustment.notes,
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Item not found")
    return transaction


@router.get("/items/{item_id}/transactions", response_model=List[StockTransactionResponse])
def get_transactions(item_id: UUID, limit: int = Query(50, le=100), db: Session = Depends(get_db)):
    """Get transaction history for an item."""
    return inventory_service.get_transactions(db, item_id, limit)


@router.get("/alerts/low-stock", response_model=List[LowStockAlert])
def get_low_stock_alerts(venue_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    """Get all items below low stock threshold."""
    return inventory_service.get_low_stock_items(db, venue_id)


