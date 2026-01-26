"""
MentorMind - Configuration Package

This package contains all configuration-related modules.
"""

from backend.config.settings import settings
from backend.config.database import DATABASE_URL

__all__ = ["settings", "DATABASE_URL"]
