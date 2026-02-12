"""
Snapshot Service - Create Evaluation Snapshots for Coach Chat.

Creates immutable snapshots of completed evaluations after Stage 2 judge evaluation.
Snapshot includes question, answer, scores (with slug conversion), evidence,
and judge feedback. This is the foundation for Coach Chat conversations.

Reference: Task 13.1 - Snapshot Service — Create
"""

import logging
import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.constants.metrics import display_name_to_slug
from backend.models.evaluation_snapshot import EvaluationSnapshot
from backend.services.evidence_service import process_evidence

logger = logging.getLogger(__name__)


# =====================================================
# Exceptions
# =====================================================

class SnapshotNotFoundError(Exception):
    """Snapshot bulunamadığında fırlatılır."""
    pass


# =====================================================
# ID Generation
# =====================================================

def generate_snapshot_id() -> str:
    """
    Generate unique snapshot ID.

    Format: snap_YYYYMMDD_HHMMSS_randomhex
    Example: snap_20260211_143052_abc123def

    Returns:
        Unique snapshot ID string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_hex = secrets.token_hex(6)
    return f"snap_{timestamp}_{random_hex}"


# =====================================================
# Score Conversion (Display Names → Slugs)
# =====================================================

def convert_user_scores_to_slugs(user_scores: dict) -> dict:
    """
    Convert user scores from display names to slugs.

    Input:  {"Truthfulness": {"score": 4, "reasoning": "..."}, ...}
    Output: {"truthfulness": {"score": 4, "reasoning": "..."}, ...}

    Args:
        user_scores: Dictionary with display name keys

    Returns:
        Dictionary with slug keys (unknown metrics are skipped with warning)
    """
    slug_scores = {}
    for display_name, score_data in user_scores.items():
        try:
            slug = display_name_to_slug(display_name)
            slug_scores[slug] = score_data
        except ValueError:
            logger.warning(f"Unknown metric display name: {display_name}, skipping")
    return slug_scores


def convert_judge_scores_to_slugs(judge_scores: dict) -> dict:
    """
    Convert judge scores from display names to slugs.

    Input:  {"Truthfulness": {"score": 5, "rationale": "..."}, ...}
    Output: {"truthfulness": {"score": 5, "rationale": "..."}, ...}

    Args:
        judge_scores: Dictionary with display name keys

    Returns:
        Dictionary with slug keys (unknown metrics are skipped with warning)
    """
    slug_scores = {}
    for display_name, score_data in judge_scores.items():
        try:
            slug = display_name_to_slug(display_name)
            slug_scores[slug] = score_data
        except ValueError:
            logger.warning(f"Unknown metric display name: {display_name}, skipping")
    return slug_scores


def convert_evidence_to_slugs(raw_evidence: dict) -> dict:
    """
    Convert evidence keys from display names to slugs.

    Input:  {"Truthfulness": [{"quote": "...", ...}], ...}
    Output: {"truthfulness": [{"quote": "...", ...}], ...}

    Args:
        raw_evidence: Dictionary with display name keys

    Returns:
        Dictionary with slug keys (unknown metrics are skipped with warning)
    """
    slug_evidence = {}
    for display_name, evidence_list in raw_evidence.items():
        try:
            slug = display_name_to_slug(display_name)
            slug_evidence[slug] = evidence_list
        except ValueError:
            logger.warning(f"Unknown metric display name in evidence: {display_name}, skipping")
    return slug_evidence


# =====================================================
# Main Snapshot Creation Function
# =====================================================

def create_evaluation_snapshot(
    db: Session,
    stage1_result: dict,
    stage2_result: dict,
    user_eval,
    question,
    model_response
) -> EvaluationSnapshot:
    """
    Create evaluation snapshot after Stage 2 completes.

    This is the single atomic write that combines:
    - Stage 1 independent scores (with evidence)
    - Stage 2 alignment analysis and feedback
    - User evaluations
    - Question and model response
    - All converted to slug format (AD-6)

    Args:
        db: Database session
        stage1_result: Stage 1 result with independent_scores (display names)
            {"independent_scores": {"Truthfulness": {...}}}
        stage2_result: Stage 2 result with alignment_analysis, meta_score, etc.
            {"judge_meta_score": 5, "weighted_gap": 0.3, ...}
        user_eval: UserEvaluation ORM object
        question: Question ORM object
        model_response: ModelResponse ORM object

    Returns:
        Created EvaluationSnapshot ORM object

    Raises:
        ValueError: If data is invalid
        RuntimeError: If database operation fails
    """
    try:
        # 1. Generate snapshot ID
        snapshot_id = generate_snapshot_id()

        # 2. Extract and convert user scores to slugs
        user_scores_display = user_eval.evaluations  # Already a dict
        user_scores_json = convert_user_scores_to_slugs(user_scores_display)

        # 3. Extract judge scores from Stage 1 (convert to slugs)
        judge_scores_display = stage1_result.get("independent_scores", {})
        judge_scores_json = convert_judge_scores_to_slugs(judge_scores_display)

        # 4. Process evidence (convert display names to slugs)
        raw_evidence = {}
        for metric_display, metric_data in judge_scores_display.items():
            if "evidence" in metric_data:
                raw_evidence[metric_display] = metric_data["evidence"]

        # Process through self-healing verification
        processed_evidence = process_evidence(
            model_answer=model_response.response_text,
            raw_evidence=raw_evidence,
            anchor_len=settings.evidence_anchor_len,
            search_window=settings.evidence_search_window
        )

        # 5. Convert evidence to slugs and format for JSON
        evidence_json = convert_evidence_to_slugs(processed_evidence) if processed_evidence else None

        # 6. Convert primary_metric and bonus_metrics to slugs
        primary_metric_slug = display_name_to_slug(question.primary_metric)
        bonus_metrics_slugs = [
            display_name_to_slug(bm) for bm in (question.bonus_metrics or [])
        ]

        # 7. Extract judge_evaluation_id from stage2_result
        # It should be passed in stage2_result, or we need to look it up
        judge_evaluation_id = stage2_result.get("judge_evaluation_id")

        # 8. Create snapshot object
        snapshot = EvaluationSnapshot(
            id=snapshot_id,

            # Question snapshot
            question_id=question.id,
            question=question.question,
            model_answer=model_response.response_text,
            model_name=model_response.model_name,
            judge_model=settings.judge_model,

            # Metric info (convert primary_metric to slug)
            primary_metric=primary_metric_slug,
            bonus_metrics=bonus_metrics_slugs,
            category=question.category,

            # Scores (slug format)
            user_scores_json=user_scores_json,
            judge_scores_json=judge_scores_json,
            evidence_json=evidence_json,

            # Judge summary
            judge_meta_score=stage2_result.get("judge_meta_score"),
            weighted_gap=stage2_result.get("weighted_gap"),
            overall_feedback=stage2_result.get("overall_feedback"),

            # Source references
            user_evaluation_id=user_eval.id,
            judge_evaluation_id=judge_evaluation_id,

            # Chat metadata (defaults)
            chat_turn_count=0,
            max_chat_turns=settings.max_chat_turns,
            status="active",
            deleted_at=None
        )

        # 9. Atomic write to database
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        logger.info(f"Snapshot created: {snapshot_id} for user_eval: {user_eval.id}")
        return snapshot

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create snapshot: {e}")
        raise RuntimeError(f"Snapshot creation failed: {e}") from e


# =====================================================
# Helper: Get Snapshot by ID
# =====================================================

def get_snapshot(db: Session, snapshot_id: str) -> Optional[EvaluationSnapshot]:
    """
    Retrieve a snapshot by ID.

    Args:
        db: Database session
        snapshot_id: Snapshot ID to retrieve

    Returns:
        EvaluationSnapshot object or None if not found
    """
    return db.query(EvaluationSnapshot).filter(
        EvaluationSnapshot.id == snapshot_id,
        EvaluationSnapshot.deleted_at.is_(None)
    ).first()


# =====================================================
# Helper: List Snapshots
# =====================================================

def list_snapshots(
    db: Session,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> tuple[list[EvaluationSnapshot], int]:
    """
    List snapshots with optional status filter and pagination.

    Args:
        db: Database session
        status: Filter by status ('active', 'completed', 'archived'), or None for all
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        Tuple of (list of snapshots, total count)
    """
    query = db.query(EvaluationSnapshot).filter(
        EvaluationSnapshot.deleted_at.is_(None)
    )

    if status:
        query = query.filter(EvaluationSnapshot.status == status)

    total = query.count()
    snapshots = query.order_by(
        EvaluationSnapshot.created_at.desc()
    ).limit(limit).offset(offset).all()

    return snapshots, total


# =====================================================
# Soft Delete
# =====================================================

def soft_delete_snapshot(db: Session, snapshot_id: str) -> bool:
    """
    Snapshot'ı soft delete yapar (deleted_at ve status günceller).

    Args:
        db: Database session
        snapshot_id: Silinecek snapshot ID

    Returns:
        True bulundu ve silindi, False bulunamadı
    """
    snapshot = db.query(EvaluationSnapshot).filter(
        EvaluationSnapshot.id == snapshot_id,
        EvaluationSnapshot.deleted_at.is_(None)
    ).first()

    if not snapshot:
        return False

    snapshot.deleted_at = datetime.utcnow()
    snapshot.status = "archived"
    db.commit()

    logger.info(f"Snapshot soft deleted: {snapshot_id}")
    return True
