"""
MentorMind - Questions Router

This module handles API endpoints for question generation and pool management.
It orchestrates Claude service (question generation) and Model service (K model answers).

Endpoints:
- POST /api/questions/generate - Generate new question or select from pool
- GET /api/questions/pool/stats - Get question pool statistics
"""

import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.schemas import QuestionPoolStats
from backend.services.claude_service import claude_service
from backend.services.model_service import model_service

logger = logging.getLogger(__name__)


# =====================================================
# Router Definition
# =====================================================

router = APIRouter()


# =====================================================
# Request/Response Schemas
# =====================================================

class QuestionGenerateRequest(BaseModel):
    """Request schema for question generation."""

    primary_metric: str = Field(..., description="Primary metric to generate for")
    use_pool: bool = Field(default=False, description="Use pool instead of generating new")


class QuestionGenerateResponse(BaseModel):
    """Response schema for question generation."""

    question_id: str = Field(..., description="Question ID")
    response_id: str = Field(..., description="Model response ID")
    question: str = Field(..., description="Question text")
    model_response: str = Field(..., description="K model's answer")
    model_name: str = Field(..., description="K model name")
    category: str = Field(..., description="Question category")


# =====================================================
# Endpoints
# =====================================================

@router.post("/generate", response_model=QuestionGenerateResponse)
async def generate_question(
    request: QuestionGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a new question or select from pool and get K model response.

    Process:
    1. Generate/select question via Claude service
    2. Select K model that hasn't answered this question
    3. Get model response via OpenRouter
    4. Return combined data (hide primary/bonus metrics from user)

    Args:
        request: Question generation request
        db: Database session

    Returns:
        Question and model response data

    Raises:
        HTTPException: If generation or API call fails
    """
    try:
        # 1. Generate question
        logger.info(
            f"Generating question for metric={request.primary_metric}, "
            f"use_pool={request.use_pool}"
        )
        question = claude_service.generate_question(
            primary_metric=request.primary_metric,
            use_pool=request.use_pool,
            db=db
        )

        # 2. Select model
        model_name = model_service.select_model(question.id, db)
        logger.info(f"Selected model {model_name} for question {question.id}")

        # 3. Get response
        model_response = model_service.answer_question(
            question_id=question.id,
            model_name=model_name,
            db=db
        )

        return QuestionGenerateResponse(
            question_id=question.id,
            response_id=model_response.id,
            question=question.question,
            model_response=model_response.response_text,
            model_name=model_response.model_name,
            category=question.category
        )

    except ValueError as e:
        logger.error(f"Question generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in question generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/pool/stats", response_model=QuestionPoolStats)
async def get_pool_stats(db: Session = Depends(get_db)):
    """
    Get statistics about the question pool.

    Returns breakdowns by:
    - Total count
    - By primary metric
    - By category
    - By difficulty
    - Average times_used

    Args:
        db: Database session

    Returns:
        Question pool statistics
    """
    from backend.models.question import Question
    from sqlalchemy import func

    # Total questions
    total = db.query(Question).count()

    # By metric
    by_metric = dict(db.query(
        Question.primary_metric,
        func.count(Question.id)
    ).group_by(Question.primary_metric).all())

    # By category
    by_category = dict(db.query(
        Question.category,
        func.count(Question.id)
    ).group_by(Question.category).all())

    # By difficulty
    by_difficulty = dict(db.query(
        Question.difficulty,
        func.count(Question.id)
    ).group_by(Question.difficulty).all())

    # Average times_used
    avg_times = db.query(
        func.avg(Question.times_used)
    ).scalar() or 0.0

    return QuestionPoolStats(
        total_questions=total,
        by_metric=by_metric,
        by_category=by_category,
        by_difficulty=by_difficulty,
        avg_times_used=float(avg_times)
    )
