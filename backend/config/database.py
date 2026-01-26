"""
Database Connection Configuration

This module handles database connection URL construction and
provides connection parameters for SQLAlchemy engine.
"""

from urllib.parse import quote_plus
from backend.config.settings import settings

# =====================================================
# Database URL Construction
# =====================================================

def get_database_url() -> str:
    """
    Construct SQLAlchemy database URL from settings.

    Returns:
        str: Database URL in format: postgresql://user:pass@host:port/db
    """
    # URL-encode password (handles special characters)
    encoded_password = quote_plus(settings.postgres_password)

    return (
        f"postgresql://{settings.postgres_user}:{encoded_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}"
        f"/{settings.postgres_db}"
    )

# Use settings.database_url directly if already configured
DATABASE_URL = get_database_url()

# =====================================================
# Connection Pool Settings
# =====================================================

# Minimal settings for single-user development
POOL_SETTINGS = {
    "pool_size": 3,           # Number of persistent connections
    "max_overflow": 5,        # Additional connections (total max: 8)
    "pool_timeout": 30,       # Seconds to wait for connection
    "pool_recycle": 3600,     # Recycle after 1 hour (prevent stale)
    "pool_pre_ping": True,    # Verify connection before using
}

# =====================================================
# Engine Settings
# =====================================================

ENGINE_SETTINGS = {
    "echo": settings.environment == "development",  # Log SQL in dev
    "echo_pool": False,                              # Don't log pool activity
    "isolation_level": "READ COMMITTED",             # Balance consistency/performance
}
