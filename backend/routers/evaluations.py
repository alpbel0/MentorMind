"""
Evaluation Router - User Evaluation Endpoints

This module handles API endpoints for user evaluation submission.
Users submit their evaluations of K model responses across 8 metrics.
"""

import logging
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.schemas import (
    EvaluationSubmitRequest,
    EvaluationSubmitResponse,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/submit", response_model=EvaluationSubmitResponse)
async def submit_evaluation(
    request: EvaluationSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit user evaluation for a model response.

    Process:
    1. Validate request (8 metrics, scores 1-5 or null)
    2. Fetch model_response to verify it exists
    3. Generate evaluation ID: eval_YYYYMMDD_HHMMSS_randomhex
    4. Create UserEvaluation object
    5. Save to database and update model_response.evaluated flag
    6. Return evaluation_id

    Note: Judge task will be implemented in Task 3.11
    Note: evaluation_id column removed due to circular dependency

    Args:
        request: Evaluation submission with response_id and evaluations dict
        db: Database session

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

        logger.info(
            f"Created evaluation: {evaluation_id} for response: {request.response_id}"
        )

        return EvaluationSubmitResponse(
            evaluation_id=evaluation_id,
            status="submitted",
            message="Evaluation submitted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evaluation submission failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
