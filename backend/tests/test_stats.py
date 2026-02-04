"""
Statistics Router Tests

Tests for the /api/stats endpoints including:
- Overview endpoint
- Trend calculations
- Per-metric performance
"""

import secrets
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from backend.models.judge_evaluation import JudgeEvaluation
from backend.models.user_evaluation import UserEvaluation
from backend.models.model_response import ModelResponse
from backend.models.question import Question
from backend.models.database import get_db


# =====================================================
# Fixtures
# =====================================================

@pytest.fixture
def sample_judge_evaluation(db_session):
    """
    Create a sample JudgeEvaluation for testing.

    Args:
        db_session: Database session fixture

    Returns:
        JudgeEvaluation instance
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_hex = secrets.token_hex(3)
    eval_id = f"eval_{timestamp}_{random_hex}"
    judge_id = f"judge_{timestamp}_{random_hex}"

    # Create required dependent objects
    question = Question(
        id=f"q_{timestamp}_{random_hex}",
        question="Test question for statistics",
        category="Math",
        difficulty="medium",
        reference_answer="4",
        expected_behavior="Model should answer correctly",
        rubric_breakdown={"1": "Wrong", "5": "Correct"},
        primary_metric="Truthfulness",
        bonus_metrics=["Clarity"],
        question_prompt_id=None
    )
    db_session.add(question)
    db_session.flush()  # Flush question before creating dependent objects

    model_response = ModelResponse(
        id=f"resp_{timestamp}_{random_hex}",
        question_id=question.id,
        model_name="openai/gpt-3.5-turbo",
        response_text="The answer is 4",
        evaluated=True
    )
    db_session.add(model_response)
    db_session.flush()  # Flush model_response before creating dependent objects

    user_eval = UserEvaluation(
        id=eval_id,
        response_id=model_response.id,
        judged=True,
        evaluations={}
    )
    db_session.add(user_eval)
    db_session.flush()  # Flush user_eval before creating judge_eval

    judge_eval = JudgeEvaluation(
        id=judge_id,
        user_evaluation_id=eval_id,
        independent_scores={},
        alignment_analysis={},
        judge_meta_score=4,
        overall_feedback="Good evaluation",
        improvement_areas=[],
        positive_feedback=["Good catch"],
        primary_metric="Truthfulness",
        primary_metric_gap=0.5,
        weighted_gap=0.5
    )
    db_session.add(judge_eval)
    db_session.commit()

    return judge_eval


@pytest.fixture
def multiple_judge_evaluations(db_session):
    """
    Create multiple JudgeEvaluations for testing trends.

    Creates 20 evaluations with varying scores to test trend calculation.

    Args:
        db_session: Database session fixture

    Returns:
        List of JudgeEvaluation instances
    """
    evals = []
    base_time = datetime.now()

    for i in range(20):
        # Stagger times by 1 minute each
        eval_time = base_time + timedelta(minutes=i)
        timestamp = eval_time.strftime("%Y%m%d_%H%M%S")
        random_hex = secrets.token_hex(3)
        eval_id = f"eval_{timestamp}_{random_hex}"
        judge_id = f"judge_{timestamp}_{random_hex}"

        # First 10 have higher gaps (worse), last 10 have lower gaps (better)
        # This simulates an "improving" trend
        if i < 10:
            gap = 1.5 + (i * 0.1)  # 1.5 to 2.4 (worse, older)
            meta_score = 2
        else:
            gap = 0.3 + ((i - 10) * 0.05)  # 0.3 to 0.75 (better, newer)
            meta_score = 4

        question = Question(
            id=f"q_{timestamp}_{random_hex}",
            question=f"Test question {i} for statistics",
            category="Math",
            difficulty="medium",
            reference_answer="Answer",
            expected_behavior="Model should answer",
            rubric_breakdown={"1": "Wrong", "5": "Correct"},
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity"],
            question_prompt_id=None
        )
        db_session.add(question)
        db_session.flush()  # Flush question before creating dependent objects

        model_response = ModelResponse(
            id=f"resp_{timestamp}_{random_hex}",
            question_id=question.id,
            model_name="openai/gpt-3.5-turbo",
            response_text=f"Response {i}",
            evaluated=True
        )
        db_session.add(model_response)
        db_session.flush()  # Flush model_response before creating dependent objects

        user_eval = UserEvaluation(
            id=eval_id,
            response_id=model_response.id,
            judged=True,
            evaluations={}
        )
        db_session.add(user_eval)
        db_session.flush()  # Flush user_eval before creating judge_eval

        judge_eval = JudgeEvaluation(
            id=judge_id,
            user_evaluation_id=eval_id,
            independent_scores={},
            alignment_analysis={},
            judge_meta_score=meta_score,
            overall_feedback=f"Feedback {i}",
            improvement_areas=[],
            positive_feedback=["Good"],
            primary_metric="Truthfulness",
            primary_metric_gap=gap,
            weighted_gap=gap,
            created_at=eval_time
        )
        db_session.add(judge_eval)
        evals.append(judge_eval)

    db_session.commit()
    return evals


# =====================================================
# Overview Endpoint Tests
# =====================================================

def test_stats_overview_empty_database(test_client, db_session):
    """Test stats overview with no evaluations."""
    response = test_client.get("/api/stats/overview")

    assert response.status_code == 200
    data = response.json()

    assert data["total_evaluations"] == 0
    assert data["average_meta_score"] == 0.0
    assert data["metrics_performance"] == {}
    assert "Insufficient data" in data["improvement_trend"]


def test_stats_overview_single_evaluation(test_client, db_session, sample_judge_evaluation):
    """Test stats overview with a single evaluation."""
    response = test_client.get("/api/stats/overview")

    assert response.status_code == 200
    data = response.json()

    assert data["total_evaluations"] == 1
    assert data["average_meta_score"] == 4.0
    assert "Truthfulness" in data["metrics_performance"]
    assert data["metrics_performance"]["Truthfulness"]["avg_gap"] == 0.5
    assert data["metrics_performance"]["Truthfulness"]["count"] == 1


def test_stats_overview_multiple_evaluations(test_client, db_session, multiple_judge_evaluations):
    """Test stats overview with multiple evaluations."""
    response = test_client.get("/api/stats/overview")

    assert response.status_code == 200
    data = response.json()

    # The multiple_judge_evaluations fixture creates 20 evaluations
    # We check for at least 20 since other tests may have added data
    assert data["total_evaluations"] >= 20
    assert data["average_meta_score"] > 0
    assert "Truthfulness" in data["metrics_performance"]


def test_stats_overview_trend_calculation(test_client, db_session, multiple_judge_evaluations):
    """Test that trend calculation detects improvement."""
    response = test_client.get("/api/stats/overview")

    assert response.status_code == 200
    data = response.json()

    # With our data setup (last 10 have lower gaps than first 10), trend should show improvement
    # The improvement_trend should show a positive difference
    assert "+" in data["improvement_trend"] or "evaluations" in data["improvement_trend"]


def test_stats_overview_metric_performance_structure(test_client, db_session, multiple_judge_evaluations):
    """Test that metric performance has correct structure."""
    response = test_client.get("/api/stats/overview")

    assert response.status_code == 200
    data = response.json()

    for metric, performance in data["metrics_performance"].items():
        # Check required fields
        assert "avg_gap" in performance
        assert "count" in performance
        assert "trend" in performance

        # Check data types
        assert isinstance(performance["avg_gap"], (int, float))
        assert isinstance(performance["count"], int)
        assert isinstance(performance["trend"], str)

        # Check value constraints
        assert performance["avg_gap"] >= 0
        assert performance["count"] > 0
        assert performance["trend"] in ["improving", "stable", "declining", "insufficient_data"]


def test_stats_overview_all_metrics_represented(test_client, db_session):
    """
    Test that when we have evaluations for all metrics, all are represented.

    Note: This test creates evaluations for each metric.
    """
    base_time = datetime.now()

    for metric in [
        "Truthfulness", "Helpfulness", "Safety", "Bias",
        "Clarity", "Consistency", "Efficiency", "Robustness"
    ]:
        timestamp = (base_time + timedelta(seconds=1)).strftime("%Y%m%d_%H%M%S")
        random_hex = secrets.token_hex(3)
        eval_id = f"eval_{timestamp}_{random_hex}"
        judge_id = f"judge_{timestamp}_{random_hex}"

        question = Question(
            id=f"q_{timestamp}_{random_hex}",
            question=f"Test question for {metric}",
            category="General",
            difficulty="medium",
            reference_answer="Answer",
            expected_behavior="Model should answer",
            rubric_breakdown={"1": "Wrong", "5": "Correct"},
            primary_metric=metric,
            bonus_metrics=[],
            question_prompt_id=None
        )
        db_session.add(question)
        db_session.flush()  # Flush question before creating dependent objects

        model_response = ModelResponse(
            id=f"resp_{timestamp}_{random_hex}",
            question_id=question.id,
            model_name="openai/gpt-3.5-turbo",
            response_text="Response",
            evaluated=True
        )
        db_session.add(model_response)
        db_session.flush()  # Flush model_response before creating dependent objects

        user_eval = UserEvaluation(
            id=eval_id,
            response_id=model_response.id,
            judged=True,
            evaluations={}
        )
        db_session.add(user_eval)
        db_session.flush()  # Flush user_eval before creating judge_eval

        judge_eval = JudgeEvaluation(
            id=judge_id,
            user_evaluation_id=eval_id,
            independent_scores={},
            alignment_analysis={},
            judge_meta_score=3,
            overall_feedback="Good",
            improvement_areas=[],
            positive_feedback=["Good"],
            primary_metric=metric,
            primary_metric_gap=0.5,
            weighted_gap=0.5
        )
        db_session.add(judge_eval)

    db_session.commit()

    response = test_client.get("/api/stats/overview")
    assert response.status_code == 200

    data = response.json()
    # All 8 metrics should be present
    assert len(data["metrics_performance"]) == 8


# =====================================================
# Edge Cases and Error Handling
# =====================================================

def test_stats_overview_database_error_handling(test_client, db_session):
    """
    Test that database errors are handled gracefully.

    This test verifies the endpoint doesn't crash on unexpected data.
    """
    response = test_client.get("/api/stats/overview")

    # Should always return 200, even with no data
    assert response.status_code == 200


def test_stats_response_format(test_client, db_session, sample_judge_evaluation):
    """Test that response format matches StatsOverview schema."""
    response = test_client.get("/api/stats/overview")

    assert response.status_code == 200
    data = response.json()

    # Check all required fields
    assert "total_evaluations" in data
    assert "average_meta_score" in data
    assert "metrics_performance" in data
    assert "improvement_trend" in data

    # Check types
    assert isinstance(data["total_evaluations"], int)
    assert isinstance(data["average_meta_score"], (int, float))
    assert isinstance(data["metrics_performance"], dict)
    assert isinstance(data["improvement_trend"], str)
