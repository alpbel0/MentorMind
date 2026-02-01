"""
Evaluation Router - User Evaluation Endpoints

This module handles API endpoints for user evaluation submission.
Users submit their evaluations of K model responses across 8 metrics.
"""

import logging
import secrets
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.schemas import (
    EvaluationSubmitRequest,
    EvaluationSubmitResponse,
)
from backend.tasks.judge_task import run_judge_evaluation, retry_judge_evaluation


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/submit", response_model=EvaluationSubmitResponse)
async def submit_evaluation(
    request: EvaluationSubmitRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Submit user evaluation for a model response.

    Process:
    1. Validate request (8 metrics, scores 1-5 or null)
    2. Fetch model_response to verify it exists
    3. Generate evaluation ID: eval_YYYYMMDD_HHMMSS_randomhex
    4. Create UserEvaluation object
    5. Save to database and update model_response.evaluated flag
    6. Start background judge task
    7. Return evaluation_id with status="submitted"

    Note: Judge task runs asynchronously. User polls /feedback endpoint.

    Args:
        request: Evaluation submission with response_id and evaluations dict
        db: Database session
        background_tasks: FastAPI BackgroundTasks for async execution

    Returns:
        EvaluationSubmitResponse with evaluation_id and status

    Raises:
        HTTPException 404: Model response not found
        HTTPException 400: Response already evaluated
        HTTPException 500: Database error
    """
    try:
        # 1. Validate evaluations (handled by Pydantic schema)
        evaluations = request.evaluations

        # 2. Fetch model response
        from backend.models.model_response import ModelResponse
        model_response = db.query(ModelResponse).filter(
            ModelResponse.id == request.response_id
        ).first()

        if not model_response:
            raise HTTPException(
                status_code=404,
                detail=f"Model response '{request.response_id}' not found"
            )

        if model_response.evaluated:
            raise HTTPException(
                status_code=400,
                detail=f"Response '{request.response_id}' already evaluated"
            )

        # 3. Generate evaluation ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hex = secrets.token_hex(3)
        evaluation_id = f"eval_{timestamp}_{random_hex}"

        # 4. Create UserEvaluation
        from backend.models.user_evaluation import UserEvaluation

        # Convert MetricEvaluation objects to dict format for JSONB
        evaluations_dict = {
            metric: {
                "score": eval_data.score,
                "reasoning": eval_data.reasoning
            }
            for metric, eval_data in evaluations.items()
        }

        user_eval = UserEvaluation(
            id=evaluation_id,
            response_id=request.response_id,
            evaluations=evaluations_dict,
            judged=False
        )

        db.add(user_eval)

        # 5. Update model_response.evaluated flag
        # NOTE: evaluation_id column was removed due to circular dependency
        model_response.evaluated = True

        try:
            db.commit()
            db.refresh(user_eval)
        except Exception as e:
            db.rollback()
            logger.error(f"Database error during evaluation submission: {e}")
            raise HTTPException(
                status_code=500,
                detail="Database error while saving evaluation"
            )

        # 6. Start async judge task
        background_tasks.add_task(run_judge_evaluation, evaluation_id)

        logger.info(
            f"Created evaluation: {evaluation_id} for response: {request.response_id}. "
            f"Judge task started in background."
        )

        return EvaluationSubmitResponse(
            evaluation_id=evaluation_id,
            status="submitted",
            message="Evaluation submitted successfully. Judge evaluation running in background."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evaluation submission failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/{evaluation_id}/feedback")
async def get_evaluation_feedback(
    evaluation_id: str,
    db: Session = Depends(get_db)
):
    """
    Get judge feedback for an evaluation.

    Polling endpoint for clients to check if judge evaluation is complete.

    Args:
        evaluation_id: User evaluation ID
        db: Database session

    Returns:
        - If judged=FALSE: {status: "processing", message: "..."}
        - If judged=TRUE: {status: "completed", message: "..."}

        Note: Full judge feedback (including scores) will be added in Week 4
        with Stage 2 implementation.

    Raises:
        HTTPException 404: Evaluation not found
    """
    from backend.models.user_evaluation import UserEvaluation

    user_eval = db.query(UserEvaluation).filter(
        UserEvaluation.id == evaluation_id
    ).first()

    if not user_eval:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation '{evaluation_id}' not found"
        )

    if not user_eval.judged:
        return {
            "evaluation_id": evaluation_id,
            "status": "processing",
            "message": "Judge evaluation in progress. Please try again later."
        }

    # Fetch judge evaluation (will be implemented in Week 4 with Stage 2)
    # For now, return basic completion status
    return {
        "evaluation_id": evaluation_id,
        "status": "completed",
        "message": "Judge evaluation completed. Full feedback will be available in Week 4."
    }


@router.post("/{evaluation_id}/retry")
async def retry_evaluation(
    evaluation_id: str,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Retry a failed judge evaluation.

    Args:
        evaluation_id: User evaluation ID to retry
        background_tasks: FastAPI BackgroundTasks for async execution
        db: Database session

    Returns:
        {status: "retrying" | "already_completed", message: "..."}

    Raises:
        HTTPException 404: Evaluation not found
    """
    from backend.models.user_evaluation import UserEvaluation

    user_eval = db.query(UserEvaluation).filter(
        UserEvaluation.id == evaluation_id
    ).first()

    if not user_eval:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation '{evaluation_id}' not found"
        )

    if user_eval.judged:
        return {
            "evaluation_id": evaluation_id,
            "status": "already_completed",
            "message": "Evaluation already judged."
        }

    # Add retry task
    background_tasks.add_task(retry_judge_evaluation, evaluation_id)

    logger.info(f"Judge evaluation retry initiated: {evaluation_id}")

    return {
        "evaluation_id": evaluation_id,
        "status": "retrying",
        "message": "Judge evaluation retry initiated."
    }
