"""
Common schemas used across the service.

Provides reusable response structures for consistency.
"""

from typing import Generic, TypeVar, List, Optional

from fastapi import Query
from pydantic import BaseModel, Field

# Generic type for paginated items
T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.
    
    Usage in routes:
        async def list_items(
            page: int = Query(1, ge=1),
            page_size: int = Query(20, ge=1, le=100)
        ):
            ...
    """
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate the database offset for this page."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.
    
    Provides consistent pagination metadata across all list endpoints.
    Frontend can use this to build pagination UI components.
    """
    items: List[T]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_prev: bool = Field(description="Whether there are previous pages")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """Factory method to create a paginated response."""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class SuccessResponse(BaseModel):
    """
    Generic success response for operations that don't return data.
    
    Provides a consistent structure for the frontend to check.
    """
    success: bool = True
    message: Optional[str] = None


class MessageResponse(BaseModel):
    """
    Response with a message, used for confirmations.
    """
    message: str


