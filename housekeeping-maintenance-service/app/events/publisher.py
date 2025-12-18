"""
Event publisher for task completion and operational events.

This service publishes events for downstream consumers:
- Analytics service: task metrics and trends
- Booking service: room ready notifications
- Inventory service: restocking completion
- Notification service: alerts and updates
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from app.config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Publishes housekeeping and maintenance events.
    
    Published Events:
    - task.created: New task generated
    - task.assigned: Task assigned to staff
    - task.started: Task execution started
    - task.completed: Task finished successfully
    - task.delayed: Task is running behind schedule
    - task.verified: Task completion verified
    - room.ready: Room is ready for check-in
    - room.cleaning_started: Room cleaning in progress
    - maintenance.reported: New maintenance issue
    - maintenance.resolved: Issue fixed
    - maintenance.escalated: Issue escalated
    - alert.sla_breach: SLA threshold exceeded
    
    Integration Notes:
    - Events are published to RabbitMQ topic exchange
    - Routing keys follow pattern: housekeeping.{entity}.{action}
    - Consumers subscribe based on their needs
    """
    
    def __init__(self):
        self.exchange = settings.rabbitmq_exchange
        self.source = "housekeeping-maintenance-service"
        logger.info(f"EventPublisher initialized with exchange: {self.exchange}")
    
    def _serialize_payload(self, payload: Dict[str, Any]) -> str:
        """Serialize payload handling UUIDs and datetimes."""
        def default_serializer(obj):
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        return json.dumps(payload, default=default_serializer)
    
    def _publish(self, topic: str, event_type: str, payload: Dict[str, Any],
                correlation_id: Optional[str] = None) -> None:
        """
        Internal method to publish events to message broker.
        
        Args:
            topic: Event topic/routing key
            event_type: Type of event
            payload: Event data
            correlation_id: Optional ID to correlate related events
        """
        event = {
            "event_id": str(UUID(int=int(datetime.utcnow().timestamp() * 1000000))),
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "source": self.source,
            "version": "1.0",
            "correlation_id": correlation_id,
        }
        
        logger.info(f"Publishing event: {event_type} to topic: {topic}")
        logger.debug(f"Event payload: {self._serialize_payload(event)}")
        
        # TODO: Implement actual RabbitMQ publishing
        # In production:
        # channel = self.connection.channel()
        # channel.basic_publish(
        #     exchange=self.exchange,
        #     routing_key=f"{settings.event_topic_housekeeping}.{topic}",
        #     body=self._serialize_payload(event),
        #     properties=pika.BasicProperties(
        #         delivery_mode=2,  # Persistent
        #         content_type='application/json',
        #         correlation_id=correlation_id
        #     )
        # )
    
    # ==================== Task Events ====================
    
    def publish_task_created(self, task_data: Dict[str, Any]) -> None:
        """Emit event when a new task is created."""
        self._publish(
            topic="task.created",
            event_type="housekeeping.task.created",
            payload={
                "task_id": task_data.get("id"),
                "task_reference": task_data.get("task_reference"),
                "task_type": task_data.get("task_type"),
                "priority": task_data.get("priority"),
                "venue_id": task_data.get("venue_id"),
                "venue_type": task_data.get("venue_type"),
                "scheduled_date": task_data.get("scheduled_date"),
                "due_date": task_data.get("due_date"),
                "source_event": task_data.get("source_event_type"),
                "is_vip": task_data.get("is_vip", False),
            }
        )
    
    def publish_task_assigned(self, task_id: UUID, task_reference: str,
                             staff_id: UUID, staff_name: str) -> None:
        """Emit event when task is assigned to staff."""
        self._publish(
            topic="task.assigned",
            event_type="housekeeping.task.assigned",
            payload={
                "task_id": str(task_id),
                "task_reference": task_reference,
                "assigned_to_staff_id": str(staff_id),
                "assigned_to_staff_name": staff_name,
                "assigned_at": datetime.utcnow().isoformat(),
            }
        )
    
    def publish_task_started(self, task_id: UUID, task_reference: str,
                            venue_id: Optional[UUID] = None) -> None:
        """Emit event when task execution begins."""
        self._publish(
            topic="task.started",
            event_type="housekeeping.task.started",
            payload={
                "task_id": str(task_id),
                "task_reference": task_reference,
                "venue_id": str(venue_id) if venue_id else None,
                "started_at": datetime.utcnow().isoformat(),
            }
        )
    
    def publish_task_completed(self, task_id: UUID, task_reference: str,
                              task_type: str, venue_id: Optional[UUID],
                              duration_minutes: int,
                              issues_found: Optional[str] = None) -> None:
        """
        Emit event when task is completed.
        
        This is a critical event consumed by:
        - Booking service: To mark room as ready
        - Analytics: For performance tracking
        - Inventory: If restocking task, update counts
        """
        self._publish(
            topic="task.completed",
            event_type="housekeeping.task.completed",
            payload={
                "task_id": str(task_id),
                "task_reference": task_reference,
                "task_type": task_type,
                "venue_id": str(venue_id) if venue_id else None,
                "completed_at": datetime.utcnow().isoformat(),
                "duration_minutes": duration_minutes,
                "issues_found": issues_found,
                "on_time": True,  # Calculate based on due_date
            },
            correlation_id=task_reference
        )
    
    def publish_task_delayed(self, task_id: UUID, task_reference: str,
                            task_type: str, venue_id: Optional[UUID],
                            delay_reason: str, new_estimated_completion: datetime) -> None:
        """
        Emit event when task is delayed beyond SLA.
        
        Consumed by:
        - Notification service: Alert supervisors
        - Booking service: Update room availability ETA
        - Analytics: Track delay patterns
        """
        self._publish(
            topic="task.delayed",
            event_type="housekeeping.task.delayed",
            payload={
                "task_id": str(task_id),
                "task_reference": task_reference,
                "task_type": task_type,
                "venue_id": str(venue_id) if venue_id else None,
                "delay_reason": delay_reason,
                "delayed_at": datetime.utcnow().isoformat(),
                "new_estimated_completion": new_estimated_completion.isoformat(),
            },
            correlation_id=task_reference
        )
    
    def publish_task_verified(self, task_id: UUID, task_reference: str,
                             verified_by: UUID, quality_score: Optional[int] = None) -> None:
        """Emit event when task completion is verified by supervisor."""
        self._publish(
            topic="task.verified",
            event_type="housekeeping.task.verified",
            payload={
                "task_id": str(task_id),
                "task_reference": task_reference,
                "verified_by": str(verified_by),
                "verified_at": datetime.utcnow().isoformat(),
                "quality_score": quality_score,
            }
        )
    
    # ==================== Room Status Events ====================
    
    def publish_room_ready(self, venue_id: UUID, room_number: str,
                          booking_reference: Optional[str] = None) -> None:
        """
        Emit event when room is ready for check-in.
        
        This is the key integration point with the booking service.
        The booking service consumes this to update room availability.
        """
        self._publish(
            topic="room.ready",
            event_type="housekeeping.room.ready",
            payload={
                "venue_id": str(venue_id),
                "room_number": room_number,
                "ready_at": datetime.utcnow().isoformat(),
                "booking_reference": booking_reference,
            },
            correlation_id=booking_reference
        )
    
    def publish_room_cleaning_started(self, venue_id: UUID, room_number: str,
                                     estimated_completion_minutes: int) -> None:
        """Emit event when room cleaning begins."""
        self._publish(
            topic="room.cleaning_started",
            event_type="housekeeping.room.cleaning_started",
            payload={
                "venue_id": str(venue_id),
                "room_number": room_number,
                "started_at": datetime.utcnow().isoformat(),
                "estimated_completion_minutes": estimated_completion_minutes,
            }
        )
    
    # ==================== Maintenance Events ====================
    
    def publish_maintenance_reported(self, request_data: Dict[str, Any]) -> None:
        """Emit event when new maintenance issue is reported."""
        self._publish(
            topic="maintenance.reported",
            event_type="housekeeping.maintenance.reported",
            payload={
                "request_id": request_data.get("id"),
                "request_reference": request_data.get("request_reference"),
                "category": request_data.get("category"),
                "priority": request_data.get("priority"),
                "venue_id": request_data.get("venue_id"),
                "affects_availability": request_data.get("affects_room_availability"),
                "safety_concern": request_data.get("safety_concern"),
                "title": request_data.get("title"),
            }
        )
    
    def publish_maintenance_resolved(self, request_id: UUID, request_reference: str,
                                    venue_id: Optional[UUID],
                                    resolution_time_minutes: int) -> None:
        """
        Emit event when maintenance issue is resolved.
        
        Consumed by:
        - Inventory service: Update room status to available
        - Booking service: Room can be booked again
        - Analytics: Track resolution metrics
        """
        self._publish(
            topic="maintenance.resolved",
            event_type="housekeeping.maintenance.resolved",
            payload={
                "request_id": str(request_id),
                "request_reference": request_reference,
                "venue_id": str(venue_id) if venue_id else None,
                "resolved_at": datetime.utcnow().isoformat(),
                "resolution_time_minutes": resolution_time_minutes,
            },
            correlation_id=request_reference
        )
    
    def publish_maintenance_escalated(self, request_id: UUID, request_reference: str,
                                     escalation_reason: str, new_priority: str) -> None:
        """Emit event when maintenance issue is escalated."""
        self._publish(
            topic="maintenance.escalated",
            event_type="housekeeping.maintenance.escalated",
            payload={
                "request_id": str(request_id),
                "request_reference": request_reference,
                "escalation_reason": escalation_reason,
                "new_priority": new_priority,
                "escalated_at": datetime.utcnow().isoformat(),
            }
        )
    
    # ==================== Alert Events ====================
    
    def publish_sla_breach_alert(self, entity_type: str, entity_id: UUID,
                                entity_reference: str, sla_type: str,
                                breach_minutes: int) -> None:
        """
        Emit alert when SLA threshold is exceeded.
        
        Consumed by:
        - Notification service: Alert management
        - Analytics: Track SLA compliance
        """
        self._publish(
            topic="alert.sla_breach",
            event_type="housekeeping.alert.sla_breach",
            payload={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "entity_reference": entity_reference,
                "sla_type": sla_type,
                "breach_minutes": breach_minutes,
                "breached_at": datetime.utcnow().isoformat(),
            }
        )
    
    def publish_critical_alert(self, alert_type: str, message: str,
                              venue_id: Optional[UUID] = None,
                              requires_immediate_action: bool = True) -> None:
        """Emit critical operational alert."""
        self._publish(
            topic="alert.critical",
            event_type="housekeeping.alert.critical",
            payload={
                "alert_type": alert_type,
                "message": message,
                "venue_id": str(venue_id) if venue_id else None,
                "requires_immediate_action": requires_immediate_action,
                "created_at": datetime.utcnow().isoformat(),
            }
        )


# Global publisher instance
event_publisher = EventPublisher()
