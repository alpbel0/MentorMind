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
    JUDGE_PROMPTS, render_stage1_prompt, render_stage2_prompt,
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

        # Add header row (Markdown table format requires header)
        rows.append("| Metric | User Score | Judge Score | Gap | Verdict |")

        # Add separator row (Markdown table format requires separator after header)
        rows.append("|--------|------------|-------------|-----|---------|")

        # Add data rows for each metric
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
    # Stage 2: Mentoring Comparison (Task 4.7)
    # =====================================================

    def stage2_mentoring_comparison(
        self,
        user_eval_id: str,
        stage1_result: dict,
        vector_context: dict,
        db: Session
    ) -> dict:
        """
        Perform Stage 2: Mentoring comparison with feedback.

        Compares user's evaluation with judge's independent assessment,
        provides gap analysis, and generates mentoring feedback.

        Args:
            user_eval_id: User evaluation ID
            stage1_result: Result from Stage 1 (contains independent_scores)
            vector_context: ChromaDB past mistakes query result
            db: Database session

        Returns:
            {
                "alignment_analysis": {metric: {...}},
                "judge_meta_score": 4,
                "overall_feedback": "...",
                "improvement_areas": [...],
                "positive_feedback": [...],
                "primary_metric_gap": 1.0,
                "weighted_gap": 0.8
            }

        Raises:
            ValueError: If data invalid or missing
            RuntimeError: If GPT-4o API call fails
        """
        start_time = time.time()

        try:
            # 1. Fetch evaluation data
            data = self.fetch_evaluation_data(user_eval_id, db)
            user_scores = data["user_scores"]
            question = data["question"]

            # 2. Extract judge scores from Stage 1 result
            judge_scores = stage1_result.get("independent_scores", {})
            if not judge_scores:
                raise ValueError("Stage 1 result missing independent_scores")

            # 3. Generate comparison table (Task 4.4 helper)
            comparison_table = self.generate_comparison_table(user_scores, judge_scores)

            # 4. Calculate weighted gap (Task 4.5 helper)
            bonus_metrics = question.bonus_metrics or []
            weighted_gap = self.calculate_weighted_gap(
                user_scores, judge_scores,
                primary_metric=question.primary_metric,
                bonus_metrics=bonus_metrics
            )

            # 5. Calculate primary metric gap (handle None scores)
            user_primary_score = user_scores.get(question.primary_metric, {}).get("score")
            judge_primary_score = judge_scores.get(question.primary_metric, {}).get("score")
            
            if user_primary_score is not None and judge_primary_score is not None:
                primary_gap = abs(user_primary_score - judge_primary_score)
            else:
                primary_gap = 0.0  # If either score is None, gap is 0

            # 6. Format past mistakes context
            past_mistakes = self._format_past_mistakes(vector_context)

            # 7. Render Stage 2 prompt
            system_prompt = JUDGE_PROMPTS["stage2"]["system_prompt"]
            user_prompt = render_stage2_prompt(
                user_scores=user_scores,
                judge_scores=judge_scores,
                comparison_table=comparison_table,
                primary_metric=question.primary_metric,
                bonus_metrics=bonus_metrics,
                past_mistakes=past_mistakes
            )

            # 8. Call GPT-4o
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
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
                    purpose="judge_stage2_comparison",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    duration_seconds=duration,
                    success=True
                )

                logger.info(
                    f"GPT-4o Stage 2 comparison completed for {user_eval_id} "
                    f"({total_tokens} tokens, {duration:.2f}s)"
                )

            except openai.APITimeoutError as e:
                duration = time.time() - start_time
                log_llm_call(
                    provider="openai",
                    model=self.model,
                    purpose="judge_stage2_comparison",
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
                    purpose="judge_stage2_comparison",
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
                    purpose="judge_stage2_comparison",
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
                    purpose="judge_stage2_comparison",
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
                    purpose="judge_stage2_comparison",
                    duration_seconds=duration,
                    success=False,
                    error=str(e)
                )
                raise RuntimeError(f"GPT-4o call failed: {e}")

            # 9. Parse and validate response
            try:
                result = self.parse_stage2_response(content)
            except ValueError as e:
                logger.error(f"Failed to parse Stage 2 response: {e}")
                logger.error(f"Response content: {content[:500]}...")
                raise

            # 10. Add calculated gaps (GPT-4o may not calculate them correctly)
            result["primary_metric_gap"] = primary_gap
            result["weighted_gap"] = weighted_gap

            logger.info(f"Stage 2 comparison successful: {user_eval_id}")
            return result

        except (ValueError, RuntimeError):
            raise
        except Exception as e:
            logger.error(f"Stage 2 comparison failed for {user_eval_id}: {e}")
            raise RuntimeError(f"Stage 2 comparison failed: {e}")

    def _format_past_mistakes(self, vector_context: dict) -> str:
        """
        Format ChromaDB results into readable text for Stage 2 prompt.

        Per user preference: Returns empty string if no past mistakes found
        (silently continues without special message).

        Args:
            vector_context: ChromaDB query result with "evaluations" array

        Returns:
            Formatted text string (empty if no evaluations found)
        """
        evaluations = vector_context.get("evaluations", [])
        if not evaluations:
            return ""  # Empty context per user preference

        lines = ["Önceki benzer değerlendirmelerinizden dikkate değer kalıplar:"]
        for i, eval_data in enumerate(evaluations[:3], 1):
            lines.append(f"{i}. Meta Skor: {eval_data.get('judge_meta_score', 'N/A')}/5")
            lines.append(f"   Birincil Metrik Farkı: {eval_data.get('primary_gap', 'N/A')}")
            feedback = eval_data.get('feedback', '')
            if feedback:
                # Truncate long feedback
                feedback_short = feedback[:100] + "..." if len(feedback) > 100 else feedback
                lines.append(f"   Geri Bildirim: {feedback_short}")
            lines.append("")  # Blank line between entries

        return "\n".join(lines)

    def parse_stage2_response(self, response: str) -> dict:
        """
        Parse GPT-4o Stage 2 response into structured data.

        Handles multiple JSON formats:
        - Direct JSON: {"alignment_analysis": {...}}
        - Markdown code block: ```json\n{...}\n```
        - JSON with extra text before/after

        Args:
            response: Raw response string from GPT-4o

        Returns:
            {
                "alignment_analysis": {metric: {...}},
                "judge_meta_score": 4,
                "overall_feedback": "...",
                "improvement_areas": [...],
                "positive_feedback": [...]
            }

        Raises:
            ValueError: If JSON is invalid or missing required fields
        """
        # Try to extract JSON from response
        json_content = response.strip()

        # Pattern 1: Try direct JSON parsing first
        try:
            parsed = json.loads(json_content)
            if "alignment_analysis" in parsed:
                return self._validate_stage2_response(parsed)
        except json.JSONDecodeError:
            pass

        # Pattern 2: Markdown code block with json language tag
        code_block_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(code_block_pattern, json_content, re.DOTALL)
        if match:
            json_content = match.group(1)
        else:
            # Pattern 3: Generic code block
            generic_block_pattern = r'```\s*(.*?)\s*```'
            match = re.search(generic_block_pattern, json_content, re.DOTALL)
            if match:
                json_content = match.group(1)
            else:
                # Pattern 4: Find first { ... } block by counting braces
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
                        raise ValueError("Could not extract JSON from Stage 2 response")

        # Parse JSON
        try:
            parsed = json.loads(json_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Stage 2 JSON: {e}")
            logger.error(f"Content: {json_content[:500]}...")
            raise ValueError(f"Invalid JSON in Stage 2 response: {e}")

        return self._validate_stage2_response(parsed)

    def _validate_stage2_response(self, parsed: dict) -> dict:
        """
        Validate the structure of the parsed Stage 2 response.

        Args:
            parsed: Parsed JSON dictionary

        Returns:
            The validated dictionary

        Raises:
            ValueError: If structure is invalid
        """
        # Validate structure
        if not isinstance(parsed, dict):
            raise ValueError(f"Stage 2 response must be object, got {type(parsed)}")

        # Required fields
        required_fields = [
            "alignment_analysis",
            "judge_meta_score",
            "overall_feedback",
            "improvement_areas",
            "positive_feedback"
        ]

        for field in required_fields:
            if field not in parsed:
                raise ValueError(f"Stage 2 response missing '{field}' key")

        alignment_analysis = parsed["alignment_analysis"]

        if not isinstance(alignment_analysis, dict):
            raise ValueError("'alignment_analysis' must be object")

        # Validate all 8 metrics present
        if not all(metric in alignment_analysis for metric in THE_EIGHT_METRICS):
            missing = set(THE_EIGHT_METRICS) - set(alignment_analysis.keys())
            raise ValueError(f"Stage 2 alignment_analysis missing metrics: {missing}")

        # Validate each metric has required fields
        for metric, data in alignment_analysis.items():
            if not isinstance(data, dict):
                raise ValueError(f"Metric {metric} data must be object")

            required_metric_fields = ["user_score", "judge_score", "gap", "verdict", "feedback"]
            for field in required_metric_fields:
                if field not in data:
                    raise ValueError(f"Metric {metric} missing '{field}'")

            # Validate verdict is one of the allowed values
            verdict = data["verdict"]
            valid_verdicts = JUDGE_STAGE1_VERDICTS
            if verdict not in valid_verdicts:
                raise ValueError(f"Metric {metric} has invalid verdict: {verdict}")

        # Validate judge_meta_score
        meta_score = parsed["judge_meta_score"]
        if not isinstance(meta_score, int):
            raise ValueError(f"judge_meta_score must be int, got {type(meta_score)}")
        if not (1 <= meta_score <= 5):
            raise ValueError(f"judge_meta_score must be 1-5, got {meta_score}")

        # Validate feedback arrays
        if not isinstance(parsed["improvement_areas"], list):
            raise ValueError("improvement_areas must be array")

        if not isinstance(parsed["positive_feedback"], list):
            raise ValueError("positive_feedback must be array")

        return parsed

    # =====================================================
    # Full Flow Orchestration (Task 4.8)
    # =====================================================

    def full_judge_evaluation(
        self,
        user_eval_id: str,
        db: Session
    ) -> str:
        """
        Run complete two-stage judge evaluation workflow.

        Orchestrates: Stage 1 → ChromaDB Query → Stage 2 → Database Save → ChromaDB Add

        Args:
            user_eval_id: User evaluation ID (e.g., "eval_20250126_143000_aaa111")
            db: Database session

        Returns:
            judge_eval_id: ID of created JudgeEvaluation record

        Raises:
            ValueError: If evaluation data not found or invalid
            RuntimeError: If API calls or database operations fail
        """
        from backend.models.judge_evaluation import JudgeEvaluation
        from backend.models.user_evaluation import UserEvaluation
        from backend.services.chromadb_service import chromadb_service
        import secrets

        try:
            # 1. Fetch evaluation data
            data = self.fetch_evaluation_data(user_eval_id, db)
            question = data["question"]
            primary_metric = question.primary_metric
            category = question.category
            bonus_metrics = question.bonus_metrics or []

            # 2. Run Stage 1: Independent Evaluation
            logger.info(f"Starting Stage 1 for {user_eval_id}")
            stage1_result = self.stage1_independent_evaluation(user_eval_id, db)

            # 3. Query ChromaDB for past mistakes
            logger.info(f"Querying ChromaDB for {primary_metric} in {category}")
            try:
                vector_context = chromadb_service.query_past_mistakes(
                    primary_metric=primary_metric,
                    category=category,
                    n=5
                )
            except RuntimeError as e:
                # ChromaDB query error - log warning and continue with empty context
                logger.warning(f"ChromaDB query failed, using empty context: {e}")
                vector_context = {"evaluations": []}

            # 4. Run Stage 2: Mentoring Comparison
            logger.info(f"Starting Stage 2 for {user_eval_id}")
            stage2_result = self.stage2_mentoring_comparison(
                user_eval_id=user_eval_id,
                stage1_result=stage1_result,
                vector_context=vector_context,
                db=db
            )

            # 5. Generate judge_eval_id
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            random_hex = secrets.token_hex(6)
            judge_eval_id = f"judge_{timestamp}_{random_hex}"

            # 6. Create JudgeEvaluation record
            judge_eval = JudgeEvaluation(
                id=judge_eval_id,
                user_evaluation_id=user_eval_id,
                independent_scores=stage1_result["independent_scores"],
                alignment_analysis=stage2_result["alignment_analysis"],
                judge_meta_score=stage2_result["judge_meta_score"],
                overall_feedback=stage2_result["overall_feedback"],
                improvement_areas=stage2_result["improvement_areas"],
                positive_feedback=stage2_result["positive_feedback"],
                vector_context=vector_context if vector_context.get("evaluations") else None,
                primary_metric=primary_metric,
                primary_metric_gap=stage2_result["primary_metric_gap"],
                weighted_gap=stage2_result["weighted_gap"]
            )

            # 7. Save to database with transaction
            try:
                db.add(judge_eval)

                # Update UserEvaluation.judged = TRUE
                user_eval = db.query(UserEvaluation).filter_by(id=user_eval_id).first()
                if user_eval:
                    user_eval.judged = True
                else:
                    raise ValueError(f"User evaluation not found: {user_eval_id}")

                db.commit()
                logger.info(f"Judge evaluation saved: {judge_eval_id}")

            except Exception as e:
                db.rollback()
                logger.error(f"Failed to save judge evaluation: {e}")
                raise RuntimeError(f"Database save failed: {e}")

            # 8. Add to ChromaDB memory (log-only on failure per user preference)
            try:
                chromadb_service.add_to_memory(
                    db_session=db,
                    user_eval_id=user_eval_id,
                    judge_eval_id=judge_eval_id
                )
                logger.info(f"Added to ChromaDB memory: {user_eval_id}")
            except Exception as e:
                # Non-fatal - log only, don't fail the evaluation
                logger.warning(f"ChromaDB add failed (non-fatal): {e}")

            logger.info(f"Full judge evaluation completed: {judge_eval_id}")
            return judge_eval_id

        except (ValueError, RuntimeError):
            raise
        except Exception as e:
            logger.error(f"Full judge evaluation failed for {user_eval_id}: {e}")
            raise RuntimeError(f"Full judge evaluation failed: {e}")


# =====================================================
# Global Service Instance
# =====================================================

judge_service = JudgeService()
