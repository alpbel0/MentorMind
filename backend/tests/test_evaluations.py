"""
Evaluation Router Unit Tests

Tests for user evaluation submission endpoints.
"""

import pytest
import secrets
from sqlalchemy.orm import Session

from backend.main import app
from backend.models.database import get_db
from backend.models.model_response import ModelResponse
from backend.models.user_evaluation import UserEvaluation
from backend.models.question import Question
from backend.models.question_prompt import QuestionPrompt


# =====================================================
# Test Helper Functions
# =====================================================

def create_test_question_prompt(db: Session, metric: str = None, q_type: str = None) -> QuestionPrompt:
    """Create a test question prompt in the database."""
    # Use provided metric/type or defaults, checking for existing prompts
    primary_metric = metric or "Truthfulness"
    question_type = q_type or "hallucination_test"

    # Check if a prompt with these values already exists
    existing = db.query(QuestionPrompt).filter_by(
        primary_metric=primary_metric,
        question_type=question_type
    ).first()
    if existing:
        return existing

    prompt = QuestionPrompt(
        primary_metric=primary_metric,
        bonus_metrics=["Clarity"],
        question_type=question_type,
        user_prompt="Generate a question that tests {metric}",
        golden_examples=[],
        difficulty="easy",
        category_hints=["any"],
    )
    db.add(prompt)
    db.commit()
    return prompt


def create_test_question(db: Session, prompt_id: int = None, suffix: str = None) -> Question:
    """Create a test question in the database."""
    # Create prompt if not provided
    if prompt_id is None:
        prompt = create_test_question_prompt(db)
        prompt_id = prompt.id

    # Generate unique ID if suffix provided
    q_id = "q_test_" + (suffix or secrets.token_hex(3))

    question = Question(
        id=q_id,
        question="What is 2 + 2?",
        category="Math",
        difficulty="easy",
        reference_answer="4",
        expected_behavior="Model should answer correctly",
        rubric_breakdown={
            "1": "Wrong answer",
            "2": "Incorrect but close",
            "3": "Partially correct",
            "4": "Correct with minor issues",
            "5": "Perfect answer",
        },
        primary_metric="Truthfulness",
        bonus_metrics=["Clarity"],
        question_prompt_id=prompt_id,
    )
    db.add(question)
    db.commit()
    return question


def create_test_model_response(db: Session, question_id: str, evaluated: bool = False, suffix: str = None) -> ModelResponse:
    """Create a test model response in the database."""
    # Generate unique ID if suffix provided
    r_id = "resp_test_" + (suffix or secrets.token_hex(3))

    response = ModelResponse(
        id=r_id,
        question_id=question_id,
        model_name="openai/gpt-3.5-turbo",
        response_text="The answer is 4.",
        evaluated=evaluated,
    )
    db.add(response)
    db.commit()
    return response


def get_valid_evaluations_data() -> dict:
    """Return valid evaluation data for all 8 metrics."""
    return {
        "Truthfulness": {"score": 4, "reasoning": "Accurate information"},
        "Helpfulness": {"score": None, "reasoning": "N/A - not applicable"},
        "Safety": {"score": 5, "reasoning": "No harmful content"},
        "Bias": {"score": None, "reasoning": "N/A"},
        "Clarity": {"score": 3, "reasoning": "Could be more clear"},
        "Consistency": {"score": 5, "reasoning": "Consistent answer"},
        "Efficiency": {"score": 4, "reasoning": "Concise"},
        "Robustness": {"score": 2, "reasoning": "Missed edge case"}
    }


# =====================================================
# Test Classes
# =====================================================

class TestEvaluationsRouter:
    """Tests for /api/evaluations endpoints."""

    def test_submit_evaluation_success(self, test_client, db_session):
        """Test successful evaluation submission."""
        # Setup: Create question and model response
        question = create_test_question(db_session)
        model_response = create_test_model_response(db_session, question.id)

        request_data = {
            "response_id": model_response.id,
            "evaluations": get_valid_evaluations_data()
        }

        response = test_client.post(
            "/api/evaluations/submit",
            json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["evaluation_id"].startswith("eval_")
        assert data["status"] == "submitted"
        assert data["message"] == "Evaluation submitted successfully"

        # Verify database state
        db_session.expire_all()
        eval_record = db_session.query(UserEvaluation).filter(
            UserEvaluation.id == data["evaluation_id"]
        ).first()
        assert eval_record is not None
        assert eval_record.response_id == model_response.id

        # Verify model_response.evaluated flag was updated
        db_session.expire_all()
        mr = db_session.query(ModelResponse).filter(
            ModelResponse.id == model_response.id
        ).first()
        assert mr.evaluated is True

    def test_submit_evaluation_missing_metrics(self, test_client, db_session):
        """Test evaluation with missing metrics fails validation."""
        request_data = {
            "response_id": "resp_test_123",
            "evaluations": {
                "Truthfulness": {"score": 4, "reasoning": "Good"},
                "Helpfulness": {"score": 5, "reasoning": "Helpful"},
                # Missing 6 other metrics - should fail
            }
        }

        response = test_client.post(
            "/api/evaluations/submit",
            json=request_data
        )

        assert response.status_code == 422  # Validation error

    def test_submit_evaluation_invalid_score(self, test_client):
        """Test evaluation with invalid score range fails."""
        request_data = {
            "response_id": "resp_test_123",
            "evaluations": {
                "Truthfulness": {"score": 6, "reasoning": "Too high"},
                "Helpfulness": {"score": 0, "reasoning": "Too low"},
                "Safety": {"score": 5, "reasoning": "OK"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Clarity": {"score": 3, "reasoning": "OK"},
                "Consistency": {"score": 4, "reasoning": "OK"},
                "Efficiency": {"score": 5, "reasoning": "OK"},
                "Robustness": {"score": 2, "reasoning": "OK"}
            }
        }

        response = test_client.post(
            "/api/evaluations/submit",
            json=request_data
        )

        assert response.status_code == 422  # Validation error

    def test_submit_evaluation_response_not_found(self, test_client):
        """Test evaluation submission with non-existent response."""
        request_data = {
            "response_id": "resp_nonexistent_123",
            "evaluations": get_valid_evaluations_data()
        }

        response = test_client.post(
            "/api/evaluations/submit",
            json=request_data
        )

        assert response.status_code == 404

    def test_submit_evaluation_already_evaluated(self, test_client, db_session):
        """Test evaluation submission with already evaluated response."""
        # Setup: Create question and already-evaluated model response
        question = create_test_question(db_session)
        model_response = create_test_model_response(
            db_session, question.id, evaluated=True
        )

        request_data = {
            "response_id": model_response.id,
            "evaluations": get_valid_evaluations_data()
        }

        response = test_client.post(
            "/api/evaluations/submit",
            json=request_data
        )

        assert response.status_code == 400
        assert "already evaluated" in response.json()["detail"]

    def test_submit_evaluation_all_null_scores(self, test_client, db_session):
        """Test evaluation with all null scores is allowed."""
        # Setup: Create question and model response
        question = create_test_question(db_session)
        model_response = create_test_model_response(db_session, question.id)

        request_data = {
            "response_id": model_response.id,
            "evaluations": {
                "Truthfulness": {"score": None, "reasoning": "N/A"},
                "Helpfulness": {"score": None, "reasoning": "N/A"},
                "Safety": {"score": None, "reasoning": "N/A"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Clarity": {"score": None, "reasoning": "N/A"},
                "Consistency": {"score": None, "reasoning": "N/A"},
                "Efficiency": {"score": None, "reasoning": "N/A"},
                "Robustness": {"score": None, "reasoning": "N/A"}
            }
        }

        response = test_client.post(
            "/api/evaluations/submit",
            json=request_data
        )

        # Should succeed - all null scores are valid
        assert response.status_code == 200

    def test_submit_evaluation_id_format(self, test_client, db_session):
        """Test that evaluation ID follows correct format."""
        # Setup: Create question and model response
        question = create_test_question(db_session)
        model_response = create_test_model_response(db_session, question.id)

        request_data = {
            "response_id": model_response.id,
            "evaluations": get_valid_evaluations_data()
        }

        response = test_client.post(
            "/api/evaluations/submit",
            json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        eval_id = data["evaluation_id"]

        # Check format: eval_YYYYMMDD_HHMMSS_randomhex
        assert eval_id.startswith("eval_")
        parts = eval_id.split("_")
        # parts[0] = "eval", parts[1] = "YYYYMMDD", parts[2] = "HHMMSS", parts[3] = "randomhex"
        assert len(parts) == 4
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # HHMMSS
        assert len(parts[3]) == 6  # 3 hex bytes = 6 chars

    def test_submit_evaluation_boundary_scores(self, test_client, db_session):
        """Test evaluation with boundary score values (1 and 5)."""
        # Setup: Create question and model response
        question = create_test_question(db_session)
        model_response = create_test_model_response(db_session, question.id)

        request_data = {
            "response_id": model_response.id,
            "evaluations": {
                "Truthfulness": {"score": 1, "reasoning": "Very poor"},
                "Helpfulness": {"score": 5, "reasoning": "Excellent"},
                "Safety": {"score": 1, "reasoning": "Unsafe"},
                "Bias": {"score": 5, "reasoning": "No bias"},
                "Clarity": {"score": None, "reasoning": "N/A"},
                "Consistency": {"score": None, "reasoning": "N/A"},
                "Efficiency": {"score": None, "reasoning": "N/A"},
                "Robustness": {"score": None, "reasoning": "N/A"}
            }
        }

        response = test_client.post(
            "/api/evaluations/submit",
            json=request_data
        )

        # Boundary values should be accepted
        assert response.status_code == 200

    def test_submit_evaluation_missing_reasoning(self, test_client):
        """Test evaluation with missing reasoning fails validation."""
        request_data = {
            "response_id": "resp_test_123",
            "evaluations": {
                "Truthfulness": {"score": 4},  # Missing reasoning
                "Helpfulness": {"score": 5, "reasoning": "OK"},
                "Safety": {"score": 5, "reasoning": "OK"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Clarity": {"score": 3, "reasoning": "OK"},
                "Consistency": {"score": 4, "reasoning": "OK"},
                "Efficiency": {"score": 5, "reasoning": "OK"},
                "Robustness": {"score": 2, "reasoning": "OK"}
            }
        }

        response = test_client.post(
            "/api/evaluations/submit",
            json=request_data
        )

        # Should fail validation because reasoning is required
        assert response.status_code == 422
