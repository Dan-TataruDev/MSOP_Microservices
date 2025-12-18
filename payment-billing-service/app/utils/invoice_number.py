"""
Utility for generating invoice numbers.
"""
import random
import string
from datetime import datetime
from app.config import settings


def generate_invoice_number() -> str:
    """Generate a unique invoice number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.digits, k=6))
    return f"{settings.invoice_number_prefix}-{timestamp}-{random_suffix}"


