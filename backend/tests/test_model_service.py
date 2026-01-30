"""
MentorMind - Model Service Tests

Tests for the K Model service that uses OpenRouter as a unified API gateway.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from backend.services.model_service import ModelService, model_service, K_MODELS
from backend.models.model_response import ModelResponse
from backend.models.question import Question


class TestModelService:
    """Test suite for ModelService class."""

    @pytest.fixture
    def service(self):
        """Create a ModelService instance for testing."""
        # Mock API key to avoid requiring real credentials
        with patch("backend.services.model_service.settings") as mock_settings:
            mock_settings.openrouter_api_key = "test-key"
            mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"
            return ModelService(api_key="test-key")

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        with patch("backend.services.model_service.openai.OpenAI") as mock:
            yield mock

    def test_service_initialization(self, service):
        """Test that ModelService initializes correctly."""
        assert service.api_key == "test-key"
        assert service.timeout == 30
        assert service.client is not None

    def test_select_model_no_existing_responses(self, db_session, service):
        """Test model selection when no models have answered yet."""
        # Create a test question
        question = Question(
            id="q_test_123",
            question="Test question?",
            category="Mathematics",
            difficulty="medium",
            reference_answer="Test answer",
            expected_behavior="Should answer",
            rubric_breakdown={"1": "Bad", "5": "Good"},
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity"],
            times_used=0
        )
        db_session.add(question)
        db_session.commit()

        # Select model - should return one of K_MODELS
        selected = service.select_model("q_test_123", db_session)
        assert selected in K_MODELS

    def test_select_model_some_answered(self, db_session, service):
        """Test model selection when some models have already answered."""
        # Create a test question
        question = Question(
            id="q_test_456",
            question="Test question 2?",
            category="Programming",
            difficulty="easy",
            reference_answer="Test answer 2",
            expected_behavior="Should answer 2",
            rubric_breakdown={"1": "Bad", "5": "Good"},
            primary_metric="Clarity",
            bonus_metrics=["Helpfulness"],
            times_used=0
        )
        db_session.add(question)
        db_session.commit()

        # Create responses for 2 of the 6 models (use unique IDs)
        for i, model in enumerate(K_MODELS[:2]):
            response = ModelResponse(
                id=f"resp_{i:02d}_456",
                question_id="q_test_456",
                model_name=model,
                response_text="Test response",
                evaluated=False
            )
            db_session.add(response)
        db_session.commit()

        # Select model - should return one of the 4 unanswered models
        selected = service.select_model("q_test_456", db_session)
        assert selected in K_MODELS[2:]  # Should be from unanswered

    def test_select_model_question_not_found(self, db_session, service):
        """Test model selection when question doesn't exist."""
        with pytest.raises(ValueError, match="Question not found"):
            service.select_model("q_nonexistent", db_session)

    def test_select_model_all_answered(self, db_session, service):
        """Test model selection when all models have answered."""
        # Create a test question
        question = Question(
            id="q_test_789",
            question="Test question 3?",
            category="Medicine",
            difficulty="hard",
            reference_answer="Test answer 3",
            expected_behavior="Should answer 3",
            rubric_breakdown={"1": "Bad", "5": "Good"},
            primary_metric="Safety",
            bonus_metrics=["Bias"],
            times_used=0
        )
        db_session.add(question)
        db_session.commit()

        # Create responses for all models (use unique IDs)
        for i, model in enumerate(K_MODELS):
            response = ModelResponse(
                id=f"resp_all_{i:02d}_789",
                question_id="q_test_789",
                model_name=model,
                response_text="Test response from all",
                evaluated=False
            )
            db_session.add(response)
        db_session.commit()

        # Select model - should still return a model (random selection)
        selected = service.select_model("q_test_789", db_session)
        assert selected in K_MODELS

    @patch("backend.services.model_service.log_llm_call")
    def test_call_openrouter_success(self, mock_log, service, mock_openai_client):
        """Test successful OpenRouter API call."""
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test model response"))]
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30

        mock_openai_client.return_value.chat.completions.create.return_value = mock_response

        # Create service with mocked client
        with patch.object(service, 'client', mock_openai_client.return_value):
            result = service._call_openrouter("openai/gpt-3.5-turbo", "Test question")

        assert result == "Test model response"
        mock_log.assert_called_once()

    @patch("backend.services.model_service.log_llm_call")
    def test_call_openrouter_failure(self, mock_log, service, mock_openai_client):
        """Test OpenRouter API call failure handling."""
        # Mock API error
        mock_openai_client.return_value.chat.completions.create.side_effect = Exception("API Error")

        # Create service with mocked client
        with patch.object(service, 'client', mock_openai_client.return_value):
            with pytest.raises(ValueError, match="OpenRouter API call failed"):
                service._call_openrouter("openai/gpt-3.5-turbo", "Test question")

        # Verify failure was logged
        mock_log.assert_called_once()
        call_args = mock_log.call_args
        assert call_args.kwargs["success"] is False
        assert "API Error" in call_args.kwargs["error"]

    @patch("backend.services.model_service.log_llm_call")
    def test_answer_question_success(self, mock_log, db_session, service, mock_openai_client):
        """Test successful question answering."""
        # Create a test question
        question = Question(
            id="q_test_answer",
            question="Test question for answer?",
            category="Business",
            difficulty="medium",
            reference_answer="Test reference",
            expected_behavior="Should behave",
            rubric_breakdown={"1": "Poor", "5": "Excellent"},
            primary_metric="Helpfulness",
            bonus_metrics=["Efficiency"],
            times_used=0
        )
        db_session.add(question)
        db_session.commit()

        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Model's answer here"))]
        mock_response.usage.prompt_tokens = 15
        mock_response.usage.completion_tokens = 25
        mock_response.usage.total_tokens = 40

        mock_openai_client.return_value.chat.completions.create.return_value = mock_response

        # Create service with mocked client
        with patch.object(service, 'client', mock_openai_client.return_value):
            result = service.answer_question(
                "q_test_answer",
                "openai/gpt-4o-mini",
                db_session
            )

        # Verify response
        assert isinstance(result, ModelResponse)
        assert result.question_id == "q_test_answer"
        assert result.model_name == "openai/gpt-4o-mini"
        assert result.response_text == "Model's answer here"
        assert result.evaluated is False
        assert result.id.startswith("resp_")

    def test_answer_question_invalid_model(self, db_session, service):
        """Test answer_question with invalid model name."""
        # Create a test question
        question = Question(
            id="q_test_invalid",
            question="Test?",
            category="General",
            difficulty="easy",
            reference_answer="Answer",
            expected_behavior="Behavior",
            rubric_breakdown={"1": "1", "5": "5"},
            primary_metric="Truthfulness",
            bonus_metrics=[],
            times_used=0
        )
        db_session.add(question)
        db_session.commit()

        with pytest.raises(ValueError, match="Invalid model"):
            service.answer_question("q_test_invalid", "invalid/model", db_session)

    def test_answer_question_not_found(self, db_session, service):
        """Test answer_question when question doesn't exist."""
        with pytest.raises(ValueError, match="Question not found"):
            service.answer_question("q_nonexistent", K_MODELS[0], db_session)

    def test_k_models_constant(self):
        """Test that K_MODELS constant has correct format."""
        assert len(K_MODELS) == 6
        assert all("/" in model for model in K_MODELS)  # Should have provider/model format
        assert "openai/gpt-3.5-turbo" in K_MODELS
        assert "mistralai/mistral-nemo" in K_MODELS
