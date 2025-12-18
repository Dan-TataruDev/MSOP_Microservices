"""
Seed script for housekeeping-maintenance-service.
Generates staff, tasks, and maintenance requests.
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.staff import StaffMember, StaffRole, StaffShift
from app.models.task import Task, TaskType, TaskStatus, TaskPriority
from app.models.maintenance import MaintenanceRequest, MaintenanceCategory, MaintenanceStatus, MaintenancePriority

Base.metadata.create_all(bind=engine)

VENUE_IDS = [str(uuid.uuid4()) for _ in range(10)]
FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", "James", "Maria", "William", "Patricia"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
SKILLS = ["plumbing", "electrical", "hvac", "carpentry", "painting", "cleaning", "inspection"]


def generate_staff(db: Session, num_staff: int = 100):
    """Generate staff member records."""
    print(f"Generating {num_staff} staff members...")
    
    staff = []
    for i in range(num_staff):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        role = random.choice(list(StaffRole))
        department = "housekeeping" if "housekeeping" in role.value else "maintenance"
        
        shift = random.choice(list(StaffShift))
        if shift == StaffShift.MORNING:
            shift_start = datetime.strptime("06:00", "%H:%M").time()
            shift_end = datetime.strptime("14:00", "%H:%M").time()
        elif shift == StaffShift.AFTERNOON:
            shift_start = datetime.strptime("14:00", "%H:%M").time()
            shift_end = datetime.strptime("22:00", "%H:%M").time()
        else:
            shift_start = datetime.strptime("22:00", "%H:%M").time()
            shift_end = datetime.strptime("06:00", "%H:%M").time()
        
        staff_member = StaffMember(
            employee_id=f"EMP{random.randint(10000, 99999)}",
            first_name=first_name,
            last_name=last_name,
            email=f"{first_name.lower()}.{last_name.lower()}@hotel.com",
            phone=f"+1{random.randint(2000000000, 9999999999)}",
            role=role,
            department=department,
            shift=shift,
            shift_start=shift_start,
            shift_end=shift_end,
            working_days=[0, 1, 2, 3, 4] if random.random() > 0.2 else [0, 1, 2, 3, 4, 5],
            skills=random.sample(SKILLS, random.randint(1, 3)) if department == "maintenance" else None,
            can_handle_vip=random.random() > 0.6,
            is_active=random.random() > 0.05,  # 95% active
            is_on_duty=random.random() > 0.4,  # 60% on duty
            tasks_completed_total=random.randint(0, 500),
            average_task_duration_minutes=random.randint(20, 60),
            quality_rating=random.randint(3, 5),
        )
        staff.append(staff_member)
    
    db.bulk_save_objects(staff)
    db.commit()
    print(f"✓ Created {len(staff)} staff members")
    return staff


def generate_tasks(db: Session, staff: list, num_tasks: int = 2000):
    """Generate task records."""
    print(f"Generating {num_tasks} tasks...")
    
    tasks = []
    for i in range(num_tasks):
        task_type = random.choice(list(TaskType))
        status = random.choice(list(TaskStatus))
        priority = random.choice(list(TaskPriority))
        
        venue_id = random.choice(VENUE_IDS)
        scheduled_date = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        due_date = scheduled_date + timedelta(hours=random.randint(1, 8))
        
        assigned_staff = random.choice(staff) if status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.VERIFIED] and random.random() > 0.3 else None
        
        started_at = scheduled_date + timedelta(minutes=random.randint(0, 60)) if status in [TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.VERIFIED] else None
        completed_at = started_at + timedelta(minutes=random.randint(15, 120)) if status in [TaskStatus.COMPLETED, TaskStatus.VERIFIED] else None
        verified_at = completed_at + timedelta(minutes=random.randint(5, 30)) if status == TaskStatus.VERIFIED else None
        
        task = Task(
            task_reference=f"TASK{random.randint(100000, 999999)}",
            task_type=task_type,
            status=status,
            priority=priority,
            venue_id=uuid.UUID(venue_id),
            venue_type=random.choice(["room", "table", "public_area"]),
            location_name=f"Location {random.randint(1, 100)}",
            floor_number=random.randint(1, 10),
            title=f"{task_type.value.replace('_', ' ').title()} Task",
            description=f"Task description for {task_type.value}",
            assigned_staff_id=assigned_staff.id if assigned_staff else None,
            assigned_at=scheduled_date if assigned_staff else None,
            scheduled_date=scheduled_date,
            due_date=due_date,
            estimated_duration_minutes=random.randint(15, 120),
            started_at=started_at,
            completed_at=completed_at,
            verified_at=verified_at,
            is_vip=random.random() > 0.8,
        )
        tasks.append(task)
    
    db.bulk_save_objects(tasks)
    db.commit()
    print(f"✓ Created {len(tasks)} tasks")


def generate_maintenance_requests(db: Session, staff: list, num_requests: int = 500):
    """Generate maintenance request records."""
    print(f"Generating {num_requests} maintenance requests...")
    
    requests = []
    for i in range(num_requests):
        category = random.choice(list(MaintenanceCategory))
        status = random.choice(list(MaintenanceStatus))
        priority = random.choice(list(MaintenancePriority))
        
        venue_id = random.choice(VENUE_IDS)
        reported_at = datetime.utcnow() - timedelta(days=random.randint(0, 90))
        
        triaged_at = reported_at + timedelta(hours=random.randint(1, 24)) if status != MaintenanceStatus.REPORTED else None
        scheduled_for = triaged_at + timedelta(days=random.randint(0, 7)) if status in [MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS, MaintenanceStatus.COMPLETED, MaintenanceStatus.VERIFIED, MaintenanceStatus.CLOSED] else None
        work_started_at = scheduled_for + timedelta(minutes=random.randint(0, 60)) if status in [MaintenanceStatus.IN_PROGRESS, MaintenanceStatus.COMPLETED, MaintenanceStatus.VERIFIED, MaintenanceStatus.CLOSED] else None
        work_completed_at = work_started_at + timedelta(hours=random.randint(1, 8)) if status in [MaintenanceStatus.COMPLETED, MaintenanceStatus.VERIFIED, MaintenanceStatus.CLOSED] else None
        
        assigned_staff = random.choice([s for s in staff if s.department == "maintenance"]) if status in [MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS, MaintenanceStatus.COMPLETED, MaintenanceStatus.VERIFIED, MaintenanceStatus.CLOSED] and random.random() > 0.4 else None
        
        request = MaintenanceRequest(
            request_reference=f"MREQ{random.randint(100000, 999999)}",
            category=category,
            status=status,
            priority=priority,
            venue_id=uuid.UUID(venue_id),
            venue_type="room",
            location_name=f"Room {random.randint(100, 999)}",
            floor_number=random.randint(1, 10),
            specific_location=random.choice(["Bathroom", "Kitchen", "Bedroom", "Living Area", "Window", "Door"]),
            title=f"{category.value.title()} Issue",
            description=f"Maintenance request for {category.value} issue",
            reported_issue=f"Reported issue with {category.value}",
            affects_room_availability=priority in [MaintenancePriority.URGENT, MaintenancePriority.EMERGENCY],
            guest_impact_level=random.choice(["none", "minor", "major", "critical"]),
            safety_concern=priority == MaintenancePriority.EMERGENCY,
            assigned_to_staff_id=assigned_staff.id if assigned_staff else None,
            reported_at=reported_at,
            triaged_at=triaged_at,
            scheduled_for=scheduled_for,
            work_started_at=work_started_at,
            work_completed_at=work_completed_at,
            estimated_cost=Decimal(random.uniform(50.0, 500.0)) if status in [MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS, MaintenanceStatus.COMPLETED, MaintenanceStatus.VERIFIED, MaintenanceStatus.CLOSED] else None,
            actual_cost=Decimal(random.uniform(50.0, 500.0)) if status in [MaintenanceStatus.COMPLETED, MaintenanceStatus.VERIFIED, MaintenanceStatus.CLOSED] else None,
        )
        requests.append(request)
    
    db.bulk_save_objects(requests)
    db.commit()
    print(f"✓ Created {len(requests)} maintenance requests")


def main():
    """Main function to seed the database."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Seeding housekeeping-maintenance-service database...")
        print("=" * 60)
        
        staff = generate_staff(db, num_staff=100)
        generate_tasks(db, staff, num_tasks=2000)
        generate_maintenance_requests(db, staff, num_requests=500)
        
        print("=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

