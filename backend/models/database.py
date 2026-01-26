"""
SQLAlchemy Database Setup

This module configures SQLAlchemy 2.0 with connection pooling,
session management, and FastAPI dependency injection.
"""

import logging
from typing import Generator

from sqlalchemy import create_engine, pool, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError

from backend.config.settings import settings

logger = logging.getLogger(__name__)

# =====================================================
# Import Database Configuration
# =====================================================

from backend.config.database import DATABASE_URL, POOL_SETTINGS, ENGINE_SETTINGS

# =====================================================
# Database Engine Configuration
# =====================================================

engine = create_engine(
    DATABASE_URL,
    poolclass=pool.QueuePool,
    **POOL_SETTINGS,
    **ENGINE_SETTINGS,
)

# =====================================================
# Session Factory
# =====================================================

SessionLocal = sessionmaker(
    autocommit=False,     # Require explicit commit
    autoflush=False,      # Don't autoflush before query
    bind=engine,
    expire_on_commit=False,  # Keep objects accessible after commit
)

# =====================================================
# SQLAlchemy 2.0 Base Class
# =====================================================

class Base(DeclarativeBase):
    """
    Base class for all ORM models.

    Usage (Task 1.11):
        class Question(Base):
            __tablename__ = "questions"
            id: Mapped[int] = mapped_column(primary_key=True)
    """
    pass

# =====================================================
# FastAPI Dependency: get_db()
# =====================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session management.

    Usage in endpoints:
        @app.get("/questions/{id}")
        def read_question(id: str, db: Session = Depends(get_db)):
            question = db.query(Question).filter(Question.id == id).first()
            return question
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction failed: {e}", exc_info=True)
        raise
    finally:
        db.close()

# =====================================================
# Database Connection Testing
# =====================================================

def test_database_connection() -> bool:
    """
    Test database connection and log result.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("Database connection successful")
        logger.info(f"   Database: {settings.postgres_db}")
        logger.info(f"   Host: {settings.postgres_host}:{settings.postgres_port}")
        logger.info(f"   Pool Size: {engine.pool.size()}")
        logger.info(f"   Pool Overflow: {engine.pool.overflow()}")
        return True

    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_pool_status() -> dict:
    """
    Get current connection pool statistics.

    Returns:
        dict: Pool status information
    """
    return {
        "pool_size": engine.pool.size(),
        "max_overflow": engine.pool._max_overflow,
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
    }

# =====================================================
# Table Management (for Task 1.13)
# =====================================================

def create_tables():
    """Create all tables defined in ORM models."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create tables: {e}")
        raise

def drop_tables():
    """Drop all tables (development/testing only)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except SQLAlchemyError as e:
        logger.error(f"Failed to drop tables: {e}")
        raise
