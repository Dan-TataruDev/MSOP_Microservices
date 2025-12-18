"""Service layer for maintenance request operations."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.maintenance import (
    MaintenanceRequest, MaintenanceCategory, 
    MaintenanceStatus, MaintenancePriority
)
from app.models.task import Task, TaskType, TaskStatus, TaskPriority
from app.schemas.maintenance import (
    MaintenanceRequestCreate, MaintenanceRequestUpdate,
    MaintenanceTriageRequest, MaintenanceCompletionRequest,
    MaintenanceFilter
)
from app.events.publisher import event_publisher
from app.utils.task_reference import generate_maintenance_reference, generate_task_reference
from app.config import settings

logger = logging.getLogger(__name__)


class MaintenanceService:
    """
    Business logic for maintenance request management.
    
    Responsibilities:
    - Create and track maintenance requests
    - Handle triage and assignment
    - Manage maintenance lifecycle
    - Generate maintenance tasks
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_request(self, request_data: MaintenanceRequestCreate) -> MaintenanceRequest:
        """
        Create a new maintenance request.
        
        Args:
            request_data: Request creation data
            
        Returns:
            Created MaintenanceRequest instance
        """
        # Calculate SLA based on priority
        sla_map = {
            MaintenancePriority.EMERGENCY: settings.critical_maintenance_sla,
            MaintenancePriority.URGENT: settings.critical_maintenance_sla * 2,
            MaintenancePriority.HIGH: settings.maintenance_response_sla,
            MaintenancePriority.NORMAL: settings.maintenance_response_sla * 2,
            MaintenancePriority.LOW: settings.maintenance_response_sla * 4,
        }
        sla_minutes = sla_map.get(request_data.priority, settings.maintenance_response_sla)
        
        request = MaintenanceRequest(
            request_reference=generate_maintenance_reference(),
            category=request_data.category,
            status=MaintenanceStatus.REPORTED,
            priority=request_data.priority,
            venue_id=request_data.venue_id,
            venue_type=request_data.venue_type,
            location_name=request_data.location_name,
            floor_number=request_data.floor_number,
            specific_location=request_data.specific_location,
            title=request_data.title,
            description=request_data.description,
            affects_room_availability=request_data.affects_room_availability,
            guest_impact_level=request_data.guest_impact_level,
            safety_concern=request_data.safety_concern,
            reported_by_staff_id=request_data.reported_by_staff_id,
            reported_by_guest_id=request_data.reported_by_guest_id,
            source_event_type=request_data.source_event_type,
            source_task_id=request_data.source_task_id,
            sla_due_date=datetime.utcnow() + timedelta(minutes=sla_minutes),
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        # Publish event
        event_publisher.publish_maintenance_reported({
            "id": request.id,
            "request_reference": request.request_reference,
            "category": request.category.value,
            "priority": request.priority.value,
            "venue_id": request.venue_id,
            "affects_availability": request.affects_room_availability,
            "safety_concern": request.safety_concern,
            "title": request.title,
        })
        
        # If safety concern or emergency, publish critical alert
        if request.safety_concern or request.priority == MaintenancePriority.EMERGENCY:
            event_publisher.publish_critical_alert(
                alert_type="maintenance_emergency",
                message=f"Emergency maintenance: {request.title}",
                venue_id=request.venue_id,
                requires_immediate_action=True
            )
        
        logger.info(f"Created maintenance request: {request.request_reference}")
        return request
    
    def get_request(self, request_id: UUID) -> Optional[MaintenanceRequest]:
        """Get maintenance request by ID."""
        return self.db.query(MaintenanceRequest).filter(
            MaintenanceRequest.id == request_id
        ).first()
    
    def get_request_by_reference(self, reference: str) -> Optional[MaintenanceRequest]:
        """Get maintenance request by reference number."""
        return self.db.query(MaintenanceRequest).filter(
            MaintenanceRequest.request_reference == reference
        ).first()
    
    def update_request(self, request_id: UUID, 
                      update_data: MaintenanceRequestUpdate) -> Optional[MaintenanceRequest]:
        """
        Update maintenance request details.
        
        Args:
            request_id: Request ID
            update_data: Fields to update
            
        Returns:
            Updated MaintenanceRequest or None
        """
        request = self.get_request(request_id)
        if not request:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(request, key, value)
        
        request.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(request)
        
        return request
    
    def triage_request(self, request_id: UUID, 
                      triage_data: MaintenanceTriageRequest) -> Optional[MaintenanceRequest]:
        """
        Triage a reported maintenance request.
        
        Args:
            request_id: Request ID
            triage_data: Triage information
            
        Returns:
            Updated MaintenanceRequest or None
        """
        request = self.get_request(request_id)
        if not request:
            return None
        
        if request.status != MaintenanceStatus.REPORTED:
            logger.warning(f"Cannot triage request {request.request_reference} not in REPORTED status")
            return None
        
        request.status = MaintenanceStatus.TRIAGED
        request.triaged_at = datetime.utcnow()
        request.priority = triage_data.priority
        request.assigned_to_staff_id = triage_data.assigned_to_staff_id
        request.assigned_to_vendor = triage_data.assigned_to_vendor
        request.scheduled_for = triage_data.scheduled_for
        request.estimated_cost = triage_data.estimated_cost
        
        # Recalculate SLA based on new priority
        sla_map = {
            MaintenancePriority.EMERGENCY: settings.critical_maintenance_sla,
            MaintenancePriority.URGENT: settings.critical_maintenance_sla * 2,
            MaintenancePriority.HIGH: settings.maintenance_response_sla,
            MaintenancePriority.NORMAL: settings.maintenance_response_sla * 2,
            MaintenancePriority.LOW: settings.maintenance_response_sla * 4,
        }
        sla_minutes = sla_map.get(triage_data.priority, settings.maintenance_response_sla)
        request.sla_due_date = datetime.utcnow() + timedelta(minutes=sla_minutes)
        
        self.db.commit()
        self.db.refresh(request)
        
        # If assigned, update status to scheduled
        if request.assigned_to_staff_id or request.assigned_to_vendor:
            request.status = MaintenanceStatus.SCHEDULED
            self.db.commit()
            
            # Create maintenance task
            self._create_maintenance_task(request)
        
        logger.info(f"Triaged maintenance request: {request.request_reference}")
        return request
    
    def start_work(self, request_id: UUID) -> Optional[MaintenanceRequest]:
        """
        Mark maintenance work as started.
        
        Args:
            request_id: Request ID
            
        Returns:
            Updated MaintenanceRequest or None
        """
        request = self.get_request(request_id)
        if not request:
            return None
        
        if request.status not in [MaintenanceStatus.TRIAGED, MaintenanceStatus.SCHEDULED]:
            logger.warning(f"Cannot start work on request {request.request_reference}")
            return None
        
        request.status = MaintenanceStatus.IN_PROGRESS
        request.work_started_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(request)
        
        logger.info(f"Started maintenance work: {request.request_reference}")
        return request
    
    def complete_request(self, request_id: UUID, 
                        completion_data: MaintenanceCompletionRequest) -> Optional[MaintenanceRequest]:
        """
        Mark maintenance request as completed.
        
        Args:
            request_id: Request ID
            completion_data: Completion details
            
        Returns:
            Updated MaintenanceRequest or None
        """
        request = self.get_request(request_id)
        if not request:
            return None
        
        if request.status != MaintenanceStatus.IN_PROGRESS:
            logger.warning(f"Cannot complete request {request.request_reference} not in progress")
            return None
        
        request.status = MaintenanceStatus.COMPLETED
        request.work_completed_at = datetime.utcnow()
        request.resolution_notes = completion_data.resolution_notes
        request.root_cause = completion_data.root_cause
        request.preventive_action = completion_data.preventive_action
        request.actual_cost = completion_data.actual_cost
        request.requires_followup = completion_data.requires_followup
        request.followup_date = completion_data.followup_date
        
        self.db.commit()
        self.db.refresh(request)
        
        # Publish completion event
        resolution_time = request.resolution_time_minutes or 0
        event_publisher.publish_maintenance_resolved(
            request_id=request.id,
            request_reference=request.request_reference,
            venue_id=request.venue_id,
            resolution_time_minutes=resolution_time
        )
        
        # Complete related tasks
        related_tasks = self.db.query(Task).filter(
            Task.source_maintenance_id == request_id,
            Task.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
        ).all()
        
        for task in related_tasks:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.completion_notes = completion_data.resolution_notes
        
        self.db.commit()
        
        logger.info(f"Completed maintenance request: {request.request_reference}")
        return request
    
    def escalate_request(self, request_id: UUID, 
                        reason: str) -> Optional[MaintenanceRequest]:
        """
        Escalate a maintenance request to higher priority.
        
        Args:
            request_id: Request ID
            reason: Escalation reason
            
        Returns:
            Updated MaintenanceRequest or None
        """
        request = self.get_request(request_id)
        if not request:
            return None
        
        # Escalate priority
        priority_order = [
            MaintenancePriority.LOW,
            MaintenancePriority.NORMAL,
            MaintenancePriority.HIGH,
            MaintenancePriority.URGENT,
            MaintenancePriority.EMERGENCY
        ]
        
        current_index = priority_order.index(request.priority)
        if current_index < len(priority_order) - 1:
            new_priority = priority_order[current_index + 1]
            request.priority = new_priority
            
            # Update SLA
            sla_map = {
                MaintenancePriority.EMERGENCY: settings.critical_maintenance_sla,
                MaintenancePriority.URGENT: settings.critical_maintenance_sla * 2,
                MaintenancePriority.HIGH: settings.maintenance_response_sla,
            }
            if new_priority in sla_map:
                request.sla_due_date = datetime.utcnow() + timedelta(
                    minutes=sla_map[new_priority]
                )
            
            self.db.commit()
            self.db.refresh(request)
            
            # Publish escalation event
            event_publisher.publish_maintenance_escalated(
                request_id=request.id,
                request_reference=request.request_reference,
                escalation_reason=reason,
                new_priority=new_priority.value
            )
            
            logger.warning(f"Escalated maintenance request: {request.request_reference} to {new_priority.value}")
        
        return request
    
    def list_requests(
        self,
        filters: Optional[MaintenanceFilter] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[MaintenanceRequest], int]:
        """
        List maintenance requests with filtering and pagination.
        
        Args:
            filters: Filter criteria
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (requests list, total count)
        """
        query = self.db.query(MaintenanceRequest)
        
        if filters:
            if filters.categories:
                query = query.filter(MaintenanceRequest.category.in_(filters.categories))
            if filters.statuses:
                query = query.filter(MaintenanceRequest.status.in_(filters.statuses))
            if filters.priorities:
                query = query.filter(MaintenanceRequest.priority.in_(filters.priorities))
            if filters.venue_id:
                query = query.filter(MaintenanceRequest.venue_id == filters.venue_id)
            if filters.floor_number is not None:
                query = query.filter(MaintenanceRequest.floor_number == filters.floor_number)
            if filters.assigned_to_staff_id:
                query = query.filter(
                    MaintenanceRequest.assigned_to_staff_id == filters.assigned_to_staff_id
                )
            if filters.safety_concern is not None:
                query = query.filter(MaintenanceRequest.safety_concern == filters.safety_concern)
            if filters.affects_room_availability is not None:
                query = query.filter(
                    MaintenanceRequest.affects_room_availability == filters.affects_room_availability
                )
            if filters.reported_from:
                query = query.filter(MaintenanceRequest.reported_at >= filters.reported_from)
            if filters.reported_to:
                query = query.filter(MaintenanceRequest.reported_at <= filters.reported_to)
        
        total = query.count()
        
        offset = (page - 1) * page_size
        requests = query.order_by(
            MaintenanceRequest.priority.desc(),
            MaintenanceRequest.reported_at.asc()
        ).offset(offset).limit(page_size).all()
        
        return requests, total
    
    def get_overdue_requests(self) -> List[MaintenanceRequest]:
        """Get all overdue maintenance requests."""
        now = datetime.utcnow()
        return self.db.query(MaintenanceRequest).filter(
            MaintenanceRequest.sla_due_date < now,
            MaintenanceRequest.status.in_([
                MaintenanceStatus.REPORTED,
                MaintenanceStatus.TRIAGED,
                MaintenanceStatus.SCHEDULED,
                MaintenanceStatus.IN_PROGRESS
            ])
        ).all()
    
    def _create_maintenance_task(self, request: MaintenanceRequest) -> Task:
        """Create a maintenance task from a request."""
        # Map maintenance priority to task priority
        priority_map = {
            MaintenancePriority.EMERGENCY: TaskPriority.CRITICAL,
            MaintenancePriority.URGENT: TaskPriority.URGENT,
            MaintenancePriority.HIGH: TaskPriority.HIGH,
            MaintenancePriority.NORMAL: TaskPriority.NORMAL,
            MaintenancePriority.LOW: TaskPriority.LOW,
        }
        
        task = Task(
            task_reference=generate_task_reference("MNT"),
            task_type=TaskType.MAINTENANCE_REPAIR,
            status=TaskStatus.ASSIGNED if request.assigned_to_staff_id else TaskStatus.PENDING,
            priority=priority_map.get(request.priority, TaskPriority.NORMAL),
            venue_id=request.venue_id,
            venue_type=request.venue_type,
            location_name=request.location_name,
            floor_number=request.floor_number,
            source_maintenance_id=request.id,
            assigned_staff_id=request.assigned_to_staff_id,
            assigned_at=datetime.utcnow() if request.assigned_to_staff_id else None,
            title=f"Maintenance: {request.title}",
            description=request.description,
            special_instructions=f"Category: {request.category.value}\nLocation: {request.specific_location or 'N/A'}",
            scheduled_date=request.scheduled_for or datetime.utcnow(),
            due_date=request.sla_due_date,
            estimated_duration_minutes=settings.default_maintenance_duration_minutes,
        )
        
        self.db.add(task)
        self.db.commit()
        
        logger.info(f"Created maintenance task {task.task_reference} for request {request.request_reference}")
        return task
