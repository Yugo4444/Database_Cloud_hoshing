"""
Application configuration
"""

import os
from functools import lru_cache

def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable not set."
        )
    return url

@lru_cache
def get_settings():
    """
    Cached application settings object.
    """
    return type(
        "Settings",
        (),
        {
            "database_url": _get_database_url(),
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
    )()