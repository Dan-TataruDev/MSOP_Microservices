"""Inventory schemas."""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.inventory import ItemCategory, TransactionType


class InventoryItemBase(BaseModel):
    name: str
    sku: str
    category: ItemCategory
    description: Optional[str] = None
    unit: str = "units"
    low_threshold: int = 10
    critical_threshold: int = 5
    reorder_quantity: int = 50
    unit_cost: Optional[float] = None
    venue_id: Optional[UUID] = None
    storage_location: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    quantity: int = 0


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    low_threshold: Optional[int] = None
    critical_threshold: Optional[int] = None
    reorder_quantity: Optional[int] = None
    unit_cost: Optional[float] = None
    storage_location: Optional[str] = None


class InventoryItemResponse(InventoryItemBase):
    id: UUID
    quantity: int
    is_low_stock: bool
    is_critical_stock: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    quantity_change: int
    transaction_type: TransactionType
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    notes: Optional[str] = None


class StockTransactionResponse(BaseModel):
    id: UUID
    item_id: UUID
    transaction_type: TransactionType
    quantity_change: int
    quantity_after: int
    reference_type: Optional[str]
    reference_id: Optional[UUID]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LowStockAlert(BaseModel):
    item_id: UUID
    sku: str
    name: str
    current_quantity: int
    low_threshold: int
    critical_threshold: int
    is_critical: bool
    reorder_quantity: int


