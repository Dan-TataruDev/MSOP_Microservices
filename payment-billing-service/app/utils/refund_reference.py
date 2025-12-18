"""
Utility for generating refund references.
"""
import random
import string
from datetime import datetime


def generate_refund_reference() -> str:
    """Generate a unique refund reference."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"REF-{timestamp}-{random_suffix}"


