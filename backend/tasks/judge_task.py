"""
MentorMind - Judge Task (Background)

Async task for GPT-4o two-stage judge evaluation.
Runs in background via FastAPI BackgroundTasks.
"""

import logging
import time
from typing import Literal

import openai
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.models.database import SessionLocal
from backend.models.user_evaluation import UserEvaluation
from backend.services.judge_service import judge_service

logger = logging.getLogger(__name__)

# =====================================================
# Configuration
# =====================================================

MAX_RETRIES = 3
RETRY_DELAYS = [1.0, 2.0, 4.0]  # Exponential backoff

# Retriable error types (network/transient issues)
RETRIABLE_ERRORS = (
    openai.APITimeoutError,
    openai.RateLimitError,
    openai.APIConnectionError,
)

# =====================================================
# Core Task Function
# =====================================================

def run_judge_evaluation(user_eval_id: str) -> Literal["success", "failed"]:
    """
    Run judge evaluation in background (full two-stage flow).

    Process:
    1. Create new database session (SessionLocal)
    2. Call judge_service.full_judge_evaluation()
       - Stage 1: Independent blind evaluation
       - ChromaDB query for past mistakes
       - Stage 2: Mentoring comparison
       - Save JudgeEvaluation to database
       - Add to ChromaDB memory
    3. Retry on retriable errors (exponential backoff)
    4. Return success/failure status
    5. Always close session in finally block

    Args:
        user_eval_id: User evaluation ID (e.g., "eval_20250126_143000_aaa111")

    Returns:
        "success" if evaluation completed, "failed" if all retries exhausted

    Note:
        - Database session created locally (FastAPI DI unavailable in background)
        - Session always closed in finally block
        - Full flow handles Stage 1, ChromaDB query, Stage 2, DB save, and memory add
    """
    db = None
    attempt = 0

    try:
        # Create database session
        db = SessionLocal()

        logger.info(f"Starting full judge evaluation for {user_eval_id}")

        # Retry loop
        while attempt < MAX_RETRIES:
            attempt += 1

            try:
                # Call full judge evaluation flow (Stage 1 → ChromaDB → Stage 2 → DB)
                judge_eval_id = judge_service.full_judge_evaluation(
                    user_eval_id=user_eval_id,
                    db=db
                )

                # Success
                logger.info(
                    f"Judge evaluation completed: {user_eval_id} -> {judge_eval_id} "
                    f"(attempt {attempt}/{MAX_RETRIES})"
                )
                return "success"

            except RETRIABLE_ERRORS as e:
                # Retryable error - check if we should retry
                if attempt < MAX_RETRIES:
                    delay = RETRY_DELAYS[min(attempt - 1, len(RETRY_DELAYS) - 1)]
                    logger.warning(
                        f"Judge evaluation failed (attempt {attempt}/{MAX_RETRIES}): "
                        f"{type(e).__name__}. Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    # Max retries exceeded
                    logger.error(
                        f"Judge evaluation failed after {MAX_RETRIES} attempts: "
                        f"{user_eval_id} - {type(e).__name__}: {e}"
                    )
                    return "failed"

            except (ValueError, RuntimeError) as e:
                # Fatal error - don't retry
                logger.error(
                    f"Judge evaluation failed (fatal): {user_eval_id} - {e}"
                )
                return "failed"

    except Exception as e:
        # Unexpected error
        logger.error(
            f"Judge evaluation task failed unexpectedly: "
            f"{user_eval_id} - {e}",
            exc_info=True
        )
        return "failed"

    finally:
        # Always close database session
        if db is not None:
            db.close()


def retry_judge_evaluation(user_eval_id: str) -> Literal["success", "failed"]:
    """
    Retry a failed judge evaluation.

    Same as run_judge_evaluation but can be called via retry endpoint.

    Args:
        user_eval_id: User evaluation ID to retry

    Returns:
        "success" if evaluation completed, "failed" otherwise
    """
    return run_judge_evaluation(user_eval_id)
