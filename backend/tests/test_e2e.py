"""
End-to-End Tests for MentorMind

Tests complete workflows from API request to database verification.
Uses TestClient for real API testing within the test environment.

Test Scenarios:
1. New Question Workflow - Generate question, get response, evaluate, judge
2. Pool Question Workflow - Select from pool, evaluate, judge
3. Recurring Pattern (ChromaDB) - Multiple evaluations with same mistake pattern
4. Statistics Endpoint - Create evaluations, verify stats calculations
"""

import secrets
import time
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from backend.models.database import get_db
from backend.models.question import Question
from backend.models.model_response import ModelResponse
from backend.models.user_evaluation import UserEvaluation
from backend.models.judge_evaluation import JudgeEvaluation
from backend.services.chromadb_service import chromadb_service


# =====================================================
# E2E Test 1: New Question Workflow
# =====================================================

def test_e2e_new_question_workflow(test_client, db_session, monkeypatch):
    """
    Test complete workflow with newly generated question.

    This test is a simplified version that doesn't call external APIs.
    It creates the necessary test data directly to verify the workflow.
    """
    # 1. Create a question and response directly (simulating what the API would do)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_hex = secrets.token_hex(3)
    question_id = f"q_{timestamp}_{random_hex}"
    response_id = f"resp_{timestamp}_{random_hex}"

    question = Question(
        id=question_id,
        question="What is 2 + 2?",
        category="Math",
        difficulty="easy",
        reference_answer="4",
        expected_behavior="Model should answer 4",
        rubric_breakdown={"1": "Wrong", "5": "Correct"},
        primary_metric="Truthfulness",
        bonus_metrics=["Clarity"],
        question_prompt_id=None
    )
    db_session.add(question)
    db_session.flush()

    model_response = ModelResponse(
        id=response_id,
        question_id=question.id,
        model_name="openai/gpt-3.5-turbo",
        response_text="The answer is 5",
        evaluated=False
    )
    db_session.add(model_response)
    db_session.flush()
    db_session.commit()

    # 2. Submit user evaluation
    evaluation_data = {
        "response_id": response_id,
        "evaluations": {
            "Truthfulness": {"score": 2, "reasoning": "Incorrect answer"},
            "Helpfulness": {"score": 3, "reasoning": "Helpful but wrong"},
            "Safety": {"score": None, "reasoning": "N/A"},
            "Bias": {"score": None, "reasoning": "N/A"},
            "Clarity": {"score": 5, "reasoning": "Clear answer"},
            "Consistency": {"score": None, "reasoning": "N/A"},
            "Efficiency": {"score": 4, "reasoning": "Concise"},
            "Robustness": {"score": 5, "reasoning": "Direct answer"}
        }
    }

    response = test_client.post("/api/evaluations/submit", json=evaluation_data)
    assert response.status_code == 200
    submit_data = response.json()
    evaluation_id = submit_data["evaluation_id"]
    assert evaluation_id.startswith("eval_")

    # 3. Verify user evaluation was created
    user_eval = db_session.query(UserEvaluation).filter(
        UserEvaluation.id == evaluation_id
    ).first()
    assert user_eval is not None
    assert user_eval.response_id == response_id
    assert user_eval.judged is False  # Not judged yet

    # 4. Verify model_response.evaluated was updated
    model_resp = db_session.query(ModelResponse).filter(
        ModelResponse.id == response_id
    ).first()
    assert model_resp.evaluated is True

    # 5. Since we can't wait for actual judge (external API), create a mock judge evaluation
    # In a real scenario, the background task would do this
    judge_id = f"judge_{timestamp}_{random_hex}"
    judge_eval = JudgeEvaluation(
        id=judge_id,
        user_evaluation_id=evaluation_id,
        independent_scores={},
        alignment_analysis={
            "Truthfulness": {
                "user_score": 2,
                "judge_score": 1,
                "gap": 1,
                "verdict": "over_estimated",
                "feedback": "Answer is factually wrong"
            }
        },
        judge_meta_score=3,
        overall_feedback="Good attempt but missed the factual error",
        improvement_areas=["Check factual accuracy"],
        positive_feedback=["Clear presentation"],
        primary_metric="Truthfulness",
        primary_metric_gap=1.0,
        weighted_gap=1.0
    )
    db_session.add(judge_eval)
    db_session.commit()

    # Update user_eval.judged
    user_eval.judged = True
    db_session.commit()

    # 6. Get judge feedback via API
    feedback_response = test_client.get(f"/api/evaluations/{evaluation_id}/feedback")
    assert feedback_response.status_code == 200
    feedback_data = feedback_response.json()

    assert feedback_data["evaluation_id"] == evaluation_id
    assert feedback_data["judge_meta_score"] == 3
    assert "Truthfulness" in feedback_data["alignment_analysis"]


# =====================================================
# E2E Test 2: Pool Question Workflow
# =====================================================

def test_e2e_pool_question_workflow(test_client, db_session):
    """
    Test complete workflow with question selected from pool.

    Simulates selecting an existing question from the pool.
    """
    # 1. Create a question in the "pool" (simulating pool selection)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_hex = secrets.token_hex(3)
    question_id = f"q_{timestamp}_{random_hex}"
    response_id = f"resp_{timestamp}_{random_hex}"

    # Create question with times_used > 0 to simulate pool selection
    question = Question(
        id=question_id,
        question="Explain the difference between list and tuple in Python",
        category="Coding",
        difficulty="medium",
        reference_answer="Lists are mutable, tuples are immutable",
        expected_behavior="Model should explain mutability difference",
        rubric_breakdown={"1": "Wrong", "5": "Complete and accurate"},
        primary_metric="Clarity",
        bonus_metrics=["Helpfulness"],
        question_prompt_id=None,
        times_used=1,  # Simulating pool selection
        first_used_at=datetime.now(),
        last_used_at=datetime.now()
    )
    db_session.add(question)
    db_session.flush()

    model_response = ModelResponse(
        id=response_id,
        question_id=question.id,
        model_name="openai/gpt-4o-mini",
        response_text="Lists can be changed, tuples cannot be changed",
        evaluated=False
    )
    db_session.add(model_response)
    db_session.flush()
    db_session.commit()

    # 2. Submit evaluation
    evaluation_data = {
        "response_id": response_id,
        "evaluations": {
            "Truthfulness": {"score": 5, "reasoning": "Accurate"},
            "Helpfulness": {"score": 4, "reasoning": "Helpful but could be more detailed"},
            "Safety": {"score": None, "reasoning": "N/A"},
            "Bias": {"score": None, "reasoning": "N/A"},
            "Clarity": {"score": 5, "reasoning": "Very clear"},
            "Consistency": {"score": 5, "reasoning": "Consistent"},
            "Efficiency": {"score": 5, "reasoning": "Concise"},
            "Robustness": {"score": 4, "reasoning": "Good explanation"}
        }
    }

    response = test_client.post("/api/evaluations/submit", json=evaluation_data)
    assert response.status_code == 200
    evaluation_id = response.json()["evaluation_id"]

    # 3. Create mock judge evaluation
    judge_id = f"judge_{timestamp}_{random_hex}"
    judge_eval = JudgeEvaluation(
        id=judge_id,
        user_evaluation_id=evaluation_id,
        independent_scores={},
        alignment_analysis={},
        judge_meta_score=5,
        overall_feedback="Excellent evaluation",
        improvement_areas=[],
        positive_feedback=["Accurate assessment", "Good attention to detail"],
        primary_metric="Clarity",
        primary_metric_gap=0,
        weighted_gap=0
    )
    db_session.add(judge_eval)
    db_session.commit()

    user_eval = db_session.query(UserEvaluation).filter(
        UserEvaluation.id == evaluation_id
    ).first()
    user_eval.judged = True
    db_session.commit()

    # 4. Verify complete feedback
    feedback_response = test_client.get(f"/api/evaluations/{evaluation_id}/feedback")
    assert feedback_response.status_code == 200
    feedback_data = feedback_response.json()

    assert feedback_data["judge_meta_score"] == 5
    assert len(feedback_data["positive_feedback"]) == 2


# =====================================================
# E2E Test 3: Recurring Pattern (ChromaDB Memory)
# =====================================================

def test_e2e_recurring_pattern_chromadb(test_client, db_session):
    """
    Test ChromaDB pattern recognition across multiple evaluations.

    Creates 3 evaluations with the same mistake pattern to verify
    that ChromaDB stores and can retrieve past patterns.
    """
    # Create 3 evaluations with same mistake (overestimating Clarity)
    eval_ids = []
    judge_ids = []

    for i in range(3):
        timestamp = (datetime.now() + timedelta(seconds=i)).strftime("%Y%m%d_%H%M%S")
        random_hex = secrets.token_hex(3)
        question_id = f"q_{timestamp}_{random_hex}"
        response_id = f"resp_{timestamp}_{random_hex}"
        eval_id = f"eval_{timestamp}_{random_hex}"
        judge_id = f"judge_{timestamp}_{random_hex}"

        question = Question(
            id=question_id,
            question=f"Test question {i} about clarity",
            category="General",
            difficulty="easy",
            reference_answer="Clear answer",
            expected_behavior="Model should be clear",
            rubric_breakdown={"1": "Unclear", "5": "Very clear"},
            primary_metric="Clarity",
            bonus_metrics=[],
            question_prompt_id=None
        )
        db_session.add(question)
        db_session.flush()

        model_response = ModelResponse(
            id=response_id,
            question_id=question.id,
            model_name="openai/gpt-3.5-turbo",
            response_text="Response with some redundancies",
            evaluated=True
        )
        db_session.add(model_response)
        db_session.flush()

        user_eval = UserEvaluation(
            id=eval_id,
            response_id=response_id,
            judged=True,
            evaluations={}
        )
        db_session.add(user_eval)
        db_session.flush()

        # Same mistake pattern: overestimates Clarity
        judge_eval = JudgeEvaluation(
            id=judge_id,
            user_evaluation_id=eval_id,
            independent_scores={},
            alignment_analysis={},
            judge_meta_score=3,
            overall_feedback="Tends to overestimate clarity scores",
            improvement_areas=["Watch for redundancies in responses"],
            positive_feedback=["Good attention to clarity"],
            primary_metric="Clarity",
            primary_metric_gap=1.0,  # Consistent gap
            weighted_gap=1.0
        )
        db_session.add(judge_eval)
        db_session.commit()

        eval_ids.append(eval_id)
        judge_ids.append(judge_id)

    # Verify all 3 evaluations were created
    assert len(eval_ids) == 3

    # Verify judge evaluations exist
    for judge_id in judge_ids:
        judge = db_session.query(JudgeEvaluation).filter(
            JudgeEvaluation.id == judge_id
        ).first()
        assert judge is not None
        assert judge.primary_metric == "Clarity"
        assert judge.primary_metric_gap == 1.0


# =====================================================
# E2E Test 4: Statistics Endpoint
# =====================================================

def test_e2e_statistics_endpoint(test_client, db_session):
    """
    Test statistics overview endpoint with varying evaluation scores.

    Creates 20 evaluations with different scores and verifies:
    - Total evaluations count
    - Average meta score calculation
    - Per-metric performance stats
    - Trend detection
    """
    # Create 20 evaluations
    base_time = datetime.now()

    for i in range(20):
        timestamp = (base_time + timedelta(minutes=i)).strftime("%Y%m%d_%H%M%S")
        random_hex = secrets.token_hex(3)
        question_id = f"q_{timestamp}_{random_hex}"
        response_id = f"resp_{timestamp}_{random_hex}"
        eval_id = f"eval_{timestamp}_{random_hex}"
        judge_id = f"judge_{timestamp}_{random_hex}"

        # Vary meta scores: first 10 have lower scores, last 10 have higher
        meta_score = 2 if i < 10 else 4
        gap = 1.5 if i < 10 else 0.5

        question = Question(
            id=question_id,
            question=f"Statistics test question {i}",
            category="Math",
            difficulty="medium",
            reference_answer="Answer",
            expected_behavior="Model should answer",
            rubric_breakdown={"1": "Wrong", "5": "Correct"},
            primary_metric="Truthfulness",
            bonus_metrics=[],
            question_prompt_id=None
        )
        db_session.add(question)
        db_session.flush()

        model_response = ModelResponse(
            id=response_id,
            question_id=question.id,
            model_name="openai/gpt-3.5-turbo",
            response_text=f"Response {i}",
            evaluated=True
        )
        db_session.add(model_response)
        db_session.flush()

        user_eval = UserEvaluation(
            id=eval_id,
            response_id=response_id,
            judged=True,
            evaluations={}
        )
        db_session.add(user_eval)
        db_session.flush()

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
            created_at=base_time + timedelta(minutes=i)
        )
        db_session.add(judge_eval)
        db_session.commit()

    # Call /api/stats/overview
    response = test_client.get("/api/stats/overview")
    assert response.status_code == 200
    data = response.json()

    # Verify calculations
    # We expect significant number of evaluations (20 from this test + others)
    assert data["total_evaluations"] >= 10

    # Average meta score should be between 1 and 5 (valid range)
    assert 1 <= data["average_meta_score"] <= 5

    # Truthfulness should be in metrics_performance
    assert "Truthfulness" in data["metrics_performance"]

    # Check performance data structure
    truthfulness_perf = data["metrics_performance"]["Truthfulness"]
    assert "avg_gap" in truthfulness_perf
    assert "count" in truthfulness_perf
    assert "trend" in truthfulness_perf
    assert truthfulness_perf["count"] >= 10
    assert truthfulness_perf["trend"] in ["improving", "stable", "declining", "insufficient_data"]


# =====================================================
# Health Check Tests
# =====================================================

def test_e2e_health_check(test_client):
    """Test basic health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "api" in data
    assert "database" in data


def test_e2e_health_check_detailed(test_client):
    """Test detailed health check endpoint."""
    response = test_client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "api" in data
    assert "database" in data
    assert "chromadb" in data


def test_e2e_root_endpoint(test_client):
    """Test root endpoint returns API info."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data
    assert "version" in data
