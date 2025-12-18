"""
Reference and code generators for the Dynamic Pricing Service.
"""
import random
import string
from datetime import datetime


def generate_decision_reference() -> str:
    """
    Generate a unique price decision reference.
    
    Format: PRC-YYYYMMDD-XXXXXX
    Example: PRC-20241218-A3B7C9
    """
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"PRC-{date_part}-{random_part}"


def generate_rule_code(rule_type: str, name: str) -> str:
    """
    Generate a rule code from type and name.
    
    Format: TYPE_NAME_RANDOM
    Example: SEASONAL_CHRISTMAS_2024_X3B7
    """
    # Sanitize name
    sanitized = name.upper().replace(" ", "_").replace("-", "_")
    sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
    sanitized = sanitized[:30]  # Limit length
    
    # Add random suffix for uniqueness
    random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    return f"{rule_type.upper()}_{sanitized}_{random_suffix}"


