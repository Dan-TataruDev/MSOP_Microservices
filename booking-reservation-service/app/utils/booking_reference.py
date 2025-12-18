"""
Utility functions for generating booking references.
"""
import random
import string
from datetime import datetime


def generate_booking_reference() -> str:
    """
    Generate a unique booking reference.
    Format: BR-YYYYMMDD-XXXXXX (e.g., BR-20241225-A3B9C2)
    """
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"BR-{date_part}-{random_part}"


