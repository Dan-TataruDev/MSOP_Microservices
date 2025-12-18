"""
FastAPI dependencies for authentication and common functionality.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from uuid import UUID
from app.config import settings

# HTTP Bearer token security scheme
security = HTTPBearer()


class CurrentUser(BaseModel):
    """Represents the currently authenticated user."""
    user_id: str
    email: Optional[str] = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Dependency to extract and validate the current user from JWT token.
    
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    token = credentials.credentials
    
    try:
        # Decode and validate the JWT token
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Extract user_id - check both 'sub' and 'user_id' for compatibility
        user_id = payload.get("sub") or payload.get("user_id")
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
        
    except JWTError as e:
        # Check if it's an expiration error
        if "expired" in str(e).lower() or "exp" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
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
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            return None
        
        return CurrentUser(
            user_id=str(user_id),
            email=payload.get("email")
        )
    except JWTError:
        # For optional auth, invalid tokens are treated as no auth
        return None

