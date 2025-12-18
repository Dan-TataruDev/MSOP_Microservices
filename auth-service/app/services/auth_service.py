"""
Authentication service - business logic for user authentication.
"""
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.user import User
from app.schemas.auth import RegisterRequest, UserUpdate
from app.utils.security import get_password_hash, verify_password


class AuthService:
    """Service for managing user authentication."""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, register_data: RegisterRequest) -> User:
        """Create a new user."""
        user = User(
            email=register_data.email,
            name=register_data.name,
            password_hash=get_password_hash(register_data.password),
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, update_data: UserUpdate) -> Optional[User]:
        """Update user profile."""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_password(db: Session, user_id: UUID, new_password: str) -> bool:
        """Update user password."""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def update_last_login(db: Session, user_id: UUID) -> None:
        """Update user's last login timestamp."""
        user = AuthService.get_user_by_id(db, user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            db.commit()

