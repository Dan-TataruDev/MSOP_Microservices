"""
Pydantic schemas for authentication APIs.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class RegisterRequest(BaseModel):
    """Schema for user registration."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    accessToken: str
    refreshToken: str
    tokenType: str = "Bearer"
    expiresIn: int = 1800  # 30 minutes in seconds


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    name: str
    role: str
    isActive: bool
    isVerified: bool
    createdAt: datetime
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_model(cls, user):
        """Convert ORM model to response schema."""
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            isActive=user.is_active,
            isVerified=user.is_verified,
            createdAt=user.created_at,
        )


class AuthResponse(BaseModel):
    """Schema for authentication response with user and tokens."""
    user: UserResponse
    tokens: TokenResponse


class ApiResponseWrapper(BaseModel):
    """Wrapper for API responses to match frontend ApiResponse<T> format."""
    data: AuthResponse
    message: Optional[str] = None


class TokenResponseWrapper(BaseModel):
    """Wrapper for token responses."""
    data: TokenResponse
    message: Optional[str] = None


class UserResponseWrapper(BaseModel):
    """Wrapper for user responses."""
    data: UserResponse
    message: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh."""
    refreshToken: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None


class PasswordChangeRequest(BaseModel):
    """Schema for password change."""
    currentPassword: str
    newPassword: str = Field(..., min_length=8, max_length=100)


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    newPassword: str = Field(..., min_length=8, max_length=100)

