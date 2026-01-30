"""
MentorMind - Claude AI Service

This module handles communication with Anthropic's Claude API
for generating evaluation questions.

Usage:
    from backend.services.claude_service import ClaudeService, claude_service
    question_data = claude_service.generate_question("Truthfulness", use_pool=False)
"""

import logging
import random
import secrets
import time
from datetime import datetime
from typing import Any

import anthropic
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.models.database import SessionLocal
from backend.models.question import Question
from backend.models.question_prompt import QuestionPrompt
from backend.prompts.master_prompts import (
    get_golden_example,
    get_question_type_description,
    get_question_types,
    render_user_prompt,
    validate_metric,
)
from backend.services.llm_logger import log_llm_call, LLMProvider

logger = logging.getLogger(__name__)


# =====================================================
# Category Pool (18 categories for 'any' selection)
# =====================================================

DEFAULT_CATEGORY_POOL = [
    # Academic & Educational
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "History",
    "Literature",
    "Philosophy",
    # Technology & Computing
    "Programming",
    "Data Science",
    "Artificial Intelligence",
    "Web Development",
    "Cybersecurity",
    # Professional & Practical
    "Business",
    "Finance",
    "Medicine",
    "Law",
    "Marketing",
    # Arts & Culture
    "Art",
    "Music",
    "Film",
    "Design"
]

# Map legacy categories to pool
LEGACY_CATEGORY_MAP = {
    "Math": "Mathematics",
    "Coding": "Programming",
    "Medical": "Medicine",
    "General": "Business"
}


# =====================================================
# Claude Service Class
# =====================================================

class ClaudeService:
    """
    Service for interacting with Claude AI API.

    Handles:
    - Anthropic client initialization
    - Question generation from prompts
    - Category selection logic
    - Error handling and logging
    """

    def __init__(self, api_key: str | None = None, timeout: int = 30):
        """
        Initialize Claude service.

        Args:
            api_key: Anthropic API key (defaults to settings.anthropic_api_key)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.timeout = timeout
        self.model = settings.claude_question_model

        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)

        logger.info(f"ClaudeService initialized with model={self.model}, timeout={timeout}s")

    # =====================================================
    # Category Selection
    # =====================================================

    def select_category(self, category_hints: list[str]) -> str:
        """
        Select a category based on hints.

        Selection logic:
        - If category_hints contains specific categories (not ["any"]),
          randomly select one from the hints
        - If category_hints is ["any"] or empty, randomly select from
          DEFAULT_CATEGORY_POOL

        Args:
            category_hints: List of category hints from database

        Returns:
            Selected category string

        Examples:
            >>> select_category(["React", "SQL"])
            "React"  # or "SQL" (random)
            >>> select_category(["any"])
            "Mathematics"  # random from DEFAULT_CATEGORY_POOL
            >>> select_category([])
            "Programming"  # random from DEFAULT_CATEGORY_POOL
        """
        if not category_hints or category_hints == ["any"]:
            # Random selection from DEFAULT_CATEGORY_POOL
            return random.choice(DEFAULT_CATEGORY_POOL)

        # Map legacy categories if needed
        mapped_hints = []
        for hint in category_hints:
            mapped = LEGACY_CATEGORY_MAP.get(hint, hint)
            mapped_hints.append(mapped)

        # Random selection from provided hints
        return random.choice(mapped_hints)

    # =====================================================
    # Question Generation (Pool Selection)
    # =====================================================

    def _select_from_pool(self, primary_metric: str, db: Session) -> Question:
        """
        Select an existing question from the pool.

        Selection criteria:
        - Filter by primary_metric
        - Order by times_used ASC (least used first)
        - If tie, random among those with same times_used

        Args:
            primary_metric: The metric to filter by
            db: Database session

        Returns:
            Question object from pool

        Raises:
            ValueError: If no questions found for metric
        """
        question = db.query(Question).filter(
            Question.primary_metric == primary_metric
        ).order_by(
            Question.times_used.asc(),
            Question.created_at.desc()  # Newer questions first for ties
        ).first()

        if not question:
            raise ValueError(f"No questions found in pool for metric: {primary_metric}")

        # Update usage tracking
        question.times_used += 1
        now = datetime.now()
        if question.first_used_at is None:
            question.first_used_at = now
        question.last_used_at = now
        db.commit()

        logger.info(f"Selected question from pool: {question.id} (times_used={question.times_used})")
        return question

    # =====================================================
    # Question Generation (New)
    # =====================================================

    def _generate_new_question(
        self,
        primary_metric: str,
        db: Session
    ) -> Question:
        """
        Generate a new question using Claude AI.

        Process:
        1. Select a random prompt for the metric
        2. Select a question_type for the metric
        3. Select a category
        4. Render the prompt
        5. Call Claude API
        6. Parse JSON response
        7. Create Question object
        8. Save to database

        Args:
            primary_metric: The metric to generate for
            db: Database session

        Returns:
            Newly created Question object

        Raises:
            ValueError: If metric is invalid or generation fails
        """
        if not validate_metric(primary_metric):
            raise ValueError(f"Invalid metric: {primary_metric}")

        # 1. Get available question types for this metric
        question_types = get_question_types(primary_metric)
        question_type = random.choice(question_types)

        # 2. Get prompt from database
        prompt = db.query(QuestionPrompt).filter(
            QuestionPrompt.primary_metric == primary_metric,
            QuestionPrompt.question_type == question_type
        ).first()

        # 3. Select category (use prompt's category_hints or default to ['any'])
        category_hints = prompt.category_hints if prompt else ["any"]
        category = self.select_category(category_hints)

        # 4. Select difficulty (use prompt's difficulty or default to 'medium')
        difficulty = prompt.difficulty if prompt else "medium"

        # 5. Render prompt
        rendered_prompt = render_user_prompt(
            primary_metric=primary_metric,
            question_type=question_type,
            category=category,
            difficulty=difficulty
        )

        # 6. Call Claude API
        start_time = time.time()
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": rendered_prompt
                    }
                ],
                timeout=self.timeout
            )

            # Extract content
            content = response.content[0].text
            duration = time.time() - start_time

            # Log LLM call
            log_llm_call(
                provider="anthropic",
                model=self.model,
                purpose="question_generation",
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                duration_seconds=duration,
                success=True
            )

        except Exception as e:
            duration = time.time() - start_time
            log_llm_call(
                provider="anthropic",
                model=self.model,
                purpose="question_generation",
                duration_seconds=duration,
                success=False,
                error=str(e)
            )
            raise ValueError(f"Claude API call failed: {e}")

        # 7. Parse JSON response
        question_data = self._parse_claude_response(content)

        # 8. Validate response structure
        required_fields = ["question", "reference_answer", "expected_behavior", "rubric_breakdown"]
        for field in required_fields:
            if field not in question_data:
                raise ValueError(f"Missing required field in Claude response: {field}")

        # 9. Validate rubric_breakdown has scores 1-5
        rubric = question_data["rubric_breakdown"]
        for score in ["1", "2", "3", "4", "5"]:
            if str(score) not in rubric:
                raise ValueError(f"Missing rubric score '{score}' in response")

        # 10. Generate Question ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hex = secrets.token_hex(3)
        question_id = f"q_{timestamp}_{random_hex}"

        # 11. Create Question object
        question = Question(
            id=question_id,
            question=question_data["question"],
            category=category,
            difficulty=difficulty,
            reference_answer=question_data["reference_answer"],
            expected_behavior=question_data["expected_behavior"],
            rubric_breakdown=question_data["rubric_breakdown"],
            primary_metric=primary_metric,
            bonus_metrics=prompt.bonus_metrics if prompt else [],
            question_prompt_id=prompt.id if prompt else None,
            times_used=0
        )

        # 12. Save to database
        db.add(question)
        db.commit()
        db.refresh(question)

        logger.info(f"Generated new question: {question_id} for metric={primary_metric}, type={question_type}")
        return question

    def _parse_claude_response(self, content: str) -> dict[str, Any]:
        """
        Parse Claude API response, handling various JSON formats.

        Args:
            content: Raw response content from Claude

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON parsing fails
        """
        # Try direct JSON parse
        try:
            return self._parse_json(content)
        except ValueError:
            pass

        # Try to extract JSON from markdown code block
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            if json_end > json_start:
                try:
                    return self._parse_json(content[json_start:json_end].strip())
                except ValueError:
                    pass
        elif "```" in content:
            json_start = content.find("```") + 3
            json_end = content.find("```", json_start)
            if json_end > json_start:
                try:
                    return self._parse_json(content[json_start:json_end].strip())
                except ValueError:
                    pass

        # If all attempts fail
        raise ValueError(f"Failed to parse Claude response as JSON: {content[:200]}")

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        """
        Parse text as JSON, raising ValueError if it fails.

        Args:
            text: Text to parse

        Returns:
            Parsed dictionary

        Raises:
            ValueError: If text is not valid JSON
        """
        import json
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    # =====================================================
    # Main Question Generation Function
    # =====================================================

    def generate_question(
        self,
        primary_metric: str,
        use_pool: bool = False,
        db: Session | None = None
    ) -> Question:
        """
        Generate or select a question for evaluation.

        Args:
            primary_metric: The metric to generate for (e.g., "Truthfulness")
            use_pool: If True, select from pool; if False, generate new
            db: Database session (optional, creates new if None)

        Returns:
            Question object

        Raises:
            ValueError: If metric is invalid or generation fails

        Examples:
            >>> claude_service.generate_question("Truthfulness", use_pool=False)
            <Question(id=q_20250130_143052_abc123, category=Mathematics...)>
            >>> claude_service.generate_question("Truthfulness", use_pool=True)
            <Question(id=q_20250129_120000_xyz789, category=Physics...)>
        """
        if db is None:
            db = SessionLocal()
            should_close_db = True
        else:
            should_close_db = False

        try:
            if use_pool:
                return self._select_from_pool(primary_metric, db)
            else:
                return self._generate_new_question(primary_metric, db)
        finally:
            # Only close if we created the session
            if should_close_db:
                db.close()


# =====================================================
# Global Service Instance
# =====================================================

claude_service = ClaudeService()


# =====================================================
# Convenience Functions
# =====================================================

def generate_question(
    primary_metric: str,
    use_pool: bool = False,
    db: Session | None = None
) -> Question:
    """
    Generate or select a question using the global service instance.

    Args:
        primary_metric: The metric to generate for
        use_pool: If True, select from pool; if False, generate new
        db: Database session (optional)

    Returns:
        Question object
    """
    return claude_service.generate_question(primary_metric, use_pool, db)


def select_category(category_hints: list[str]) -> str:
    """
    Select a category using the global service instance.

    Args:
        category_hints: List of category hints

    Returns:
        Selected category string
    """
    return claude_service.select_category(category_hints)
