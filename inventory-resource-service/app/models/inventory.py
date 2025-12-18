"""Inventory item database models."""
from sqlalchemy import Column, String, Integer, DateTime, Numeric, Text, Enum, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum
from app.database import Base


class ItemCategory(str, enum.Enum):
    CONSUMABLE = "consumable"
    AMENITY = "amenity"
    LINEN = "linen"
    CLEANING = "cleaning"
    FOOD_BEVERAGE = "food_beverage"
    EQUIPMENT = "equipment"


class TransactionType(str, enum.Enum):
    RESTOCK = "restock"
    USAGE = "usage"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"
    WRITE_OFF = "write_off"


class InventoryItem(Base):
    """Stock item with quantity tracking and thresholds."""
    __tablename__ = "inventory_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(ItemCategory), nullable=False, index=True)
    
    # Stock levels
    quantity = Column(Integer, nullable=False, default=0)
    unit = Column(String(20), nullable=False, default="units")
    
    # Thresholds for alerts
    low_threshold = Column(Integer, nullable=False, default=10)
    critical_threshold = Column(Integer, nullable=False, default=5)
    reorder_quantity = Column(Integer, nullable=False, default=50)
    
    # Pricing
    unit_cost = Column(Numeric(10, 2), nullable=True)
    
    # Location
    venue_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    storage_location = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    transactions = relationship("StockTransaction", back_populates="item", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_inventory_venue_category", "venue_id", "category"),
    )
    
    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.low_threshold
    
    @property
    def is_critical_stock(self) -> bool:
        return self.quantity <= self.critical_threshold


class StockTransaction(Base):
    """Audit log of all stock movements."""
    __tablename__ = "stock_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity_change = Column(Integer, nullable=False)  # Positive for additions, negative for removals
    quantity_after = Column(Integer, nullable=False)
    
    # Reference to source event
    reference_type = Column(String(50), nullable=True)  # booking, housekeeping, supplier
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    item = relationship("InventoryItem", back_populates="transactions")


