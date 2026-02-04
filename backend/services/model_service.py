"""
MentorMind - Model Service (K Models)

This module handles communication with K models via OpenRouter.
OpenRouter provides a unified API gateway to access multiple LLM providers.

Usage:
    from backend.services.model_service import ModelService, model_service
    response = model_service.answer_question("q_123", "openai/gpt-3.5-turbo", db)
"""

import logging
import random
import secrets
import time
from datetime import datetime

import openai
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.models.model_response import ModelResponse, K_MODELS
from backend.models.question import Question
from backend.services.llm_logger import log_llm_call

logger = logging.getLogger(__name__)


# =====================================================
# Model Service Class
# =====================================================

class ModelService:
    """
    Service for K model interactions via OpenRouter.

    Handles:
    - Model selection (ensuring all 6 models answer questions)
    - OpenRouter API calls (unified interface)
    - Response creation and storage
    - Error handling and logging
    """

    def __init__(self, api_key: str | None = None, timeout: int = 30):
        """
        Initialize Model service.

        Args:
            api_key: OpenRouter API key (defaults to settings.openrouter_api_key)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key or settings.openrouter_api_key
        self.timeout = timeout

        # Initialize OpenAI client with OpenRouter base URL
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=settings.openrouter_base_url,
            timeout=timeout
        )

        logger.info(f"ModelService initialized with timeout={timeout}s")

    # =====================================================
    # Model Selection
    # =====================================================

    def select_model(self, question_id: str, db: Session) -> str:
        """
        Select a K model that hasn't answered this question yet.

        Selection priority:
        1. Models that haven't answered this question (random from unanswered)
        2. If all answered, random selection from all models
        3. Models with fewer responses get priority (implicit in unanswered)

        Args:
            question_id: Question ID to check
            db: Database session

        Returns:
            Selected model name (e.g., "openai/gpt-3.5-turbo")

        Raises:
            ValueError: If question not found
        """
        # Verify question exists
        question = db.query(Question).filter(
            Question.id == question_id
        ).first()

        if not question:
            raise ValueError(f"Question not found: {question_id}")

        # Get existing responses for this question
        existing = db.query(ModelResponse).filter(
            ModelResponse.question_id == question_id
        ).all()

        answered_models = {r.model_name for r in existing}
        unanswered = [m for m in K_MODELS if m not in answered_models]

        if unanswered:
            # Random selection from unanswered models
            selected = random.choice(unanswered)
            logger.info(
                f"Selected unanswered model {selected} for question {question_id} "
                f"({len(unanswered)}/{len(K_MODELS)} remaining)"
            )
            return selected
        else:
            # All models answered - random selection
            selected = random.choice(K_MODELS)
            logger.info(
                f"All models answered question {question_id}, "
                f"randomly selected {selected}"
            )
            return selected

    # =====================================================
    # OpenRouter API Call
    # =====================================================

    def _call_openrouter(self, model_name: str, question: str) -> str:
        """
        Call OpenRouter API to get model response.

        Args:
            model_name: Model identifier (e.g., "openai/gpt-3.5-turbo")
            question: Question text

        Returns:
            Model's response text

        Raises:
            ValueError: If API call fails
        """
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You must respond in Turkish. All answers must be in Turkish language."},
                    {"role": "user", "content": question}
                ],
                timeout=self.timeout,
                extra_headers={
                    "HTTP-Referer": "https://github.com/yigitalp/MentorMind",
                    "X-Title": "MentorMind"
                }
            )

            duration = time.time() - start_time
            content = response.choices[0].message.content

            # Log LLM call (provider="openai" for OpenRouter since we use OpenAI client)
            log_llm_call(
                provider="openai",
                model=model_name,
                purpose="k_model_response",
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                duration_seconds=duration,
                success=True
            )

            return content

        except Exception as e:
            duration = time.time() - start_time
            log_llm_call(
                provider="openai",
                model=model_name,
                purpose="k_model_response",
                duration_seconds=duration,
                success=False,
                error=str(e)
            )
            raise ValueError(f"OpenRouter API call failed for {model_name}: {e}")

    # =====================================================
    # Question Answering (Unified Interface)
    # =====================================================

    def answer_question(
        self,
        question_id: str,
        model_name: str,
        db: Session
    ) -> ModelResponse:
        """
        Get a K model's response to a question.

        Process:
        1. Fetch question from database
        2. Validate model_name is in K_MODELS
        3. Call OpenRouter API
        4. Create ModelResponse object
        5. Save to database
        6. Return response

        Args:
            question_id: Question ID
            model_name: K model name (must be in K_MODELS)
            db: Database session

        Returns:
            Created ModelResponse object

        Raises:
            ValueError: If question not found, model invalid, or API call fails
        """
        # Validate model name
        if model_name not in K_MODELS:
            raise ValueError(
                f"Invalid model: {model_name}. Must be one of {K_MODELS}"
            )

        # Fetch question
        question = db.query(Question).filter(
            Question.id == question_id
        ).first()

        if not question:
            raise ValueError(f"Question not found: {question_id}")

        # Call OpenRouter
        try:
            response_text = self._call_openrouter(model_name, question.question)
        except ValueError as e:
            logger.error(f"Failed to get response from {model_name}: {e}")
            raise

        # Generate response ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hex = secrets.token_hex(3)
        response_id = f"resp_{timestamp}_{random_hex}"

        # Create ModelResponse
        model_response = ModelResponse(
            id=response_id,
            question_id=question_id,
            model_name=model_name,
            response_text=response_text,
            evaluated=False
        )

        db.add(model_response)
        db.commit()
        db.refresh(model_response)

        logger.info(
            f"Created model response: {response_id} for question={question_id}, "
            f"model={model_name}"
        )
        return model_response


# =====================================================
# Global Service Instance
# =====================================================

model_service = ModelService()


# =====================================================
# Convenience Functions
# =====================================================

def select_model(question_id: str, db: Session) -> str:
    """
    Select a K model using the global service instance.

    Args:
        question_id: Question ID
        db: Database session

    Returns:
        Selected model name
    """
    return model_service.select_model(question_id, db)


def answer_question(
    question_id: str,
    model_name: str,
    db: Session
) -> ModelResponse:
    """
    Get a K model's response using the global service instance.

    Args:
        question_id: Question ID
        model_name: K model name
        db: Database session

    Returns:
        Created ModelResponse object
    """
    return model_service.answer_question(question_id, model_name, db)
