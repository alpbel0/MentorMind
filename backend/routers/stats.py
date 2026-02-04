"""
Statistics Router - User Performance Statistics Endpoints

This module handles API endpoints for user performance statistics.
Provides overview of evaluations, meta scores, and per-metric performance.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.database import get_db
from backend.models.schemas import StatsOverview, MetricPerformance
from backend.models.judge_evaluation import JudgeEvaluation


router = APIRouter()
logger = logging.getLogger(__name__)

# Constants
EVALUATION_METRICS = [
    "Truthfulness", "Helpfulness", "Safety", "Bias",
    "Clarity", "Consistency", "Efficiency", "Robustness"
]


def _calculate_overall_trend(db: Session) -> str:
    """
    Calculate overall improvement trend based on recent evaluations.

    Compares last 10 evaluations with previous 10 evaluations.

    Args:
        db: Database session

    Returns:
        Trend string: "+X.X (last 10 evaluations)" or "No data yet"
    """
    # Get last 20 evaluations ordered by created_at
    recent_evals = db.query(JudgeEvaluation)\
        .order_by(JudgeEvaluation.created_at.desc())\
        .limit(20)\
        .all()

    if len(recent_evals) < 10:
        return "Insufficient data (need at least 10 evaluations)"

    last_10 = recent_evals[:10]
    prev_10 = recent_evals[10:20] if len(recent_evals) > 10 else []

    # Calculate average weighted gap for last 10
    last_avg_gap = sum(e.weighted_gap for e in last_10) / len(last_10)

    if prev_10:
        prev_avg_gap = sum(e.weighted_gap for e in prev_10) / len(prev_10)
        diff = prev_avg_gap - last_avg_gap
        direction = "+" if diff >= 0 else ""
        return f"{direction}{diff:.2f} (last 10 evaluations)"
    else:
        return f"{last_avg_gap:.2f} (current avg)"


def _calculate_metric_trend(evaluations: list) -> str:
    """
    Calculate trend for a specific metric.

    Args:
        evaluations: List of JudgeEvaluation objects for this metric

    Returns:
        Trend string: "improving", "stable", or "declining"
    """
    if len(evaluations) < 2:
        return "insufficient_data"

    # First 10 (most recent) vs next 10 (previous)
    last_10 = evaluations[:10]
    prev_10 = evaluations[10:20] if len(evaluations) > 10 else []

    if not prev_10:
        return "stable"

    last_avg_gap = sum(e.primary_metric_gap for e in last_10) / len(last_10)
    prev_avg_gap = sum(e.primary_metric_gap for e in prev_10) / len(prev_10)

    # Threshold of 0.2 for meaningful change
    if last_avg_gap < prev_avg_gap - 0.2:
        return "improving"
    elif last_avg_gap > prev_avg_gap + 0.2:
        return "declining"
    else:
        return "stable"


@router.get("/overview", response_model=StatsOverview)
async def get_stats_overview(db: Session = Depends(get_db)) -> StatsOverview:
    """
    Get user performance statistics overview.

    Returns:
        - Total evaluations count
        - Average judge meta score
        - Per-metric performance (avg gap, count, trend)
        - Overall improvement trend

    Trend calculation:
    - Improving: last avg gap < prev avg gap - 0.2
    - Declining: last avg gap > prev avg gap + 0.2
    - Stable: within 0.2 threshold
    """
    # 1. Total evaluations
    total_evaluations = db.query(JudgeEvaluation).count()

    # 2. Average meta score
    avg_meta_score = db.query(func.avg(JudgeEvaluation.judge_meta_score)).scalar() or 0.0

    # 3. Per-metric performance
    metrics_performance = {}

    for metric in EVALUATION_METRICS:
        # Get recent evaluations for this metric (last 20)
        recent = db.query(JudgeEvaluation)\
            .filter(JudgeEvaluation.primary_metric == metric)\
            .order_by(JudgeEvaluation.created_at.desc())\
            .limit(20)\
            .all()

        if not recent:
            continue

        # Calculate average gap from available evaluations
        last_evals = recent[:10]
        avg_gap = sum(e.primary_metric_gap for e in last_evals) / len(last_evals)

        # Calculate trend
        trend = _calculate_metric_trend(recent)

        metrics_performance[metric] = MetricPerformance(
            avg_gap=round(avg_gap, 2),
            count=len(last_evals),
            trend=trend
        )

    # 4. Overall improvement trend
    improvement_trend = _calculate_overall_trend(db)

    logger.info(f"Stats overview: {total_evaluations} evaluations, avg meta score: {avg_meta_score:.1f}")

    return StatsOverview(
        total_evaluations=total_evaluations,
        average_meta_score=round(float(avg_meta_score), 1),
        metrics_performance=metrics_performance,
        improvement_trend=improvement_trend
    )
