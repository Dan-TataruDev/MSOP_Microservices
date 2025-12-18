"""
FastAPI dependencies for authentication and common functionality.

Provides reusable dependencies that can be injected into route handlers.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel

from app.config import get_settings

settings = get_settings()

# HTTP Bearer token security scheme
security = HTTPBearer()


class TokenPayload(BaseModel):
    """
    JWT token payload structure.
    
    Assumes the auth service provides at least user_id in the token.
    Additional fields can be added as needed.
    """
    user_id: str
    email: Optional[str] = None
    exp: Optional[int] = None  # Expiration timestamp


class CurrentUser(BaseModel):
    """
    Represents the currently authenticated user.
    
    This is a lightweight model containing only what this service needs.
    Full user details should be fetched from the User Service if required.
    """
    user_id: str
    email: Optional[str] = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Dependency to extract and validate the current user from JWT token.
    
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    
    Usage:
        @router.get("/my-favorites")
        async def get_favorites(user: CurrentUser = Depends(get_current_user)):
            # user.user_id is now available
            ...
    """
    token = credentials.credentials
    
    try:
        # Decode and validate the JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extract user_id - this is required
        user_id = payload.get("user_id") or payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return CurrentUser(
            user_id=str(user_id),
            email=payload.get("email")
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[CurrentUser]:
    """
    Dependency for optional authentication.
    
    Returns None if no token is provided, otherwise validates the token.
    Useful for endpoints that behave differently for authenticated vs anonymous users.
    
    Usage:
        @router.get("/public-collection/{public_id}")
        async def get_public_collection(
            public_id: str,
            user: Optional[CurrentUser] = Depends(get_optional_user)
        ):
            # user is None if not authenticated
            ...
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id = payload.get("user_id") or payload.get("sub")
        if not user_id:
            return None
        
        return CurrentUser(
            user_id=str(user_id),
            email=payload.get("email")
        )
    except jwt.InvalidTokenError:
        # For optional auth, invalid tokens are treated as no auth
        return None


