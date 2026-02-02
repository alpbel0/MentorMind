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
        # Note: Message now includes background task info
        assert "Evaluation submitted successfully" in data["message"]

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

        # Note: Background task runs in separate session and may fail to find
        # the evaluation since test session data isn't visible to other sessions.
        # This is expected behavior - in production, data is committed immediately.

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


class TestFeedbackEndpointComplete:
    """Tests for complete feedback endpoint implementation (Task 4.10)."""

    def test_feedback_endpoint_complete_judged(self, test_client, db_session):
        """Test feedback endpoint returns complete judge evaluation."""
        from backend.models.judge_evaluation import JudgeEvaluation
        import secrets

        # Setup: Create question, model response, and user evaluation
        question = create_test_question(db_session)
        model_response = create_test_model_response(db_session, question.id)

        eval_id = f"eval_test_{secrets.token_hex(3)}"
        user_eval = UserEvaluation(
            id=eval_id,
            response_id=model_response.id,
            evaluations=get_valid_evaluations_data(),
            judged=True
        )
        db_session.add(user_eval)
        # Flush UserEvaluation first to ensure it exists before adding JudgeEvaluation
        db_session.flush()

        # Create judge evaluation with complete data
        judge_id = f"judge_test_{secrets.token_hex(3)}"
        judge_eval = JudgeEvaluation(
            id=judge_id,
            user_evaluation_id=eval_id,
            independent_scores={
                "Truthfulness": {"score": 4, "rationale": "Accurate"},
                "Helpfulness": {"score": 5, "rationale": "Helpful"},
                "Safety": {"score": 5, "rationale": "Safe"},
                "Bias": {"score": 5, "rationale": "No bias"},
                "Clarity": {"score": 3, "rationale": "Clear"},
                "Consistency": {"score": 5, "rationale": "Consistent"},
                "Efficiency": {"score": 4, "rationale": "Efficient"},
                "Robustness": {"score": 2, "rationale": "Not robust"}
            },
            alignment_analysis={
                "Truthfulness": {
                    "user_score": 4,
                    "judge_score": 4,
                    "gap": 0,
                    "verdict": "aligned",
                    "feedback": "Perfect alignment"
                },
                "Helpfulness": {
                    "user_score": 5,
                    "judge_score": 5,
                    "gap": 0,
                    "verdict": "aligned",
                    "feedback": "Great assessment"
                }
            },
            judge_meta_score=5,
            overall_feedback="Excellent evaluation! Very objective.",
            improvement_areas=[],
            positive_feedback=["Great work overall"],
            vector_context={
                "evaluations": [
                    {"evaluation_id": "eval_001"},
                    {"evaluation_id": "eval_002"}
                ]
            },
            primary_metric="Truthfulness",
            primary_metric_gap=0.0,
            weighted_gap=0.0
        )
        db_session.add(judge_eval)
        # Flush to ensure UserEvaluation is committed before JudgeEvaluation FK check
        db_session.flush()

        # Test the endpoint
        response = test_client.get(f"/api/evaluations/{eval_id}/feedback")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["evaluation_id"] == eval_id
        assert data["judge_meta_score"] == 5
        assert data["overall_feedback"] == "Excellent evaluation! Very objective."
        assert "alignment_analysis" in data
        assert data["improvement_areas"] == []
        assert data["positive_feedback"] == ["Great work overall"]
        assert data["past_patterns_referenced"] == ["eval_001", "eval_002"]

        # Verify alignment_analysis structure
        assert "Truthfulness" in data["alignment_analysis"]
        truthfulness = data["alignment_analysis"]["Truthfulness"]
        assert truthfulness["user_score"] == 4
        assert truthfulness["judge_score"] == 4
        assert truthfulness["gap"] == 0
        assert truthfulness["verdict"] == "aligned"
        assert truthfulness["feedback"] == "Perfect alignment"

    def test_feedback_endpoint_processing_status(self, test_client, db_session):
        """Test feedback endpoint returns processing status for non-judged evaluation."""
        from backend.models.judge_evaluation import JudgeEvaluation
        import secrets

        # Setup: Create question, model response, and non-judged user evaluation
        question = create_test_question(db_session)
        model_response = create_test_model_response(db_session, question.id)

        eval_id = f"eval_test_{secrets.token_hex(3)}"
        user_eval = UserEvaluation(
            id=eval_id,
            response_id=model_response.id,
            evaluations=get_valid_evaluations_data(),
            judged=False  # Not yet judged
        )
        db_session.add(user_eval)
        db_session.flush()

        # Test the endpoint
        response = test_client.get(f"/api/evaluations/{eval_id}/feedback")

        # Should return HTTP 200 with processing status
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert "message" in data
        assert "in progress" in data["message"].lower()

    def test_feedback_endpoint_past_patterns_extracted(self, test_client, db_session):
        """Test past_patterns_referenced correctly extracted from vector_context."""
        from backend.models.judge_evaluation import JudgeEvaluation
        import secrets

        # Setup: Create judged evaluation with vector_context
        question = create_test_question(db_session)
        model_response = create_test_model_response(db_session, question.id)

        eval_id = f"eval_test_{secrets.token_hex(3)}"
        user_eval = UserEvaluation(
            id=eval_id,
            response_id=model_response.id,
            evaluations=get_valid_evaluations_data(),
            judged=True
        )
        db_session.add(user_eval)
        # Flush UserEvaluation first to ensure it exists before adding JudgeEvaluation
        db_session.flush()

        judge_id = f"judge_test_{secrets.token_hex(3)}"
        judge_eval = JudgeEvaluation(
            id=judge_id,
            user_evaluation_id=eval_id,
            independent_scores={},
            alignment_analysis={},
            judge_meta_score=4,
            overall_feedback="Good work",
            improvement_areas=[],
            positive_feedback=[],
            vector_context={
                "evaluations": [
                    {"evaluation_id": "eval_old_001"},
                    {"evaluation_id": "eval_old_002"},
                    {"evaluation_id": "eval_old_003"}
                ]
            },
            primary_metric="Truthfulness",
            primary_metric_gap=0.5,
            weighted_gap=0.5
        )
        db_session.add(judge_eval)
        # Flush to ensure UserEvaluation is committed before JudgeEvaluation FK check
        db_session.flush()

        # Test the endpoint
        response = test_client.get(f"/api/evaluations/{eval_id}/feedback")

        assert response.status_code == 200
        data = response.json()
        assert data["past_patterns_referenced"] == [
            "eval_old_001",
            "eval_old_002",
            "eval_old_003"
        ]

    def test_feedback_endpoint_empty_vector_context(self, test_client, db_session):
        """Test feedback endpoint with empty vector_context."""
        from backend.models.judge_evaluation import JudgeEvaluation
        import secrets

        # Setup: Create judged evaluation with None vector_context
        question = create_test_question(db_session)
        model_response = create_test_model_response(db_session, question.id)

        eval_id = f"eval_test_{secrets.token_hex(3)}"
        user_eval = UserEvaluation(
            id=eval_id,
            response_id=model_response.id,
            evaluations=get_valid_evaluations_data(),
            judged=True
        )
        db_session.add(user_eval)
        # Flush UserEvaluation first to ensure it exists before adding JudgeEvaluation
        db_session.flush()

        judge_id = f"judge_test_{secrets.token_hex(3)}"
        judge_eval = JudgeEvaluation(
            id=judge_id,
            user_evaluation_id=eval_id,
            independent_scores={},
            alignment_analysis={},
            judge_meta_score=3,
            overall_feedback="Needs improvement",
            improvement_areas=["Be more critical"],
            positive_feedback=[],
            vector_context=None,  # No past patterns
            primary_metric="Truthfulness",
            primary_metric_gap=1.0,
            weighted_gap=1.0
        )
        db_session.add(judge_eval)
        # Flush to ensure UserEvaluation is committed before JudgeEvaluation FK check
        db_session.flush()

        # Test the endpoint
        response = test_client.get(f"/api/evaluations/{eval_id}/feedback")

        assert response.status_code == 200
        data = response.json()
        assert data["past_patterns_referenced"] == []

    def test_feedback_endpoint_judge_data_missing(self, test_client, db_session):
        """Test feedback endpoint when judged=TRUE but JudgeEvaluation not found."""
        import secrets

        # Setup: Create judged user evaluation WITHOUT judge evaluation
        # (data inconsistency scenario)
        question = create_test_question(db_session)
        model_response = create_test_model_response(db_session, question.id)

        eval_id = f"eval_test_{secrets.token_hex(3)}"
        user_eval = UserEvaluation(
            id=eval_id,
            response_id=model_response.id,
            evaluations=get_valid_evaluations_data(),
            judged=True  # Marked as judged but no JudgeEvaluation
        )
        db_session.add(user_eval)
        db_session.flush()

        # Test the endpoint - should return HTTP 500
        response = test_client.get(f"/api/evaluations/{eval_id}/feedback")

        assert response.status_code == 500
        assert "not found" in response.json()["detail"].lower()

    def test_feedback_endpoint_evaluation_not_found(self, test_client):
        """Test feedback endpoint with non-existent evaluation."""
        response = test_client.get("/api/evaluations/eval_nonexistent_123/feedback")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_feedback_endpoint_all_8_metrics_in_alignment(self, test_client, db_session):
        """Test feedback endpoint returns all 8 metrics in alignment_analysis."""
        from backend.models.judge_evaluation import JudgeEvaluation
        import secrets

        # Setup: Create judged evaluation with all 8 metrics
        question = create_test_question(db_session)
        model_response = create_test_model_response(db_session, question.id)

        eval_id = f"eval_test_{secrets.token_hex(3)}"
        user_eval = UserEvaluation(
            id=eval_id,
            response_id=model_response.id,
            evaluations=get_valid_evaluations_data(),
            judged=True
        )
        db_session.add(user_eval)
        # Flush UserEvaluation first to ensure it exists before adding JudgeEvaluation
        db_session.flush()

        # Create alignment_analysis with all 8 metrics
        alignment_data = {}
        for metric in [
            "Truthfulness", "Helpfulness", "Safety", "Bias",
            "Clarity", "Consistency", "Efficiency", "Robustness"
        ]:
            alignment_data[metric] = {
                "user_score": 4,
                "judge_score": 4,
                "gap": 0,
                "verdict": "aligned",
                "feedback": f"Good {metric} assessment"
            }

        judge_id = f"judge_test_{secrets.token_hex(3)}"
        judge_eval = JudgeEvaluation(
            id=judge_id,
            user_evaluation_id=eval_id,
            independent_scores={},
            alignment_analysis=alignment_data,
            judge_meta_score=4,
            overall_feedback="All metrics aligned well",
            improvement_areas=[],
            positive_feedback=[],
            vector_context=None,
            primary_metric="Truthfulness",
            primary_metric_gap=0.0,
            weighted_gap=0.0
        )
        db_session.add(judge_eval)
        # Flush to ensure UserEvaluation is committed before JudgeEvaluation FK check
        db_session.flush()

        # Test the endpoint
        response = test_client.get(f"/api/evaluations/{eval_id}/feedback")

        assert response.status_code == 200
        data = response.json()

        # Verify all 8 metrics present
        assert len(data["alignment_analysis"]) == 8
        for metric in [
            "Truthfulness", "Helpfulness", "Safety", "Bias",
            "Clarity", "Consistency", "Efficiency", "Robustness"
        ]:
            assert metric in data["alignment_analysis"]
            metric_data = data["alignment_analysis"][metric]
            assert "user_score" in metric_data
            assert "judge_score" in metric_data
            assert "gap" in metric_data
            assert "verdict" in metric_data
            assert "feedback" in metric_data
