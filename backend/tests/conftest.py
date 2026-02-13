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
# Pytest Configuration
# =====================================================

def pytest_configure(config):
    """
    Register custom pytest markers.

    Markers:
        live_api: Tests requiring live API calls (e.g., OpenAI, Anthropic)
    """
    config.addinivalue_line(
        "markers",
        "live_api: mark test as requiring live API calls (e.g., OPENAI_API_KEY required)"
    )


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
    # The URL format is: postgresql://user:pass@host:port
    # We need to append /mentormind_test for the test database
    test_url = base_url.rstrip("/") + "/mentormind_test"
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
        conn.execute(text("DROP TYPE IF EXISTS snapshot_status CASCADE"))

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
# Clean Database Tables
# =====================================================

@pytest.fixture(scope="function", autouse=True)
def clean_database_tables(test_engine):
    """
    Clean all test tables before each test.

    Using autouse=True means this runs before every test function.
    """
    from sqlalchemy import text

    with test_engine.begin() as conn:
        # Clean all tables except enums
        tables = [
            "question_prompts", "questions", "model_responses",
            "user_evaluations", "judge_evaluations",
            "evaluation_snapshots", "chat_messages"
        ]
        for table in tables:
            conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    yield


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
        expire_on_commit=False,
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


# =====================================================
# ORM Fixtures for Snapshot Service Tests
# =====================================================

@pytest.fixture
def make_question(db_session):
    """
    Create a Question ORM object for testing.

    Args:
        db_session: Database session fixture

    Returns:
        Function that creates Question objects
    """
    from backend.models.question import Question
    from datetime import datetime
    import uuid

    # Counter for unique IDs
    counter = {"value": 0}

    def _create(**kwargs):
        counter["value"] += 1
        unique_id = f"q_test_{datetime.now().strftime('%Y%m%d%H%M%S')}_{counter['value']}"

        data = {
            "id": unique_id,
            "question": "Test question?",
            "category": "General",
            "difficulty": "easy",
            "reference_answer": "Test answer",
            "expected_behavior": "Should work",
            "rubric_breakdown": {"1": "Bad", "5": "Good"},
            "primary_metric": kwargs.get("primary_metric", "Truthfulness"),
            "bonus_metrics": kwargs.get("bonus_metrics", []),
            "question_type": kwargs.get("question_type", "general"),
        }
        data.update(kwargs)

        question = Question(**data)
        db_session.add(question)
        db_session.flush()  # Use flush instead of commit for test isolation
        return question

    return _create


@pytest.fixture
def make_model_response(db_session):
    """
    Create a ModelResponse ORM object for testing.

    Args:
        db_session: Database session fixture

    Returns:
        Function that creates ModelResponse objects
    """
    from backend.models.model_response import ModelResponse
    from datetime import datetime

    # Counter for unique IDs
    counter = {"value": 0}

    def _create(question_id=None, **kwargs):
        counter["value"] += 1
        unique_id = f"resp_test_{datetime.now().strftime('%Y%m%d%H%M%S')}_{counter['value']}"

        data = {
            "id": unique_id,
            "question_id": question_id or "q_test",
            "model_name": "openai/gpt-3.5-turbo",
            "response_text": "This is a test response.",
        }
        data.update(kwargs)

        response = ModelResponse(**data)
        db_session.add(response)
        db_session.flush()  # Use flush instead of commit for test isolation
        return response

    return _create


@pytest.fixture
def make_user_evaluation(db_session):
    """
    Create a UserEvaluation ORM object for testing.

    Args:
        db_session: Database session fixture

    Returns:
        Function that creates UserEvaluation objects
    """
    from backend.models.user_evaluation import UserEvaluation
    from datetime import datetime

    # Counter for unique IDs
    counter = {"value": 0}

    def _create(response_id=None, **kwargs):
        counter["value"] += 1
        unique_id = f"eval_test_{datetime.now().strftime('%Y%m%d%H%M%S')}_{counter['value']}"

        data = {
            "id": unique_id,
            "response_id": response_id or "resp_test",
            "evaluations": {
                "Truthfulness": {"score": 4, "reasoning": "Good"},
                "Helpfulness": {"score": 3, "reasoning": "OK"},
                "Safety": {"score": 5, "reasoning": "Safe"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Clarity": {"score": 4, "reasoning": "Clear"},
                "Consistency": {"score": 4, "reasoning": "Consistent"},
                "Efficiency": {"score": 4, "reasoning": "Efficient"},
                "Robustness": {"score": 4, "reasoning": "Robust"},
            },
        }
        data.update(kwargs)

        user_eval = UserEvaluation(**data)
        db_session.add(user_eval)
        db_session.flush()  # Use flush instead of commit for test isolation
        return user_eval

    return _create


@pytest.fixture
def make_snapshot(db_session):
    """
    Create an EvaluationSnapshot ORM object for testing.

    Args:
        db_session: Database session fixture

    Returns:
        Function that creates EvaluationSnapshot objects
    """
    from backend.models.evaluation_snapshot import EvaluationSnapshot
    from datetime import datetime
    import secrets

    def _create(**kwargs):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hex = secrets.token_hex(6)
        snapshot_id = f"snap_{timestamp}_{random_hex}"

        data = {
            "id": snapshot_id,
            "question_id": "q_test",
            "question": "Test question?",
            "model_answer": "Test answer",
            "model_name": "openai/gpt-3.5-turbo",
            "judge_model": "gpt-4o",
            "primary_metric": kwargs.get("primary_metric", "truthfulness"),
            "bonus_metrics": [],
            "category": "General",
            "user_scores_json": {"truthfulness": {"score": 4, "reasoning": "Good"}},
            "judge_scores_json": {"truthfulness": {"score": 5, "rationale": "Excellent"}},
            "evidence_json": None,
            "judge_meta_score": 5,
            "weighted_gap": 0.2,
            "overall_feedback": "Good job",
            "user_evaluation_id": "eval_test",
            "judge_evaluation_id": "judge_test",
            "chat_turn_count": 0,
            "max_chat_turns": 15,
            "status": kwargs.get("status", "active"),
            "deleted_at": None,
        }
        data.update(kwargs)

        snapshot = EvaluationSnapshot(**data)
        db_session.add(snapshot)
        db_session.flush()  # Use flush instead of commit for test isolation
        return snapshot

    return _create
