"""Utilities for generating task and maintenance reference numbers."""
import random
import string
from datetime import datetime


def generate_task_reference(prefix: str = "TSK") -> str:
    """
    Generate a unique task reference number.
    
    Format: {PREFIX}-{YYMMDD}-{RANDOM}
    Example: CLN-241217-A7K2
    
    Prefixes:
    - TSK: Generic task
    - CLN: Cleaning task
    - MNT: Maintenance task
    - RST: Restocking task
    - INS: Inspection task
    """
    date_part = datetime.utcnow().strftime("%y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{date_part}-{random_part}"


def generate_maintenance_reference() -> str:
    """
    Generate a unique maintenance request reference number.
    
    Format: MR-{YYMMDD}-{RANDOM}
    Example: MR-241217-X9P3
    """
    date_part = datetime.utcnow().strftime("%y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"MR-{date_part}-{random_part}"


def generate_schedule_reference() -> str:
    """
    Generate a unique schedule reference number.
    
    Format: SCH-{RANDOM}
    Example: SCH-M4K9P2
    """
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"SCH-{random_part}"
