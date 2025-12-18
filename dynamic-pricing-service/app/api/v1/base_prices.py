"""
Base Prices management API endpoints.

CRUD operations for base prices that serve as the
foundation for dynamic pricing calculations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models.base_price import BasePrice, VenueType
from app.schemas.base_price import (
    BasePriceCreate,
    BasePriceUpdate,
    BasePriceResponse,
    BasePriceListResponse,
)

router = APIRouter(prefix="/base-prices", tags=["Base Prices"])


@router.post(
    "",
    response_model=BasePriceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a base price",
    description="""
    Create a new base price for a venue or product.
    
    Base prices are the starting point for all dynamic pricing calculations.
    They represent the "normal" price before any adjustments.
    """
)
async def create_base_price(
    price_data: BasePriceCreate,
    db: Session = Depends(get_db),
    created_by: Optional[str] = Query(None, description="User creating the price"),
) -> BasePriceResponse:
    """Create a new base price."""
    # Check for existing active price for same venue/product
    existing = db.query(BasePrice).filter(
        BasePrice.venue_id == price_data.venue_id,
        BasePrice.product_id == price_data.product_id,
        BasePrice.is_active == True,
    ).first()
    
    if existing:
        # Deactivate existing price
        existing.is_active = False
        existing.valid_until = datetime.utcnow()
    
    base_price = BasePrice(
        venue_id=price_data.venue_id,
        venue_type=price_data.venue_type,
        venue_name=price_data.venue_name,
        product_id=price_data.product_id,
        product_name=price_data.product_name,
        product_category=price_data.product_category,
        base_price=price_data.base_price,
        currency=price_data.currency,
        price_type=price_data.price_type,
        unit_description=price_data.unit_description,
        min_price=price_data.min_price,
        max_price=price_data.max_price,
        tax_rate=price_data.tax_rate,
        tax_included=price_data.tax_included,
        valid_from=price_data.valid_from or datetime.utcnow(),
        valid_until=price_data.valid_until,
        metadata=price_data.metadata,
        created_by=created_by,
    )
    
    db.add(base_price)
    db.commit()
    db.refresh(base_price)
    
    return _price_to_response(base_price)


@router.get(
    "",
    response_model=BasePriceListResponse,
    summary="List base prices",
    description="Get a paginated list of base prices with optional filtering."
)
async def list_base_prices(
    venue_id: Optional[UUID] = Query(None, description="Filter by venue ID"),
    venue_type: Optional[VenueType] = Query(None, description="Filter by venue type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
) -> BasePriceListResponse:
    """List base prices with filtering."""
    query = db.query(BasePrice)
    
    if venue_id:
        query = query.filter(BasePrice.venue_id == venue_id)
    if venue_type:
        query = query.filter(BasePrice.venue_type == venue_type)
    if is_active is not None:
        query = query.filter(BasePrice.is_active == is_active)
    
    total = query.count()
    
    prices = (
        query
        .order_by(BasePrice.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    
    price_responses = [_price_to_response(p) for p in prices]
    total_pages = (total + page_size - 1) // page_size
    
    return BasePriceListResponse(
        prices=price_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/venue/{venue_id}",
    response_model=List[BasePriceResponse],
    summary="Get base prices for a venue",
    description="Get all active base prices for a specific venue."
)
async def get_venue_prices(
    venue_id: UUID,
    db: Session = Depends(get_db),
) -> List[BasePriceResponse]:
    """Get all base prices for a venue."""
    prices = db.query(BasePrice).filter(
        BasePrice.venue_id == venue_id,
        BasePrice.is_active == True,
    ).all()
    
    return [_price_to_response(p) for p in prices]


@router.get(
    "/{price_id}",
    response_model=BasePriceResponse,
    summary="Get a base price",
    description="Get details of a specific base price by ID."
)
async def get_base_price(
    price_id: UUID,
    db: Session = Depends(get_db),
) -> BasePriceResponse:
    """Get a single base price."""
    price = db.query(BasePrice).filter(BasePrice.id == price_id).first()
    
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Base price {price_id} not found"
        )
    
    return _price_to_response(price)


@router.patch(
    "/{price_id}",
    response_model=BasePriceResponse,
    summary="Update a base price",
    description="Update an existing base price. Creates a new version."
)
async def update_base_price(
    price_id: UUID,
    price_data: BasePriceUpdate,
    db: Session = Depends(get_db),
    updated_by: Optional[str] = Query(None, description="User updating the price"),
) -> BasePriceResponse:
    """Update a base price."""
    price = db.query(BasePrice).filter(BasePrice.id == price_id).first()
    
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Base price {price_id} not found"
        )
    
    # Update fields
    update_data = price_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(price, field, value)
    
    price.version += 1
    price.updated_by = updated_by
    
    db.commit()
    db.refresh(price)
    
    return _price_to_response(price)


@router.delete(
    "/{price_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a base price",
    description="Deactivate a base price. The price will no longer be used."
)
async def deactivate_base_price(
    price_id: UUID,
    db: Session = Depends(get_db),
):
    """Deactivate a base price."""
    price = db.query(BasePrice).filter(BasePrice.id == price_id).first()
    
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Base price {price_id} not found"
        )
    
    price.is_active = False
    price.valid_until = datetime.utcnow()
    db.commit()


def _price_to_response(price: BasePrice) -> BasePriceResponse:
    """Convert price model to response schema."""
    return BasePriceResponse(
        id=price.id,
        venue_id=price.venue_id,
        venue_type=price.venue_type,
        venue_name=price.venue_name,
        product_id=price.product_id,
        product_name=price.product_name,
        product_category=price.product_category,
        base_price=price.base_price,
        currency=price.currency,
        price_type=price.price_type,
        unit_description=price.unit_description,
        min_price=price.min_price,
        max_price=price.max_price,
        tax_rate=price.tax_rate,
        tax_included=price.tax_included,
        valid_from=price.valid_from,
        valid_until=price.valid_until,
        version=price.version,
        is_active=price.is_active,
        metadata=price.metadata,
        created_at=price.created_at,
        updated_at=price.updated_at,
    )


