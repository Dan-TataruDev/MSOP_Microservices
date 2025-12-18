"""
Custom exceptions and error handlers for the Favorites & Collections Service.

Provides consistent, frontend-friendly error responses across all endpoints.
"""

from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# =============================================================================
# Custom Exception Classes
# =============================================================================

class ServiceException(Exception):
    """
    Base exception for all service-level errors.
    
    Provides a consistent structure for error handling.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[dict] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(ServiceException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found",
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier}
        )


class ForbiddenException(ServiceException):
    """Raised when a user attempts an action they don't have permission for."""
    
    def __init__(self, message: str = "You don't have permission to perform this action"):
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )


class ConflictException(ServiceException):
    """Raised when an action conflicts with existing state."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class ValidationException(ServiceException):
    """Raised when input validation fails at the service layer."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


# =============================================================================
# Error Response Model
# =============================================================================

class ErrorResponse(BaseModel):
    """
    Standard error response format.
    
    This consistent structure makes it easy for frontend clients
    to handle errors uniformly.
    """
    success: bool = False
    error_code: str
    message: str
    details: dict = {}


# =============================================================================
# Exception Handlers
# =============================================================================

async def service_exception_handler(request: Request, exc: ServiceException) -> JSONResponse:
    """Handler for all ServiceException subclasses."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details
        ).model_dump()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unexpected exceptions.
    
    In production, this prevents sensitive error details from leaking to clients.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={}
        ).model_dump()
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.
    
    Call this during application startup.
    """
    app.add_exception_handler(ServiceException, service_exception_handler)
    # Uncomment the following line to catch all unhandled exceptions:
    # app.add_exception_handler(Exception, generic_exception_handler)


