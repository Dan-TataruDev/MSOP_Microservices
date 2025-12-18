"""Service layer for dashboard and reporting operations."""
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from app.models.task import Task, TaskStatus, TaskType, TaskPriority
from app.models.maintenance import MaintenanceRequest, MaintenanceStatus, MaintenanceCategory
from app.models.staff import StaffMember
from app.schemas.dashboard import (
    DashboardSummary, TaskMetrics, MaintenanceMetrics,
    StaffWorkload, StaffWorkloadSummary, FloorSummary,
    TaskCountByStatus, TaskCountByType, MaintenanceCountByCategory,
    OperationalReport, RealTimeStatus, TaskTrendData, TrendReport
)

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Business logic for dashboard and reporting.
    
    Responsibilities:
    - Aggregate operational metrics
    - Generate real-time status
    - Create operational reports
    - Provide trend analysis
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_summary(self, target_date: Optional[date] = None) -> DashboardSummary:
        """
        Get comprehensive dashboard summary.
        
        Args:
            target_date: Date to generate summary for (defaults to today)
            
        Returns:
            DashboardSummary with all metrics
        """
        target_date = target_date or date.today()
        now = datetime.utcnow()
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = datetime.combine(target_date, datetime.max.time())
        
        return DashboardSummary(
            generated_at=now,
            date=target_date,
            task_metrics=self._get_task_metrics(day_start, day_end),
            maintenance_metrics=self._get_maintenance_metrics(day_start, day_end),
            staff_summary=self._get_staff_workload_summary(),
            floors_summary=self._get_floors_summary(day_start, day_end),
            upcoming_checkouts=self._count_upcoming_checkouts(),
            rooms_ready=self._count_rooms_ready(),
            rooms_pending_cleaning=self._count_rooms_pending_cleaning(),
            critical_alerts=self._get_critical_alerts()
        )
    
    def _get_task_metrics(self, day_start: datetime, day_end: datetime) -> TaskMetrics:
        """Calculate task metrics for the day."""
        now = datetime.utcnow()
        
        # Total tasks today
        total_today = self.db.query(func.count(Task.id)).filter(
            Task.scheduled_date >= day_start,
            Task.scheduled_date <= day_end
        ).scalar() or 0
        
        # Completed today
        completed_today = self.db.query(func.count(Task.id)).filter(
            Task.completed_at >= day_start,
            Task.completed_at <= day_end
        ).scalar() or 0
        
        # Pending tasks
        pending = self.db.query(func.count(Task.id)).filter(
            Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED])
        ).scalar() or 0
        
        # Overdue tasks
        overdue = self.db.query(func.count(Task.id)).filter(
            Task.due_date < now,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED, 
                           TaskStatus.IN_PROGRESS, TaskStatus.ON_HOLD])
        ).scalar() or 0
        
        # Delayed tasks
        delayed = self.db.query(func.count(Task.id)).filter(
            Task.is_delayed == True,
            Task.status != TaskStatus.COMPLETED
        ).scalar() or 0
        
        # Average completion time
        avg_duration = self.db.query(
            func.avg(
                func.extract('epoch', Task.completed_at - Task.started_at) / 60
            )
        ).filter(
            Task.completed_at.isnot(None),
            Task.started_at.isnot(None),
            Task.completed_at >= day_start
        ).scalar()
        
        # On-time completion rate
        completed_on_time = self.db.query(func.count(Task.id)).filter(
            Task.completed_at.isnot(None),
            Task.completed_at <= Task.due_date,
            Task.completed_at >= day_start
        ).scalar() or 0
        
        total_completed = self.db.query(func.count(Task.id)).filter(
            Task.completed_at.isnot(None),
            Task.completed_at >= day_start
        ).scalar() or 1  # Avoid division by zero
        
        on_time_rate = (completed_on_time / total_completed) * 100 if total_completed > 0 else 100.0
        
        # VIP tasks pending
        vip_pending = self.db.query(func.count(Task.id)).filter(
            Task.is_vip == True,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED])
        ).scalar() or 0
        
        return TaskMetrics(
            total_tasks_today=total_today,
            completed_tasks_today=completed_today,
            pending_tasks=pending,
            overdue_tasks=overdue,
            delayed_tasks=delayed,
            average_completion_time_minutes=avg_duration,
            on_time_completion_rate=on_time_rate,
            tasks_by_status=self._get_tasks_by_status(),
            tasks_by_type=self._get_tasks_by_type(day_start, day_end),
            vip_tasks_pending=vip_pending
        )
    
    def _get_tasks_by_status(self) -> TaskCountByStatus:
        """Get task counts grouped by status."""
        counts = self.db.query(
            Task.status,
            func.count(Task.id)
        ).group_by(Task.status).all()
        
        result = TaskCountByStatus()
        for status, count in counts:
            setattr(result, status.value, count)
        
        return result
    
    def _get_tasks_by_type(self, day_start: datetime, day_end: datetime) -> TaskCountByType:
        """Get task counts grouped by type."""
        counts = self.db.query(
            Task.task_type,
            func.count(Task.id)
        ).filter(
            Task.scheduled_date >= day_start,
            Task.scheduled_date <= day_end
        ).group_by(Task.task_type).all()
        
        result = TaskCountByType()
        for task_type, count in counts:
            attr_name = task_type.value
            if hasattr(result, attr_name):
                setattr(result, attr_name, count)
        
        return result
    
    def _get_maintenance_metrics(self, day_start: datetime, day_end: datetime) -> MaintenanceMetrics:
        """Calculate maintenance metrics."""
        now = datetime.utcnow()
        
        # Total requests today
        total_today = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.reported_at >= day_start,
            MaintenanceRequest.reported_at <= day_end
        ).scalar() or 0
        
        # Open requests
        open_requests = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.status.in_([
                MaintenanceStatus.REPORTED,
                MaintenanceStatus.TRIAGED,
                MaintenanceStatus.SCHEDULED,
                MaintenanceStatus.IN_PROGRESS,
                MaintenanceStatus.PARTS_ORDERED,
                MaintenanceStatus.ON_HOLD
            ])
        ).scalar() or 0
        
        # Critical requests
        critical = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.priority.in_([
                'emergency', 'urgent'
            ]),
            MaintenanceRequest.status.notin_([
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.VERIFIED,
                MaintenanceStatus.CLOSED
            ])
        ).scalar() or 0
        
        # Overdue requests
        overdue = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.sla_due_date < now,
            MaintenanceRequest.status.notin_([
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.VERIFIED,
                MaintenanceStatus.CLOSED,
                MaintenanceStatus.CANCELLED
            ])
        ).scalar() or 0
        
        # Average resolution time
        avg_resolution = self.db.query(
            func.avg(
                func.extract('epoch', MaintenanceRequest.work_completed_at - MaintenanceRequest.reported_at) / 60
            )
        ).filter(
            MaintenanceRequest.work_completed_at.isnot(None),
            MaintenanceRequest.work_completed_at >= day_start
        ).scalar()
        
        # SLA compliance rate
        completed_within_sla = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.work_completed_at.isnot(None),
            MaintenanceRequest.work_completed_at <= MaintenanceRequest.sla_due_date
        ).scalar() or 0
        
        total_completed_maintenance = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.work_completed_at.isnot(None)
        ).scalar() or 1
        
        sla_compliance = (completed_within_sla / total_completed_maintenance) * 100 if total_completed_maintenance > 0 else 100.0
        
        # Safety concerns open
        safety_open = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.safety_concern == True,
            MaintenanceRequest.status.notin_([
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.VERIFIED,
                MaintenanceStatus.CLOSED
            ])
        ).scalar() or 0
        
        return MaintenanceMetrics(
            total_requests_today=total_today,
            open_requests=open_requests,
            critical_requests=critical,
            overdue_requests=overdue,
            average_resolution_time_minutes=avg_resolution,
            sla_compliance_rate=sla_compliance,
            requests_by_category=self._get_maintenance_by_category(),
            safety_concerns_open=safety_open
        )
    
    def _get_maintenance_by_category(self) -> MaintenanceCountByCategory:
        """Get maintenance counts grouped by category."""
        counts = self.db.query(
            MaintenanceRequest.category,
            func.count(MaintenanceRequest.id)
        ).filter(
            MaintenanceRequest.status.notin_([
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.CLOSED,
                MaintenanceStatus.CANCELLED
            ])
        ).group_by(MaintenanceRequest.category).all()
        
        result = MaintenanceCountByCategory()
        for category, count in counts:
            attr_name = category.value
            if hasattr(result, attr_name):
                setattr(result, attr_name, count)
        
        return result
    
    def _get_staff_workload_summary(self) -> StaffWorkloadSummary:
        """Get staff workload summary."""
        # Get all active staff
        staff_members = self.db.query(StaffMember).filter(
            StaffMember.is_active == True
        ).all()
        
        on_duty = sum(1 for s in staff_members if s.is_on_duty)
        available = sum(1 for s in staff_members if s.is_available)
        
        workloads = []
        total_assigned = 0
        overloaded_count = 0
        
        for staff in staff_members:
            if not staff.is_on_duty:
                continue
            
            # Count assigned tasks
            assigned_count = self.db.query(func.count(Task.id)).filter(
                Task.assigned_staff_id == staff.id,
                Task.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
            ).scalar() or 0
            
            # Count completed today
            today_start = datetime.combine(date.today(), datetime.min.time())
            completed_today = self.db.query(func.count(Task.id)).filter(
                Task.assigned_staff_id == staff.id,
                Task.status == TaskStatus.COMPLETED,
                Task.completed_at >= today_start
            ).scalar() or 0
            
            # Get current in-progress task
            current_task = self.db.query(Task).filter(
                Task.assigned_staff_id == staff.id,
                Task.status == TaskStatus.IN_PROGRESS
            ).first()
            
            total_assigned += assigned_count
            if assigned_count > staff.max_tasks_per_shift:
                overloaded_count += 1
            
            workloads.append(StaffWorkload(
                staff_id=staff.id,
                staff_name=staff.full_name,
                role=staff.role.value,
                is_on_duty=staff.is_on_duty,
                assigned_tasks_count=assigned_count,
                completed_tasks_today=completed_today,
                in_progress_task_id=current_task.id if current_task else None,
                current_location=staff.current_location,
                efficiency_score=None  # Calculate based on historical data
            ))
        
        avg_tasks = total_assigned / on_duty if on_duty > 0 else 0
        
        return StaffWorkloadSummary(
            total_staff_on_duty=on_duty,
            total_staff_available=available,
            staff_workloads=workloads,
            average_tasks_per_staff=avg_tasks,
            overloaded_staff_count=overloaded_count
        )
    
    def _get_floors_summary(self, day_start: datetime, day_end: datetime) -> List[FloorSummary]:
        """Get task summary by floor."""
        # Get distinct floors
        floors = self.db.query(Task.floor_number).filter(
            Task.floor_number.isnot(None)
        ).distinct().all()
        
        summaries = []
        for (floor_num,) in floors:
            if floor_num is None:
                continue
            
            total = self.db.query(func.count(Task.id)).filter(
                Task.floor_number == floor_num,
                Task.scheduled_date >= day_start,
                Task.scheduled_date <= day_end
            ).scalar() or 0
            
            pending = self.db.query(func.count(Task.id)).filter(
                Task.floor_number == floor_num,
                Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED])
            ).scalar() or 0
            
            completed = self.db.query(func.count(Task.id)).filter(
                Task.floor_number == floor_num,
                Task.status == TaskStatus.COMPLETED,
                Task.completed_at >= day_start
            ).scalar() or 0
            
            cleaning_needed = self.db.query(func.count(Task.id)).filter(
                Task.floor_number == floor_num,
                Task.task_type.in_([
                    TaskType.CHECKOUT_CLEANING,
                    TaskType.STAY_OVER_CLEANING
                ]),
                Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED])
            ).scalar() or 0
            
            maintenance_issues = self.db.query(func.count(MaintenanceRequest.id)).filter(
                MaintenanceRequest.floor_number == floor_num,
                MaintenanceRequest.status.notin_([
                    MaintenanceStatus.COMPLETED,
                    MaintenanceStatus.CLOSED
                ])
            ).scalar() or 0
            
            summaries.append(FloorSummary(
                floor_number=floor_num,
                total_tasks=total,
                pending_tasks=pending,
                completed_tasks=completed,
                rooms_needing_cleaning=cleaning_needed,
                maintenance_issues=maintenance_issues
            ))
        
        return sorted(summaries, key=lambda x: x.floor_number)
    
    def _count_upcoming_checkouts(self) -> int:
        """Count upcoming checkouts (tasks scheduled)."""
        return self.db.query(func.count(Task.id)).filter(
            Task.task_type == TaskType.CHECKOUT_CLEANING,
            Task.status == TaskStatus.PENDING
        ).scalar() or 0
    
    def _count_rooms_ready(self) -> int:
        """Count rooms marked as ready (completed cleaning)."""
        today_start = datetime.combine(date.today(), datetime.min.time())
        return self.db.query(func.count(Task.id)).filter(
            Task.task_type.in_([
                TaskType.CHECKOUT_CLEANING,
                TaskType.STAY_OVER_CLEANING
            ]),
            Task.status.in_([TaskStatus.COMPLETED, TaskStatus.VERIFIED]),
            Task.completed_at >= today_start
        ).scalar() or 0
    
    def _count_rooms_pending_cleaning(self) -> int:
        """Count rooms pending cleaning."""
        return self.db.query(func.count(Task.id)).filter(
            Task.task_type.in_([
                TaskType.CHECKOUT_CLEANING,
                TaskType.STAY_OVER_CLEANING
            ]),
            Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
        ).scalar() or 0
    
    def _get_critical_alerts(self) -> List[str]:
        """Get list of critical alerts."""
        alerts = []
        now = datetime.utcnow()
        
        # Overdue VIP tasks
        overdue_vip = self.db.query(func.count(Task.id)).filter(
            Task.is_vip == True,
            Task.due_date < now,
            Task.status.notin_([TaskStatus.COMPLETED, TaskStatus.VERIFIED])
        ).scalar() or 0
        
        if overdue_vip > 0:
            alerts.append(f"⚠️ {overdue_vip} overdue VIP task(s)")
        
        # Safety concerns
        safety = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.safety_concern == True,
            MaintenanceRequest.status.notin_([
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.CLOSED
            ])
        ).scalar() or 0
        
        if safety > 0:
            alerts.append(f"🚨 {safety} open safety concern(s)")
        
        # Critical maintenance
        critical = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.priority == 'emergency',
            MaintenanceRequest.status.notin_([
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.CLOSED
            ])
        ).scalar() or 0
        
        if critical > 0:
            alerts.append(f"🔴 {critical} emergency maintenance request(s)")
        
        return alerts
    
    def get_real_time_status(self) -> RealTimeStatus:
        """Get real-time operational status for live dashboards."""
        now = datetime.utcnow()
        
        # Active tasks
        active_count = self.db.query(func.count(Task.id)).filter(
            Task.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
        ).scalar() or 0
        
        # Staff on duty
        staff_on_duty = self.db.query(func.count(StaffMember.id)).filter(
            StaffMember.is_on_duty == True,
            StaffMember.is_active == True
        ).scalar() or 0
        
        # Tasks in progress
        in_progress = self.db.query(Task).filter(
            Task.status == TaskStatus.IN_PROGRESS
        ).limit(10).all()
        
        tasks_in_progress = [{
            "task_reference": t.task_reference,
            "task_type": t.task_type.value,
            "location": t.location_name,
            "started_at": t.started_at.isoformat() if t.started_at else None
        } for t in in_progress]
        
        # Recent completions (last hour)
        one_hour_ago = now - timedelta(hours=1)
        recent = self.db.query(Task).filter(
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at >= one_hour_ago
        ).order_by(Task.completed_at.desc()).limit(5).all()
        
        recent_completions = [{
            "task_reference": t.task_reference,
            "task_type": t.task_type.value,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None
        } for t in recent]
        
        # Active alerts
        alerts = self._get_critical_alerts()
        alert_list = [{"message": a, "severity": "high"} for a in alerts]
        
        # Estimate backlog
        pending_minutes = self.db.query(
            func.sum(Task.estimated_duration_minutes)
        ).filter(
            Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED])
        ).scalar() or 0
        
        return RealTimeStatus(
            timestamp=now,
            active_tasks_count=active_count,
            staff_on_duty_count=staff_on_duty,
            tasks_in_progress=tasks_in_progress,
            recent_completions=recent_completions,
            alerts=alert_list,
            estimated_completion_backlog_minutes=pending_minutes
        )
    
    def get_operational_report(self, start_date: datetime, 
                              end_date: datetime) -> OperationalReport:
        """Generate detailed operational report for a period."""
        # Task statistics
        total_created = self.db.query(func.count(Task.id)).filter(
            Task.created_at >= start_date,
            Task.created_at <= end_date
        ).scalar() or 0
        
        total_completed = self.db.query(func.count(Task.id)).filter(
            Task.completed_at >= start_date,
            Task.completed_at <= end_date
        ).scalar() or 0
        
        total_cancelled = self.db.query(func.count(Task.id)).filter(
            Task.status == TaskStatus.CANCELLED,
            Task.updated_at >= start_date,
            Task.updated_at <= end_date
        ).scalar() or 0
        
        # Average duration
        avg_duration = self.db.query(
            func.avg(
                func.extract('epoch', Task.completed_at - Task.started_at) / 60
            )
        ).filter(
            Task.completed_at >= start_date,
            Task.completed_at <= end_date,
            Task.started_at.isnot(None)
        ).scalar() or 0
        
        # On-time rate
        on_time = self.db.query(func.count(Task.id)).filter(
            Task.completed_at >= start_date,
            Task.completed_at <= end_date,
            Task.completed_at <= Task.due_date
        ).scalar() or 0
        
        on_time_rate = (on_time / total_completed * 100) if total_completed > 0 else 100.0
        
        # Tasks by type
        type_counts = self.db.query(
            Task.task_type,
            func.count(Task.id)
        ).filter(
            Task.created_at >= start_date,
            Task.created_at <= end_date
        ).group_by(Task.task_type).all()
        
        tasks_by_type = {t.value: c for t, c in type_counts}
        
        # Tasks by priority
        priority_counts = self.db.query(
            Task.priority,
            func.count(Task.id)
        ).filter(
            Task.created_at >= start_date,
            Task.created_at <= end_date
        ).group_by(Task.priority).all()
        
        tasks_by_priority = {p.value: c for p, c in priority_counts}
        
        # Tasks by floor
        floor_counts = self.db.query(
            Task.floor_number,
            func.count(Task.id)
        ).filter(
            Task.created_at >= start_date,
            Task.created_at <= end_date,
            Task.floor_number.isnot(None)
        ).group_by(Task.floor_number).all()
        
        tasks_by_floor = {f: c for f, c in floor_counts if f is not None}
        
        # Maintenance statistics
        maintenance_total = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.reported_at >= start_date,
            MaintenanceRequest.reported_at <= end_date
        ).scalar() or 0
        
        maintenance_completed = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.work_completed_at >= start_date,
            MaintenanceRequest.work_completed_at <= end_date
        ).scalar() or 0
        
        maintenance_pending = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.status.notin_([
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.CLOSED,
                MaintenanceStatus.CANCELLED
            ])
        ).scalar() or 0
        
        # Average resolution time
        avg_resolution = self.db.query(
            func.avg(
                func.extract('epoch', 
                    MaintenanceRequest.work_completed_at - MaintenanceRequest.reported_at
                ) / 3600
            )
        ).filter(
            MaintenanceRequest.work_completed_at >= start_date,
            MaintenanceRequest.work_completed_at <= end_date
        ).scalar() or 0
        
        # Maintenance SLA compliance
        within_sla = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.work_completed_at >= start_date,
            MaintenanceRequest.work_completed_at <= end_date,
            MaintenanceRequest.work_completed_at <= MaintenanceRequest.sla_due_date
        ).scalar() or 0
        
        maint_sla_rate = (within_sla / maintenance_completed * 100) if maintenance_completed > 0 else 100.0
        
        # Maintenance by category
        cat_counts = self.db.query(
            MaintenanceRequest.category,
            func.count(MaintenanceRequest.id)
        ).filter(
            MaintenanceRequest.reported_at >= start_date,
            MaintenanceRequest.reported_at <= end_date
        ).group_by(MaintenanceRequest.category).all()
        
        maintenance_by_category = {c.value: cnt for c, cnt in cat_counts}
        
        # Maintenance by priority
        maint_priority_counts = self.db.query(
            MaintenanceRequest.priority,
            func.count(MaintenanceRequest.id)
        ).filter(
            MaintenanceRequest.reported_at >= start_date,
            MaintenanceRequest.reported_at <= end_date
        ).group_by(MaintenanceRequest.priority).all()
        
        maintenance_by_priority = {p.value: c for p, c in maint_priority_counts}
        
        return OperationalReport(
            report_period_start=start_date,
            report_period_end=end_date,
            generated_at=datetime.utcnow(),
            total_tasks_created=total_created,
            total_tasks_completed=total_completed,
            total_tasks_cancelled=total_cancelled,
            average_task_duration_minutes=float(avg_duration),
            on_time_completion_rate=on_time_rate,
            tasks_by_type=tasks_by_type,
            tasks_by_priority=tasks_by_priority,
            tasks_by_floor=tasks_by_floor,
            total_maintenance_requests=maintenance_total,
            maintenance_completed=maintenance_completed,
            maintenance_pending=maintenance_pending,
            average_resolution_time_hours=float(avg_resolution),
            sla_compliance_rate=maint_sla_rate,
            maintenance_by_category=maintenance_by_category,
            maintenance_by_priority=maintenance_by_priority,
            top_performers=[],
            staff_efficiency_average=0.0,
            recurring_maintenance_issues=[],
            frequently_delayed_task_types=[],
            recommendations=[]
        )
