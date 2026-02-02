"""
MentorMind - Judge Service (GPT-4o)

This module handles communication with OpenAI's GPT-4o API
for the two-stage judge evaluation workflow.

Usage:
    from backend.services.judge_service import JudgeService, judge_service
    result = judge_service.stage1_independent_evaluation("eval_123", db)
"""

import json
import logging
import re
import time
from typing import Any

import openai
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.models.question import Question
from backend.models.user_evaluation import UserEvaluation
from backend.models.model_response import ModelResponse
from backend.prompts.judge_prompts import (
    JUDGE_PROMPTS, render_stage1_prompt,
    JUDGE_STAGE1_VERDICTS, WEIGHTED_GAP_WEIGHTS, META_SCORE_THRESHOLDS
)
from backend.services.llm_logger import log_llm_call, LLMProvider

logger = logging.getLogger(__name__)

# The 8 evaluation metrics (constant)
THE_EIGHT_METRICS = [
    "Truthfulness", "Helpfulness", "Safety", "Bias",
    "Clarity", "Consistency", "Efficiency", "Robustness"
]


# =====================================================
# Judge Service Class
# =====================================================

class JudgeService:
    """
    Service for GPT-4o judge evaluation.

    Handles:
    - OpenAI client initialization (GPT-4o)
    - Data fetching (3-table join)
    - Stage 1 independent evaluation
    - Response parsing
    - Error handling and logging
    """

    def __init__(self, api_key: str | None = None, timeout: int = 60):
        """
        Initialize Judge service.

        Args:
            api_key: OpenAI API key (defaults to settings.openai_api_key)
            timeout: Request timeout in seconds (default: 60)
        """
        self.api_key = api_key or settings.openai_api_key
        self.timeout = timeout
        self.model = settings.judge_model  # "gpt-4o"

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)

        logger.info(f"JudgeService initialized with model={self.model}, timeout={timeout}s")

    # =====================================================
    # Public API
    # =====================================================

    def stage1_independent_evaluation(self, user_eval_id: str, db: Session) -> dict:
        """
        Perform Stage 1: Independent blind evaluation.

        Args:
            user_eval_id: User evaluation ID (e.g., "eval_20250126_143000_aaa111")
            db: Database session

        Returns:
            {
                "independent_scores": {
                    "Truthfulness": {"score": 3, "rationale": "..."},
                    ... (all 8 metrics)
                }
            }

        Raises:
            ValueError: If evaluation data not found or invalid
            RuntimeError: If GPT-4o API call fails
        """
        start_time = time.time()

        try:
            # 1. Fetch evaluation data
            data = self.fetch_evaluation_data(user_eval_id, db)
            question = data["question"]
            model_response = data["model_response"]

            # 2. Render prompt
            # NOTE: render_stage1_prompt() returns ONLY user_prompt (str)
            # System prompt is fetched from JUDGE_PROMPTS dictionary
            system_prompt = JUDGE_PROMPTS["stage1"]["system_prompt"]
            user_prompt = render_stage1_prompt(
                question=question.question,
                model_name=model_response.model_name,
                model_response=model_response.response_text,
                reference_answer=question.reference_answer or "Belirtilmemiş",
                expected_behavior=question.expected_behavior or "Belirtilmemiş",
                primary_metric=question.primary_metric,
                rubric_breakdown=question.rubric_breakdown
            )

            # 3. Call GPT-4o
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,  # Lower for more consistent evaluation
                    timeout=self.timeout
                )

                duration = time.time() - start_time
                content = response.choices[0].message.content

                # Extract token usage
                usage = response.usage
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens

                # Log LLM call
                log_llm_call(
                    provider="openai",
                    model=self.model,
                    purpose="judge_stage1_evaluation",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    duration_seconds=duration,
                    success=True
                )

                logger.info(
                    f"GPT-4o Stage 1 evaluation completed for {user_eval_id} "
                    f"({total_tokens} tokens, {duration:.2f}s)"
                )

            except openai.APITimeoutError as e:
                duration = time.time() - start_time
                log_llm_call(
                    provider="openai",
                    model=self.model,
                    purpose="judge_stage1_evaluation",
                    duration_seconds=duration,
                    success=False,
                    error=f"Timeout: {e}"
                )
                raise RuntimeError(f"GPT-4o API timeout after {self.timeout}s: {e}")

            except openai.RateLimitError as e:
                duration = time.time() - start_time
                log_llm_call(
                    provider="openai",
                    model=self.model,
                    purpose="judge_stage1_evaluation",
                    duration_seconds=duration,
                    success=False,
                    error=f"Rate limit: {e}"
                )
                raise RuntimeError(f"GPT-4o API rate limit exceeded: {e}")

            except openai.APIConnectionError as e:
                duration = time.time() - start_time
                log_llm_call(
                    provider="openai",
                    model=self.model,
                    purpose="judge_stage1_evaluation",
                    duration_seconds=duration,
                    success=False,
                    error=f"Connection error: {e}"
                )
                raise RuntimeError(f"GPT-4o API connection failed: {e}")

            except openai.APIError as e:
                duration = time.time() - start_time
                log_llm_call(
                    provider="openai",
                    model=self.model,
                    purpose="judge_stage1_evaluation",
                    duration_seconds=duration,
                    success=False,
                    error=str(e)
                )
                raise RuntimeError(f"GPT-4o API error: {e}")

            except Exception as e:
                duration = time.time() - start_time
                log_llm_call(
                    provider="openai",
                    model=self.model,
                    purpose="judge_stage1_evaluation",
                    duration_seconds=duration,
                    success=False,
                    error=str(e)
                )
                raise RuntimeError(f"GPT-4o call failed: {e}")

            # 4. Parse response
            try:
                result = self.parse_judge_response(content)
            except ValueError as e:
                logger.error(f"Failed to parse GPT-4o response: {e}")
                logger.error(f"Response content: {content[:500]}...")
                raise

            # 5. Validate 8 metrics
            independent_scores = result.get("independent_scores", {})

            if not all(metric in independent_scores for metric in THE_EIGHT_METRICS):
                missing = set(THE_EIGHT_METRICS) - set(independent_scores.keys())
                raise ValueError(f"GPT-4o response missing metrics: {missing}")

            # Validate each metric has score + rationale
            for metric, data in independent_scores.items():
                if "score" not in data:
                    raise ValueError(f"Metric {metric} missing score")
                if "rationale" not in data:
                    raise ValueError(f"Metric {metric} missing rationale")

                score = data["score"]
                if score is not None and not isinstance(score, int):
                    raise ValueError(f"Metric {metric} score must be int or null, got {type(score)}")
                if score is not None and not (1 <= score <= 5):
                    raise ValueError(f"Metric {metric} score must be 1-5 or null, got {score}")

            logger.info(f"Stage 1 evaluation successful: {user_eval_id}")
            return result

        except (ValueError, RuntimeError):
            raise
        except Exception as e:
            logger.error(f"Stage 1 evaluation failed for {user_eval_id}: {e}")
            raise RuntimeError(f"Stage 1 evaluation failed: {e}")

    def fetch_evaluation_data(self, user_eval_id: str, db: Session) -> dict:
        """
        Fetch all data needed for evaluation.

        Performs 3-table join: user_evaluations → model_responses → questions

        Args:
            user_eval_id: User evaluation ID
            db: Database session

        Returns:
            {
                "user_eval": UserEvaluation object,
                "model_response": ModelResponse object,
                "question": Question object,
                "user_scores": dict (8 metrics with score + reasoning)
            }

        Raises:
            ValueError: If any data not found or invalid
        """
        # 1. Fetch user evaluation
        user_eval = db.query(UserEvaluation).filter(
            UserEvaluation.id == user_eval_id
        ).first()

        if not user_eval:
            raise ValueError(f"User evaluation not found: {user_eval_id}")

        # 2. Fetch model response
        model_response = db.query(ModelResponse).filter(
            ModelResponse.id == user_eval.response_id
        ).first()

        if not model_response:
            raise ValueError(f"Model response not found: {user_eval.response_id}")

        # 3. Fetch question
        question = db.query(Question).filter(
            Question.id == model_response.question_id
        ).first()

        if not question:
            raise ValueError(f"Question not found: {model_response.question_id}")

        # 4. Extract user scores from JSONB
        user_scores = user_eval.evaluations  # Already a dict

        # Validate user_scores has 8 metrics
        if not all(metric in user_scores for metric in THE_EIGHT_METRICS):
            missing = set(THE_EIGHT_METRICS) - set(user_scores.keys())
            raise ValueError(f"User evaluation missing metrics: {missing}")

        return {
            "user_eval": user_eval,
            "model_response": model_response,
            "question": question,
            "user_scores": user_scores
        }

    def parse_judge_response(self, response: str) -> dict:
        """
        Parse GPT-4o response into structured data.

        Handles multiple JSON formats:
        - Direct JSON: {"independent_scores": {...}}
        - Markdown code block: ```json\n{...}\n```
        - JSON with extra text before/after

        Args:
            response: Raw response string from GPT-4o

        Returns:
            {"independent_scores": {metric: {"score": int, "rationale": str}}}

        Raises:
            ValueError: If JSON is invalid or missing required fields
        """
        # Try to extract JSON from response
        json_content = response.strip()

        # Pattern 1: Try direct JSON parsing first
        try:
            parsed = json.loads(json_content)
            # If it worked, validate and return
            if "independent_scores" in parsed:
                return self._validate_judge_response(parsed)
        except json.JSONDecodeError:
            # Not direct JSON, continue to extraction patterns
            pass

        # Pattern 2: Markdown code block with json language tag
        # ```json\n{...}\n```
        code_block_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(code_block_pattern, json_content, re.DOTALL)
        if match:
            json_content = match.group(1)
        else:
            # Pattern 3: Generic code block
            # ```\n{...}\n```
            generic_block_pattern = r'```\s*(.*?)\s*```'
            match = re.search(generic_block_pattern, json_content, re.DOTALL)
            if match:
                json_content = match.group(1)
            else:
                # Pattern 4: Find first { ... } block by counting braces
                # This handles nested braces better than regex
                start_idx = json_content.find('{')
                if start_idx != -1:
                    brace_count = 0
                    in_string = False
                    escape_next = False
                    for i, char in enumerate(json_content[start_idx:], start=start_idx):
                        if escape_next:
                            escape_next = False
                            continue
                        if char == '\\':
                            escape_next = True
                            continue
                        if char == '"' and not escape_next:
                            in_string = not in_string
                            continue
                        if not in_string:
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    json_content = json_content[start_idx:i+1]
                                    break
                    else:
                        # Couldn't find matching braces
                        raise ValueError("Could not extract JSON from response")

        # Parse JSON
        try:
            parsed = json.loads(json_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Content: {json_content[:500]}...")
            raise ValueError(f"Invalid JSON in GPT-4o response: {e}")

        return self._validate_judge_response(parsed)

    def _validate_judge_response(self, parsed: dict) -> dict:
        """
        Validate the structure of the parsed judge response.

        Args:
            parsed: Parsed JSON dictionary

        Returns:
            The validated dictionary

        Raises:
            ValueError: If structure is invalid
        """
        # Validate structure
        if not isinstance(parsed, dict):
            raise ValueError(f"GPT-4o response must be object, got {type(parsed)}")

        if "independent_scores" not in parsed:
            raise ValueError("GPT-4o response missing 'independent_scores' key")

        independent_scores = parsed["independent_scores"]

        if not isinstance(independent_scores, dict):
            raise ValueError("'independent_scores' must be object")

        return parsed

    # =====================================================
    # Stage 2 Helper Functions (Tasks 4.4, 4.5 & 4.6)
    # =====================================================

    def generate_comparison_table(
        self,
        user_scores: dict[str, dict[str, Any]],
        judge_scores: dict[str, dict[str, Any]]
    ) -> str:
        """
        Generate markdown comparison table for Stage 2 prompt.

        Creates a table showing user scores, judge scores, gaps, and verdicts
        for all 8 metrics. This table is included in the Stage 2 prompt to
        help GPT-4o provide targeted feedback.

        Args:
            user_scores: User's evaluation scores
                {"Truthfulness": {"score": 3, "reasoning": "..."}, ...}
            judge_scores: Judge's independent scores
                {"Truthfulness": {"score": 4, "rationale": "..."}, ...}

        Returns:
            Markdown table string with rows for each metric.

        Example:
            "| Metric | User Score | Judge Score | Gap | Verdict |"
            "|--------|------------|-------------|-----|---------|"
            "| Truthfulness | 4 | 3 | 1 | slightly_over_estimated |"
        """
        rows = []

        for metric in THE_EIGHT_METRICS:
            user_data = user_scores.get(metric, {})
            judge_data = judge_scores.get(metric, {})

            user_score = user_data.get("score")
            judge_score = judge_data.get("score")

            # Handle null scores
            if user_score is None or judge_score is None:
                gap = 0
                verdict = "not_applicable"
                user_display = "N/A"
                judge_display = "N/A" if judge_score is None else str(judge_score)
            else:
                gap = abs(user_score - judge_score)
                user_display = str(user_score)
                judge_display = str(judge_score)

                # Determine verdict based on gap and direction
                if gap == 0:
                    verdict = "aligned"
                elif gap == 1:
                    verdict = "slightly_over_estimated" if user_score > judge_score else "slightly_under_estimated"
                elif gap == 2:
                    verdict = "moderately_over_estimated" if user_score > judge_score else "moderately_under_estimated"
                else:  # gap >= 3
                    verdict = "significantly_over_estimated" if user_score > judge_score else "significantly_under_estimated"

            # Format as markdown table row
            row = f"| {metric} | {user_display} | {judge_display} | {gap} | {verdict} |"
            rows.append(row)

        # Join with newlines
        return "\n".join(rows)

    def calculate_weighted_gap(
        self,
        user_scores: dict[str, dict[str, Any]],
        judge_scores: dict[str, dict[str, Any]],
        primary_metric: str,
        bonus_metrics: list[str]
    ) -> float:
        """
        Calculate weighted gap for meta score computation.

        The weighted gap formula prioritizes alignment on the primary metric
        (what the user is training on) while considering bonus and other metrics.

        Formula:
            weighted_gap = (primary_gap * 0.7) + (bonus_avg * 0.2) + (other_avg * 0.1)

        Args:
            user_scores: User's evaluation scores
            judge_scores: Judge's independent scores
            primary_metric: The metric being tested (e.g., "Truthfulness")
            bonus_metrics: List of 2 bonus metrics (hidden from user)

        Returns:
            Weighted gap as float (0-5 scale)

        Example:
            user_scores = {"Truthfulness": {"score": 4}, ...}
            judge_scores = {"Truthfulness": {"score": 3}, ...}
            primary_metric = "Truthfulness"
            bonus_metrics = ["Clarity", "Safety"]
            -> Returns 0.7 (primary gap=1, bonus avg=0.5, other avg=0.5)
        """
        # Calculate gaps for all metrics (only where both scores exist)
        gaps = {}

        for metric in THE_EIGHT_METRICS:
            user_score = user_scores.get(metric, {}).get("score")
            judge_score = judge_scores.get(metric, {}).get("score")

            if user_score is not None and judge_score is not None:
                gaps[metric] = abs(user_score - judge_score)

        # Extract primary gap
        primary_gap = gaps.get(primary_metric, 0.0)

        # Calculate bonus average
        bonus_gaps = [gaps.get(m, 0.0) for m in bonus_metrics]
        bonus_avg = sum(bonus_gaps) / len(bonus_gaps) if bonus_gaps else 0.0

        # Calculate other average (remaining metrics)
        other_metrics = set(THE_EIGHT_METRICS) - {primary_metric} - set(bonus_metrics)
        other_gaps = [gaps.get(m, 0.0) for m in other_metrics]
        other_avg = sum(other_gaps) / len(other_gaps) if other_gaps else 0.0

        # Apply weights
        weights = WEIGHTED_GAP_WEIGHTS
        weighted_gap = (primary_gap * weights["primary"] +
                        bonus_avg * weights["bonus"] +
                        other_avg * weights["other"])

        # Round to 2 decimal places for consistency
        return round(weighted_gap, 2)

    @staticmethod
    def weighted_gap_to_meta_score(weighted_gap: float) -> int:
        """
        Map weighted gap to meta score (1-5).

        The meta score represents the user's overall evaluation quality.
        Lower gap = better alignment = higher meta score.

        Args:
            weighted_gap: Calculated weighted gap (0-5 scale)

        Returns:
            Meta score as integer (1-5)

        Mapping:
            gap <= 0.5 -> 5 (Excellent alignment)
            gap <= 1.0 -> 4 (Good alignment)
            gap <= 1.5 -> 3 (Moderate alignment)
            gap <= 2.0 -> 2 (Poor alignment)
            gap > 2.0  -> 1 (Very poor alignment)
        """
        # Check thresholds in descending order
        if weighted_gap <= META_SCORE_THRESHOLDS[5]:
            return 5
        elif weighted_gap <= META_SCORE_THRESHOLDS[4]:
            return 4
        elif weighted_gap <= META_SCORE_THRESHOLDS[3]:
            return 3
        elif weighted_gap <= META_SCORE_THRESHOLDS[2]:
            return 2
        else:
            return 1


# =====================================================
# Global Service Instance
# =====================================================

judge_service = JudgeService()
