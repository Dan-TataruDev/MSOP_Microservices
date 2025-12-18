"""Utilities for calculating task priorities and due dates."""
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
from app.models.task import TaskPriority


def calculate_priority(
    task_type: str,
    is_vip: bool = False,
    is_safety_concern: bool = False,
    guest_impact: Optional[str] = None,
    base_priority: TaskPriority = TaskPriority.NORMAL
) -> TaskPriority:
    """
    Calculate task priority based on various factors.
    
    Priority escalation rules:
    1. Safety concerns -> CRITICAL
    2. VIP guests -> Boost by 1-2 levels
    3. High guest impact -> Boost by 1 level
    4. Certain task types have inherent priority
    
    Args:
        task_type: Type of task
        is_vip: Whether task is for VIP guest
        is_safety_concern: Whether there's a safety issue
        guest_impact: Impact level ("none", "minor", "major", "critical")
        base_priority: Starting priority level
        
    Returns:
        Calculated TaskPriority
    """
    # Priority ordering for escalation
    priority_levels = [
        TaskPriority.LOW,
        TaskPriority.NORMAL,
        TaskPriority.HIGH,
        TaskPriority.URGENT,
        TaskPriority.CRITICAL
    ]
    
    current_index = priority_levels.index(base_priority)
    
    # Safety concerns are always critical
    if is_safety_concern:
        return TaskPriority.CRITICAL
    
    # VIP boost
    if is_vip:
        current_index = min(current_index + settings.vip_priority_boost, len(priority_levels) - 1)
    
    # Guest impact boost
    impact_boost = {
        "critical": 2,
        "major": 1,
        "minor": 0,
        "none": 0,
    }
    if guest_impact:
        boost = impact_boost.get(guest_impact.lower(), 0)
        current_index = min(current_index + boost, len(priority_levels) - 1)
    
    # Task type inherent priority
    high_priority_types = ["checkout_cleaning", "emergency", "inspection"]
    if task_type in high_priority_types:
        current_index = max(current_index, priority_levels.index(TaskPriority.HIGH))
    
    return priority_levels[current_index]


def calculate_due_date(
    base_time: datetime,
    sla_minutes: int,
    priority: Optional[TaskPriority] = None
) -> datetime:
    """
    Calculate due date based on SLA and priority.
    
    Higher priority tasks get tighter deadlines.
    
    Args:
        base_time: Starting time for calculation
        sla_minutes: Standard SLA in minutes
        priority: Task priority (affects deadline)
        
    Returns:
        Due date/time
    """
    # Priority modifiers (percentage of base SLA)
    priority_modifiers = {
        TaskPriority.CRITICAL: 0.25,  # 25% of normal SLA
        TaskPriority.URGENT: 0.5,     # 50% of normal SLA
        TaskPriority.HIGH: 0.75,      # 75% of normal SLA
        TaskPriority.NORMAL: 1.0,     # 100% of normal SLA
        TaskPriority.LOW: 1.5,        # 150% of normal SLA
    }
    
    modifier = priority_modifiers.get(priority, 1.0) if priority else 1.0
    adjusted_minutes = int(sla_minutes * modifier)
    
    return base_time + timedelta(minutes=adjusted_minutes)


def calculate_escalation_time(
    created_at: datetime,
    priority: TaskPriority,
    base_escalation_minutes: int = 60
) -> datetime:
    """
    Calculate when a task should be escalated if not progressing.
    
    Args:
        created_at: Task creation time
        priority: Current priority
        base_escalation_minutes: Base time before escalation
        
    Returns:
        Time when escalation should occur
    """
    escalation_modifiers = {
        TaskPriority.CRITICAL: 0.25,
        TaskPriority.URGENT: 0.5,
        TaskPriority.HIGH: 0.75,
        TaskPriority.NORMAL: 1.0,
        TaskPriority.LOW: 2.0,
    }
    
    modifier = escalation_modifiers.get(priority, 1.0)
    adjusted_minutes = int(base_escalation_minutes * modifier)
    
    return created_at + timedelta(minutes=adjusted_minutes)
