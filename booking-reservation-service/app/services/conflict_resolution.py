"""
Conflict resolution service for handling concurrent booking operations.
Implements optimistic locking and idempotency checks.
"""
import hashlib
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from app.models.booking import Booking, IdempotencyKey
from app.config import settings


class ConflictResolutionService:
    """
    Handles conflicts in booking operations through:
    1. Optimistic locking (version field)
    2. Idempotency keys
    3. Transaction isolation
    """
    
    @staticmethod
    def check_idempotency(
        db: Session,
        idempotency_key: str,
        operation_type: str,
        request_hash: Optional[str] = None
    ) -> Optional[UUID]:
        """
        Check if an operation with this idempotency key already exists.
        
        Returns:
            booking_id if operation was already performed, None otherwise
        """
        if not idempotency_key:
            return None
        
        # Check for existing idempotency key
        existing = db.query(IdempotencyKey).filter(
            and_(
                IdempotencyKey.key == idempotency_key,
                IdempotencyKey.operation_type == operation_type,
                IdempotencyKey.expires_at > datetime.utcnow()
            )
        ).first()
        
        if existing:
            return existing.booking_id
        
        return None
    
    @staticmethod
    def create_idempotency_key(
        db: Session,
        idempotency_key: str,
        operation_type: str,
        booking_id: UUID,
        request_hash: Optional[str] = None
    ) -> IdempotencyKey:
        """
        Create an idempotency key record.
        """
        expires_at = datetime.utcnow() + timedelta(
            hours=settings.idempotency_key_ttl_hours
        )
        
        key_record = IdempotencyKey(
            key=idempotency_key,
            operation_type=operation_type,
            booking_id=booking_id,
            request_hash=request_hash,
            expires_at=expires_at
        )
        
        db.add(key_record)
        db.commit()
        return key_record
    
    @staticmethod
    def check_optimistic_lock(
        db: Session,
        booking_id: UUID,
        expected_version: int
    ) -> bool:
        """
        Check if booking version matches expected version (optimistic locking).
        
        Returns:
            True if version matches, False if conflict detected
        """
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False
        
        return booking.version == expected_version
    
    @staticmethod
    def increment_version(db: Session, booking: Booking) -> int:
        """
        Increment booking version for optimistic locking.
        """
        booking.version += 1
        db.commit()
        return booking.version
    
    @staticmethod
    def hash_request(request_data: dict) -> str:
        """
        Create a hash of request data for idempotency checking.
        """
        # Sort keys for consistent hashing
        sorted_data = json.dumps(request_data, sort_keys=True)
        return hashlib.sha256(sorted_data.encode()).hexdigest()


