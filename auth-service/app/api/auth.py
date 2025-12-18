"""
API endpoints for authentication (register, login, token refresh).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    AuthResponse,
    RefreshTokenRequest,
    UserResponse,
    UserUpdate,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    ApiResponseWrapper,
    TokenResponseWrapper,
    UserResponseWrapper,
)
from app.services.auth_service import AuthService
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.config import settings
from uuid import UUID
from datetime import datetime
from app.models.user import User, UserRole

router = APIRouter(prefix="/auth", tags=["auth"])

# Hardcoded admin credentials for easy development access
HARDCODED_ADMIN_EMAIL = "admin@example.com"
HARDCODED_ADMIN_PASSWORD = "admin123"
HARDCODED_ADMIN_ID = UUID("00000000-0000-0000-0000-000000000001")  # Fixed UUID for consistent tokens


def create_hardcoded_admin_user() -> User:
    """Create a mock admin user object for hardcoded credentials."""
    admin = User()
    admin.id = HARDCODED_ADMIN_ID
    admin.email = HARDCODED_ADMIN_EMAIL
    admin.name = "Admin User"
    admin.role = UserRole.ADMIN.value
    admin.is_active = True
    admin.is_verified = True
    admin.created_at = datetime.now()
    admin.updated_at = datetime.now()
    admin.last_login_at = None
    return admin

security = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """Extract and validate user ID from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return UUID(user_id)


@router.post("/register", response_model=ApiResponseWrapper, status_code=status.HTTP_201_CREATED)
def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user with email already exists
    existing_user = AuthService.get_user_by_email(db, register_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Create user
    user = AuthService.create_user(db, register_data)
    
    # Create tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    auth_response = AuthResponse(
        user=UserResponse.from_orm_model(user),
        tokens=TokenResponse(
            accessToken=access_token,
            refreshToken=refresh_token,
            expiresIn=settings.jwt_access_token_expire_minutes * 60,
        )
    )
    
    return ApiResponseWrapper(
        data=auth_response,
        message="User registered successfully"
    )


@router.post("/login", response_model=ApiResponseWrapper)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = None
    
    # Check for hardcoded admin credentials first (bypass database)
    if login_data.email == HARDCODED_ADMIN_EMAIL and login_data.password == HARDCODED_ADMIN_PASSWORD:
        user = create_hardcoded_admin_user()
    else:
        # Normal database authentication
        user = AuthService.authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        # Update last login for database users only
        AuthService.update_last_login(db, user.id)
    
    # Create tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    auth_response = AuthResponse(
        user=UserResponse.from_orm_model(user),
        tokens=TokenResponse(
            accessToken=access_token,
            refreshToken=refresh_token,
            expiresIn=settings.jwt_access_token_expire_minutes * 60,
        )
    )
    
    return ApiResponseWrapper(
        data=auth_response,
        message="Login successful"
    )


@router.post("/refresh", response_model=TokenResponseWrapper)
def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_data.refreshToken)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user_id_uuid = UUID(user_id)
    
    # Check if it's the hardcoded admin
    if user_id_uuid == HARDCODED_ADMIN_ID:
        user = create_hardcoded_admin_user()
    else:
        # Verify user still exists and is active
        user = AuthService.get_user_by_id(db, user_id_uuid)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
    
    # Create new tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    token_response = TokenResponse(
        accessToken=access_token,
        refreshToken=new_refresh_token,
        expiresIn=settings.jwt_access_token_expire_minutes * 60,
    )
    
    return TokenResponseWrapper(
        data=token_response,
        message="Token refreshed successfully"
    )


@router.post("/logout")
def logout():
    """Logout (client should discard tokens)."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponseWrapper)
def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get current authenticated user."""
    # Check if it's the hardcoded admin
    if user_id == HARDCODED_ADMIN_ID:
        user = create_hardcoded_admin_user()
    else:
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    return UserResponseWrapper(
        data=UserResponse.from_orm_model(user),
        message="User retrieved successfully"
    )


@router.patch("/profile", response_model=UserResponseWrapper)
def update_profile(
    update_data: UserUpdate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    # Check if email is being changed and if it's already taken
    if update_data.email:
        existing = AuthService.get_user_by_email(db, update_data.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
    
    user = AuthService.update_user(db, user_id, update_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponseWrapper(
        data=UserResponse.from_orm_model(user),
        message="Profile updated successfully"
    )


@router.post("/change-password")
def change_password(
    password_data: PasswordChangeRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Change user password."""
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.currentPassword, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    AuthService.update_password(db, user_id, password_data.newPassword)
    
    return {"message": "Password changed successfully"}


@router.post("/password-reset/request")
def request_password_reset(reset_data: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset (send email with reset token)."""
    # In production, send email with reset token
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset/confirm")
def confirm_password_reset(reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Confirm password reset with token."""
    # In production, verify reset token and update password
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset not yet implemented"
    )

