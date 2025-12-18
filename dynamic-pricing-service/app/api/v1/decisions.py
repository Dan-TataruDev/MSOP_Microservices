"""
Price Decisions API endpoints.

Query and audit price decisions for transparency
and compliance purposes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models.price_decision import PriceDecision, DecisionSource, DecisionStatus
from app.services.audit_service import AuditService
from app.schemas.decision import (
    PriceDecisionResponse,
    PriceDecisionListResponse,
    DecisionAuditResponse,
    DecisionStatusUpdate,
)

router = APIRouter(prefix="/decisions", tags=["Price Decisions"])


@router.get(
    "",
    response_model=PriceDecisionListResponse,
    summary="List price decisions",
    description="""
    Query price decisions with filtering options.
    
    Use this for:
    - Auditing pricing decisions
    - Analytics and reporting
    - Customer dispute resolution
    """
)
async def list_decisions(
    venue_id: Optional[UUID] = Query(None, description="Filter by venue ID"),
    venue_type: Optional[str] = Query(None, description="Filter by venue type"),
    guest_id: Optional[UUID] = Query(None, description="Filter by guest ID"),
    booking_id: Optional[UUID] = Query(None, description="Filter by booking ID"),
    source: Optional[DecisionSource] = Query(None, description="Filter by decision source"),
    status: Optional[DecisionStatus] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
) -> PriceDecisionListResponse:
    """List price decisions with filtering."""
    query = db.query(PriceDecision)
    
    # Apply filters
    if venue_id:
        query = query.filter(PriceDecision.venue_id == venue_id)
    if venue_type:
        query = query.filter(PriceDecision.venue_type == venue_type)
    if guest_id:
        query = query.filter(PriceDecision.guest_id == guest_id)
    if booking_id:
        query = query.filter(PriceDecision.booking_id == booking_id)
    if source:
        query = query.filter(PriceDecision.source == source)
    if status:
        query = query.filter(PriceDecision.status == status)
    if date_from:
        query = query.filter(PriceDecision.created_at >= date_from)
    if date_to:
        query = query.filter(PriceDecision.created_at <= date_to)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    decisions = (
        query
        .order_by(PriceDecision.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    
    # Convert to responses
    decision_responses = [_decision_to_response(d) for d in decisions]
    
    total_pages = (total + page_size - 1) // page_size
    
    return PriceDecisionListResponse(
        decisions=decision_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{decision_reference}",
    response_model=PriceDecisionResponse,
    summary="Get a price decision",
    description="Get details of a specific price decision by reference."
)
async def get_decision(
    decision_reference: str,
    db: Session = Depends(get_db),
) -> PriceDecisionResponse:
    """Get a single price decision."""
    decision = db.query(PriceDecision).filter(
        PriceDecision.decision_reference == decision_reference
    ).first()
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision {decision_reference} not found"
        )
    
    return _decision_to_response(decision)


@router.get(
    "/{decision_reference}/audit",
    response_model=DecisionAuditResponse,
    summary="Get decision audit trail",
    description="""
    Get the complete audit trail for a price decision.
    
    Includes:
    - Full decision details
    - Version history
    - All audit events (calculated, served, accepted, etc.)
    - Related decisions for the same booking context
    """
)
async def get_decision_audit(
    decision_reference: str,
    db: Session = Depends(get_db),
) -> DecisionAuditResponse:
    """Get audit trail for a price decision."""
    decision = db.query(PriceDecision).filter(
        PriceDecision.decision_reference == decision_reference
    ).first()
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision {decision_reference} not found"
        )
    
    audit_service = AuditService(db)
    
    # Get audit events
    audit_logs = audit_service.get_decision_audit_trail(decision.id)
    audit_events = [
        {
            "action": log.action.value,
            "description": log.action_description,
            "timestamp": log.created_at.isoformat(),
            "actor": log.actor_id,
            "details": log.new_value,
        }
        for log in audit_logs
    ]
    
    # Get version history (parent decisions)
    version_history = []
    current = decision
    while current.parent_decision_id:
        parent = db.query(PriceDecision).filter(
            PriceDecision.id == current.parent_decision_id
        ).first()
        if parent:
            version_history.append({
                "version": parent.version,
                "reference": parent.decision_reference,
                "total_price": float(parent.total_price),
                "created_at": parent.created_at.isoformat(),
            })
            current = parent
        else:
            break
    
    # Get related decisions (same venue/time)
    related = (
        db.query(PriceDecision)
        .filter(
            PriceDecision.venue_id == decision.venue_id,
            PriceDecision.booking_time == decision.booking_time,
            PriceDecision.id != decision.id,
        )
        .order_by(PriceDecision.created_at.desc())
        .limit(5)
        .all()
    )
    
    related_decisions = [
        {
            "reference": d.decision_reference,
            "total_price": float(d.total_price),
            "source": d.source.value,
            "status": d.status.value,
            "created_at": d.created_at.isoformat(),
        }
        for d in related
    ]
    
    return DecisionAuditResponse(
        decision=_decision_to_response(decision),
        version_history=version_history,
        audit_events=audit_events,
        related_decisions=related_decisions,
    )


@router.patch(
    "/{decision_reference}/status",
    response_model=PriceDecisionResponse,
    summary="Update decision status",
    description="Update the status of a price decision (e.g., mark as accepted)."
)
async def update_decision_status(
    decision_reference: str,
    status_update: DecisionStatusUpdate,
    db: Session = Depends(get_db),
) -> PriceDecisionResponse:
    """Update the status of a price decision."""
    decision = db.query(PriceDecision).filter(
        PriceDecision.decision_reference == decision_reference
    ).first()
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision {decision_reference} not found"
        )
    
    # Update status
    decision.status = status_update.status
    
    if status_update.status == DecisionStatus.ACCEPTED:
        decision.accepted_at = datetime.utcnow()
        if status_update.booking_id:
            decision.booking_id = status_update.booking_id
        if status_update.booking_reference:
            decision.booking_reference = status_update.booking_reference
    elif status_update.status == DecisionStatus.SERVED:
        decision.served_at = datetime.utcnow()
    
    db.commit()
    db.refresh(decision)
    
    # Log the status change
    audit_service = AuditService(db)
    if status_update.status == DecisionStatus.ACCEPTED:
        audit_service.log_price_accepted(decision)
    elif status_update.status == DecisionStatus.SERVED:
        audit_service.log_price_served(decision)
    
    return _decision_to_response(decision)


def _decision_to_response(decision: PriceDecision) -> PriceDecisionResponse:
    """Convert decision model to response schema."""
    return PriceDecisionResponse(
        id=decision.id,
        decision_reference=decision.decision_reference,
        version=decision.version,
        venue_id=decision.venue_id,
        venue_type=decision.venue_type,
        venue_name=decision.venue_name,
        booking_date=decision.booking_date,
        booking_time=decision.booking_time,
        duration_minutes=decision.duration_minutes,
        party_size=decision.party_size,
        guest_id=decision.guest_id,
        guest_tier=decision.guest_tier,
        base_price=decision.base_price,
        demand_adjustment=decision.demand_adjustment,
        seasonal_adjustment=decision.seasonal_adjustment,
        time_adjustment=decision.time_adjustment,
        loyalty_adjustment=decision.loyalty_adjustment,
        promotional_adjustment=decision.promotional_adjustment,
        ai_adjustment=decision.ai_adjustment,
        subtotal=decision.subtotal,
        tax_amount=decision.tax_amount,
        discount_amount=decision.discount_amount,
        total_price=decision.total_price,
        currency=decision.currency,
        source=decision.source,
        status=decision.status,
        ai_confidence=decision.ai_confidence,
        model_version=decision.model_version,
        applied_rules=decision.applied_rules,
        price_breakdown=decision.price_breakdown,
        valid_from=decision.valid_from,
        valid_until=decision.valid_until,
        calculation_time_ms=decision.calculation_time_ms,
        created_at=decision.created_at,
        served_at=decision.served_at,
        accepted_at=decision.accepted_at,
        booking_id=decision.booking_id,
        booking_reference=decision.booking_reference,
    )


