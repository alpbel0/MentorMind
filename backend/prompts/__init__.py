"""
MentorMind - Prompt Templates Package

This package contains LLM prompt templates for:
- Question generation (master_prompts.py)
- Judge evaluation (judge_prompts.py)
"""

from backend.prompts.judge_prompts import (
    JUDGE_PROMPTS,
    JUDGE_STAGE1_VERDICTS,
    META_SCORE_THRESHOLDS,
    WEIGHTED_GAP_WEIGHTS,
    render_stage1_prompt,
    render_stage2_prompt,
)
from backend.prompts.master_prompts import (
    BONUS_METRIC_MAPPINGS,
    CATEGORIES,
    DIFFICULTIES,
    MASTER_PROMPTS,
    METRICS,
    QUESTION_TYPES,
    get_prompt,
    render_user_prompt,
)

__all__ = [
    # Master prompts (question generation)
    "MASTER_PROMPTS",
    "METRICS",
    "CATEGORIES",
    "DIFFICULTIES",
    "QUESTION_TYPES",
    "BONUS_METRIC_MAPPINGS",
    "get_prompt",
    "render_user_prompt",
    # Judge prompts (evaluation)
    "JUDGE_PROMPTS",
    "JUDGE_STAGE1_VERDICTS",
    "META_SCORE_THRESHOLDS",
    "WEIGHTED_GAP_WEIGHTS",
    "render_stage1_prompt",
    "render_stage2_prompt",
]
