"""Workload balancing utilities for task assignment."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.task import Task, TaskStatus, TaskType
from app.models.staff import StaffMember, StaffRole


class WorkloadBalancer:
    """
    Intelligent workload balancing for task assignment.
    
    Assignment Strategy:
    1. Filter by availability and skills
    2. Consider current workload
    3. Factor in proximity (floor assignment)
    4. Account for VIP handling capability
    5. Balance for efficiency
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_available_staff(
        self,
        department: str = "housekeeping",
        required_skills: Optional[List[str]] = None,
        floor_number: Optional[int] = None,
        requires_vip_capability: bool = False
    ) -> List[StaffMember]:
        """
        Get list of available staff members filtered by criteria.
        
        Args:
            department: Department to filter by
            required_skills: Skills needed for the task
            floor_number: Preferred floor for proximity
            requires_vip_capability: Whether task requires VIP handling
            
        Returns:
            List of available staff members
        """
        query = self.db.query(StaffMember).filter(
            StaffMember.is_active == True,
            StaffMember.is_on_duty == True,
            StaffMember.department == department
        )
        
        if requires_vip_capability:
            query = query.filter(StaffMember.can_handle_vip == True)
        
        staff_list = query.all()
        
        # Filter by skills if required
        if required_skills:
            staff_list = [
                s for s in staff_list
                if s.skills and any(skill.lower() in [sk.lower() for sk in s.skills] 
                                   for skill in required_skills)
            ]
        
        # Sort by floor proximity if specified
        if floor_number is not None:
            staff_list.sort(
                key=lambda s: self._floor_distance(s.preferred_floors, floor_number)
            )
        
        return staff_list
    
    def _floor_distance(self, preferred_floors: Optional[List[int]], target_floor: int) -> int:
        """Calculate proximity score based on floor assignment."""
        if not preferred_floors:
            return 100  # No preference, lower priority
        
        if target_floor in preferred_floors:
            return 0  # Perfect match
        
        # Return minimum distance to any preferred floor
        return min(abs(target_floor - f) for f in preferred_floors)
    
    def get_staff_workload(self, staff_id: UUID) -> Dict[str, Any]:
        """
        Get current workload metrics for a staff member.
        
        Returns:
            Dictionary with workload metrics
        """
        # Count active tasks
        active_tasks = self.db.query(func.count(Task.id)).filter(
            Task.assigned_staff_id == staff_id,
            Task.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
        ).scalar()
        
        # Count completed today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today = self.db.query(func.count(Task.id)).filter(
            Task.assigned_staff_id == staff_id,
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at >= today_start
        ).scalar()
        
        # Get staff details
        staff = self.db.query(StaffMember).filter(StaffMember.id == staff_id).first()
        
        return {
            "staff_id": staff_id,
            "active_tasks": active_tasks,
            "completed_today": completed_today,
            "max_tasks": staff.max_tasks_per_shift if staff else 15,
            "availability_score": self._calculate_availability_score(
                active_tasks, 
                staff.max_tasks_per_shift if staff else 15
            )
        }
    
    def _calculate_availability_score(self, current_tasks: int, max_tasks: int) -> float:
        """Calculate availability score (0-1, higher is more available)."""
        if max_tasks == 0:
            return 0.0
        return max(0.0, 1.0 - (current_tasks / max_tasks))
    
    def find_best_assignee(
        self,
        task_type: TaskType,
        floor_number: Optional[int] = None,
        is_vip: bool = False,
        required_skills: Optional[List[str]] = None
    ) -> Optional[StaffMember]:
        """
        Find the best staff member to assign a task to.
        
        Algorithm:
        1. Get available staff matching criteria
        2. Calculate composite score for each
        3. Return highest scoring candidate
        
        Args:
            task_type: Type of task
            floor_number: Floor where task is located
            is_vip: Whether this is a VIP task
            required_skills: Skills needed for the task
            
        Returns:
            Best candidate StaffMember or None
        """
        # Determine department based on task type
        department = "maintenance" if task_type in [
            TaskType.MAINTENANCE_REPAIR, 
            TaskType.PREVENTIVE_MAINTENANCE
        ] else "housekeeping"
        
        # Get available staff
        candidates = self.get_available_staff(
            department=department,
            required_skills=required_skills,
            floor_number=floor_number,
            requires_vip_capability=is_vip
        )
        
        if not candidates:
            return None
        
        # Score each candidate
        scored_candidates = []
        for staff in candidates:
            workload = self.get_staff_workload(staff.id)
            
            # Composite score calculation
            score = 0.0
            
            # Availability weight (40%)
            score += workload["availability_score"] * 0.4
            
            # Floor proximity weight (30%)
            floor_distance = self._floor_distance(staff.preferred_floors, floor_number) if floor_number else 0
            proximity_score = max(0, 1 - (floor_distance / 10))
            score += proximity_score * 0.3
            
            # Experience/rating weight (20%)
            if staff.quality_rating:
                score += (staff.quality_rating / 5) * 0.2
            else:
                score += 0.6 * 0.2  # Default rating
            
            # VIP capability bonus (10%)
            if is_vip and staff.can_handle_vip:
                score += 0.1
            
            scored_candidates.append((staff, score))
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return scored_candidates[0][0] if scored_candidates else None
    
    def auto_assign_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Automatically assign pending tasks to available staff.
        
        Returns:
            List of assignment results
        """
        # Get pending tasks ordered by priority and due date
        pending_tasks = self.db.query(Task).filter(
            Task.status == TaskStatus.PENDING,
            Task.assigned_staff_id.is_(None)
        ).order_by(
            Task.priority.desc(),
            Task.due_date.asc()
        ).limit(limit).all()
        
        assignments = []
        
        for task in pending_tasks:
            # Determine required skills based on task type
            skills_map = {
                TaskType.MAINTENANCE_REPAIR: ["general_maintenance"],
                TaskType.PREVENTIVE_MAINTENANCE: ["preventive_maintenance"],
            }
            required_skills = skills_map.get(task.task_type)
            
            # Find best assignee
            assignee = self.find_best_assignee(
                task_type=task.task_type,
                floor_number=task.floor_number,
                is_vip=task.is_vip,
                required_skills=required_skills
            )
            
            if assignee:
                task.assigned_staff_id = assignee.id
                task.assigned_at = datetime.utcnow()
                task.status = TaskStatus.ASSIGNED
                
                assignments.append({
                    "task_id": task.id,
                    "task_reference": task.task_reference,
                    "assigned_to": assignee.id,
                    "staff_name": assignee.full_name
                })
        
        self.db.commit()
        return assignments
