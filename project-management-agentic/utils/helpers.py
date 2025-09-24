import re
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system operations."""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra spaces and dots
    sanitized = re.sub(r'\s+', '_', sanitized.strip())
    sanitized = re.sub(r'\.+', '.', sanitized)
    # Ensure not empty
    if not sanitized or sanitized == '.':
        sanitized = 'unnamed_file'
    return sanitized


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount."""
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string with default fallback."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default
