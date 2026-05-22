"""
Rate limiter instance for slowapi integration.

Shared across route modules via import. Configured and registered in main.py.
"""

import os
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def get_rate_limit_str() -> str:
    """Return the rate limit string from env, defaulting to '60/minute'."""
    per_minute = os.getenv("RATE_LIMIT_PER_MINUTE", "60")
    return f"{per_minute}/minute"
