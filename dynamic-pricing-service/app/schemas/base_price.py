"""
Pydantic schemas for base price management APIs.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.models.base_price import VenueType


class BasePriceCreate(BaseModel):
    """Schema for creating a base price."""
    venue_id: UUID = Field(..., description="Venue ID")
    venue_type: VenueType = Field(..., description="Venue type")
    venue_name: Optional[str] = Field(None, max_length=255, description="Venue name")
    
    # Product (optional for granular pricing)
    product_id: Optional[UUID] = Field(None, description="Product/service ID")
    product_name: Optional[str] = Field(None, max_length=255, description="Product name")
    product_category: Optional[str] = Field(None, max_length=100, description="Product category")
    
    # Pricing
    base_price: Decimal = Field(..., ge=0, description="Base price")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    
    price_type: str = Field(default="per_unit", description="Price type")
    unit_description: Optional[str] = Field(None, description="Unit description")
    
    # Guardrails
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum price floor")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum price ceiling")
    
    # Tax
    tax_rate: Decimal = Field(default=Decimal("0.10"), ge=0, le=1, description="Tax rate (0-1)")
    tax_included: bool = Field(default=False, description="Is tax included in base price")
    
    # Validity
    valid_from: Optional[datetime] = Field(None, description="Price valid from")
    valid_until: Optional[datetime] = Field(None, description="Price valid until")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "venue_id": "223e4567-e89b-12d3-a456-426614174000",
                "venue_type": "restaurant",
                "venue_name": "Fine Dining Restaurant",
                "base_price": "100.00",
                "currency": "USD",
                "price_type": "per_person",
                "unit_description": "Per person, per meal",
                "min_price": "50.00",
                "max_price": "300.00",
                "tax_rate": "0.10",
                "tax_included": False
            }
        }


class BasePriceUpdate(BaseModel):
    """Schema for updating a base price."""
    venue_name: Optional[str] = None
    product_name: Optional[str] = None
    product_category: Optional[str] = None
    
    base_price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = None
    
    price_type: Optional[str] = None
    unit_description: Optional[str] = None
    
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    tax_included: Optional[bool] = None
    
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    
    is_active: Optional[bool] = None
    
    metadata: Optional[Dict[str, Any]] = None


class BasePriceResponse(BaseModel):
    """Response schema for a base price."""
    id: UUID
    venue_id: UUID
    venue_type: VenueType
    venue_name: Optional[str]
    
    product_id: Optional[UUID]
    product_name: Optional[str]
    product_category: Optional[str]
    
    base_price: Decimal
    currency: str
    
    price_type: str
    unit_description: Optional[str]
    
    min_price: Optional[Decimal]
    max_price: Optional[Decimal]
    
    tax_rate: Decimal
    tax_included: bool
    
    valid_from: datetime
    valid_until: Optional[datetime]
    
    version: int
    is_active: bool
    
    metadata: Optional[Dict[str, Any]]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BasePriceListResponse(BaseModel):
    """Response schema for paginated base price list."""
    prices: List[BasePriceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


