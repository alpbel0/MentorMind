"""
Tests for Judge Service - Live GPT-4o API

These tests use live GPT-4o API calls (no mocks).
Ensure OPENAI_API_KEY is set in environment.
"""

import pytest
from sqlalchemy.orm import Session

from backend.services.judge_service import JudgeService, THE_EIGHT_METRICS
from backend.models.user_evaluation import UserEvaluation
from backend.models.model_response import ModelResponse
from backend.models.question import Question


class TestJudgeServiceInit:
    """Test JudgeService initialization."""

    def test_service_initialization(self):
        """Test JudgeService initializes correctly."""
        service = JudgeService()
        assert service.model == "gpt-4o"
        assert service.client is not None
        assert service.timeout == 60


class TestFetchEvaluationData:
    """Test data fetching logic."""

    def test_fetch_evaluation_data_success(self, db_session):
        """Test successful data fetching with inline data creation."""
        # Setup: Create test data inline (no external fixture)
        from datetime import datetime
        question = Question(
            id="q_fetch_test_001",
            question="Test question?",
            category="Testing",
            difficulty="medium",
            reference_answer="Test answer",
            expected_behavior="Test behavior",
            rubric_breakdown={"1": "Bad", "5": "Good"},
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()  # Flush to get the question in the DB before creating model_response

        model_response = ModelResponse(
            id="resp_fetch_test_001",
            question_id="q_fetch_test_001",
            model_name="openai/gpt-3.5-turbo",
            response_text="Test response",
            evaluated=False
        )
        db_session.add(model_response)

        user_eval = UserEvaluation(
            id="eval_fetch_test_001",
            response_id="resp_fetch_test_001",
            evaluations={
                "Truthfulness": {"score": 3, "reasoning": "Test"},
                "Helpfulness": {"score": 3, "reasoning": "Test"},
                "Safety": {"score": None, "reasoning": "N/A"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Clarity": {"score": 3, "reasoning": "Test"},
                "Consistency": {"score": None, "reasoning": "N/A"},
                "Efficiency": {"score": None, "reasoning": "N/A"},
                "Robustness": {"score": None, "reasoning": "N/A"}
            },
            judged=False
        )
        db_session.add(user_eval)
        db_session.commit()

        # Execute
        service = JudgeService()
        result = service.fetch_evaluation_data("eval_fetch_test_001", db_session)

        # Verify
        assert "user_eval" in result
        assert "model_response" in result
        assert "question" in result
        assert "user_scores" in result
        assert len(result["user_scores"]) == 8

    def test_fetch_evaluation_data_not_found(self, db_session):
        """Test error when evaluation not found."""
        service = JudgeService()
        with pytest.raises(ValueError, match="not found"):
            service.fetch_evaluation_data("eval_nonexistent", db_session)

    def test_fetch_evaluation_data_missing_metrics(self, db_session):
        """Test error when user evaluation missing metrics."""
        # Create evaluation with only 1 metric (inline, no fixture)
        from datetime import datetime
        question = Question(
            id="q_fetch_test_002",
            question="Test?",
            category="Test",
            difficulty="medium",
            reference_answer="Answer",
            expected_behavior="Behavior",
            rubric_breakdown={"1": "Bad", "5": "Good"},
            primary_metric="Truthfulness",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()  # Flush before creating model_response

        model_response = ModelResponse(
            id="resp_fetch_test_002",
            question_id="q_fetch_test_002",
            model_name="openai/gpt-3.5-turbo",
            response_text="Response",
            evaluated=False
        )
        db_session.add(model_response)

        user_eval = UserEvaluation(
            id="eval_fetch_test_002",
            response_id="resp_fetch_test_002",
            evaluations={"Truthfulness": {"score": 3, "reasoning": "..."}}
        )
        db_session.add(user_eval)
        db_session.commit()

        service = JudgeService()
        with pytest.raises(ValueError, match="missing metrics"):
            service.fetch_evaluation_data("eval_fetch_test_002", db_session)


class TestParseJudgeResponse:
    """Test response parsing."""

    def test_parse_direct_json(self):
        """Test parsing direct JSON."""
        service = JudgeService()
        response = '{"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test"}}}'
        result = service.parse_judge_response(response)
        assert "independent_scores" in result
        assert result["independent_scores"]["Truthfulness"]["score"] == 3

    def test_parse_markdown_json(self):
        """Test parsing JSON in markdown code block."""
        service = JudgeService()
        response = '''```json
{
  "independent_scores": {
    "Truthfulness": {"score": 4, "rationale": "Test"}
  }
}
```'''
        result = service.parse_judge_response(response)
        assert "independent_scores" in result

    def test_parse_with_extra_text(self):
        """Test parsing JSON with extra text before/after."""
        service = JudgeService()
        response = '''Here is the evaluation:

```json
{"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test"}}}
```

That's my assessment.'''
        result = service.parse_judge_response(response)
        assert "independent_scores" in result

    def test_parse_invalid_json(self):
        """Test error on invalid JSON."""
        service = JudgeService()
        with pytest.raises(ValueError, match="Invalid JSON"):
            service.parse_judge_response("not json at all")

    def test_parse_missing_key(self):
        """Test error when independent_scores missing."""
        service = JudgeService()
        with pytest.raises(ValueError, match="missing 'independent_scores'"):
            service.parse_judge_response('{"other_key": "value"}')


class TestStage1LiveAPI:
    """Test Stage 1 evaluation with live GPT-4o API."""

    @pytest.mark.live_api
    def test_stage1_wrong_answer(self, db_session):
        """Test Stage 1 with a wrong model response."""
        # Setup: Create test evaluation with wrong answer (inline data)
        from datetime import datetime
        question = Question(
            id="q_test_001",
            question="What is 2+2?",
            category="Mathematics",
            difficulty="easy",
            reference_answer="4",
            expected_behavior="Model should answer correctly",
            rubric_breakdown={
                "1": "Completely wrong",
                "5": "Correct answer"
            },
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Helpfulness"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()  # Flush before creating model_response

        model_response = ModelResponse(
            id="resp_test_001",
            question_id="q_test_001",
            model_name="openai/gpt-3.5-turbo",
            response_text="The answer is 5.",
            evaluated=False
        )
        db_session.add(model_response)
        db_session.flush()  # Flush before creating user_evaluation

        user_eval = UserEvaluation(
            id="eval_test_001",
            response_id="resp_test_001",
            evaluations={
                "Truthfulness": {"score": 2, "reasoning": "Wrong answer"},
                "Helpfulness": {"score": 3, "reasoning": "Brief but incorrect"},
                "Safety": {"score": None, "reasoning": "Not applicable"},
                "Bias": {"score": None, "reasoning": "Not applicable"},
                "Clarity": {"score": 5, "reasoning": "Clear"},
                "Consistency": {"score": None, "reasoning": "Not applicable"},
                "Efficiency": {"score": 4, "reasoning": "Concise"},
                "Robustness": {"score": None, "reasoning": "Not applicable"}
            },
            judged=False
        )
        db_session.add(user_eval)
        db_session.commit()

        # Execute: Call Stage 1
        service = JudgeService()
        result = service.stage1_independent_evaluation("eval_test_001", db_session)

        # Verify
        assert "independent_scores" in result
        scores = result["independent_scores"]

        # All 8 metrics present
        assert len(scores) == 8
        for metric in THE_EIGHT_METRICS:
            assert metric in scores
            assert "score" in scores[metric]
            assert "rationale" in scores[metric]

            # Score validation
            score = scores[metric]["score"]
            assert score is None or isinstance(score, int)
            if score is not None:
                assert 1 <= score <= 5

            # Rationale is string (Turkish expected)
            assert isinstance(scores[metric]["rationale"], str)
            assert len(scores[metric]["rationale"]) > 0

        # Log for manual verification
        print(f"\n=== GPT-4o Stage 1 Evaluation ===")
        for metric, data in scores.items():
            if data["score"] is not None:
                print(f"{metric}: {data['score']}/5 - {data['rationale']}")

    @pytest.mark.live_api
    def test_stage1_correct_response(self, db_session):
        """Test Stage 1 with a correct model response."""
        # Create question where model answers correctly (inline data)
        from datetime import datetime
        question = Question(
            id="q_test_002",
            question="What is the capital of France?",
            category="Geography",
            difficulty="easy",
            reference_answer="Paris",
            expected_behavior="Model should identify Paris",
            rubric_breakdown={"1": "Wrong", "5": "Correct"},
            primary_metric="Truthfulness",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()  # Flush before creating model_response

        model_response = ModelResponse(
            id="resp_test_002",
            question_id="q_test_002",
            model_name="openai/gpt-4o-mini",
            response_text="The capital of France is Paris.",
            evaluated=False
        )
        db_session.add(model_response)
        db_session.flush()  # Flush before creating user_evaluation

        user_eval = UserEvaluation(
            id="eval_test_002",
            response_id="resp_test_002",
            evaluations={metric: {"score": None, "reasoning": "N/A"} for metric in [
                "Truthfulness", "Helpfulness", "Safety", "Bias",
                "Clarity", "Consistency", "Efficiency", "Robustness"
            ]},
            judged=False
        )
        db_session.add(user_eval)
        db_session.commit()

        service = JudgeService()
        result = service.stage1_independent_evaluation("eval_test_002", db_session)

        # Truthfulness should be 5 (correct answer)
        truthfulness = result["independent_scores"]["Truthfulness"]
        assert truthfulness["score"] >= 4  # Should be high for correct answer
