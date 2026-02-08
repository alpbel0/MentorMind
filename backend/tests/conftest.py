"""
MentorMind - Test Configuration and Fixtures

This module provides pytest fixtures for testing the MentorMind application.
It sets up the test database, test client, and sample data.

IMPORTANT: SQLAlchemy's create_all() cannot create PostgreSQL ENUM types
and triggers! We must execute the raw SQL schema files in order.
"""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.config.logging_config import setup_logging
from backend.config.settings import settings
from backend.main import app
from backend.models.database import get_db


# =====================================================
# Setup Logging for Tests
# =====================================================

setup_logging()


# =====================================================
# Test Database URL
# =====================================================

@pytest.fixture(scope="session")
def test_database_url() -> str:
    """
    Get the test database URL.

    Uses PostgreSQL (not SQLite) as per user preference.
    Database name: mentormind_test

    Returns:
        Database connection URL string
    """
    # Override the database URL to use test database
    base_url = settings.database_url
    # Replace database name with mentormind_test
    test_url = base_url.rstrip("/").rsplit("/", 1)[0] + "/mentormind_test"
    return test_url


# =====================================================
# Setup Test Schema (SQL Execution)
# =====================================================

@pytest.fixture(scope="session")
def setup_test_schema(test_database_url):
    """
    Execute all SQL schema files in order.

    This is necessary because SQLAlchemy's create_all() cannot create:
    - PostgreSQL ENUM types (metric_type, difficulty_level)
    - Triggers (auto-update updated_at)

    Args:
        test_database_url: Test database URL
    """
    schema_dir = Path(__file__).parent.parent / "schemas"
    schema_files = [
        "00_enums.sql",
        "01_question_prompts.sql",
        "02_questions.sql",
        "03_model_responses.sql",
        "04_user_evaluations.sql",
        "05_judge_evaluations.sql",
        "06_triggers.sql",
        # Hotfix for Task 4.20 - question_type denormalization
        "07_add_question_type_to_questions.sql",
        # Phase 3 schemas for Coach Chat & Evidence feature
        "08_evaluation_snapshots.sql",
        "09_chat_messages.sql",
    ]

    engine = create_engine(test_database_url)

    with engine.begin() as conn:
        for schema_file in schema_files:
            file_path = schema_dir / schema_file
            sql_content = file_path.read_text()
            conn.execute(text(sql_content))
            print(f"✓ Executed: {schema_file}")

    engine.dispose()
    yield

    # Cleanup: Drop all tables after tests complete
    with engine.begin() as conn:
        for schema_file in reversed(schema_files[1:]):  # Skip enums.sql
            table_name = schema_file.split("_", 1)[1].replace(".sql", "")
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))

    # Drop ENUM types
    with engine.begin() as conn:
        conn.execute(text("DROP TYPE IF EXISTS metric_type CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS difficulty_level CASCADE"))

    engine.dispose()


# =====================================================
# Test Engine
# =====================================================

@pytest.fixture(scope="session")
def test_engine(test_database_url, setup_test_schema):
    """
    Create test database engine.

    The engine is created once per test session and shared across all tests.

    Args:
        test_database_url: Test database URL
        setup_test_schema: Schema setup fixture (ensures tables exist)

    Yields:
        SQLAlchemy engine instance
    """
    from sqlalchemy import create_engine

    engine = create_engine(test_database_url)
    yield engine

    # Dispose engine after all tests
    engine.dispose()


# =====================================================
# Test Database Session
# =====================================================

@pytest.fixture(scope="function")
def db_session(test_engine):
    """
    Create a database session for each test function.

    Each test gets a fresh session with automatic rollback after the test.
    This ensures tests don't affect each other.

    Args:
        test_engine: Test database engine

    Yields:
        SQLAlchemy Session instance
    """
    from sqlalchemy.orm import sessionmaker

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    session = TestSessionLocal()

    yield session

    # Rollback all changes after test
    session.rollback()
    session.close()


# =====================================================
# Test Client
# =====================================================

@pytest.fixture(scope="function")
def test_client(db_session):
    """
    Create a FastAPI test client with database override.

    The test client can make HTTP requests to the application
    without running a server.
    Uses db_session to override the database dependency.

    Args:
        db_session: Database session fixture

    Yields:
        TestClient instance with database override
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app=app) as client:
        yield client

    app.dependency_overrides.clear()


# =====================================================
# Sample Data Fixtures
# =====================================================

@pytest.fixture
def sample_question_prompt():
    """
    Provide a sample QuestionPrompt for testing.

    Returns:
        Dictionary with question prompt data
    """
    return {
        "primary_metric": "Truthfulness",
        "bonus_metrics": ["Clarity", "Helpfulness"],
        "question_type": "hallucination_test",
        "user_prompt": "Generate a question that tests {metric}",
        "golden_examples": [],
        "difficulty": "easy",
        "category_hints": ["any"],
    }


@pytest.fixture
def sample_question():
    """
    Provide a sample Question for testing.

    Returns:
        Dictionary with question data
    """
    return {
        "id": "q_test_001",
        "question": "What is 2 + 2?",
        "category": "Math",
        "reference_answer": "4",
        "expected_behavior": "Model should answer correctly",
        "rubric_breakdown": {
            "1": "Wrong answer",
            "2": "Incorrect but close",
            "3": "Partially correct",
            "4": "Correct with minor issues",
            "5": "Perfect answer",
        },
        "primary_metric": "Truthfulness",
        "bonus_metrics": ["Clarity"],
        "question_prompt_id": 1,
    }
