"""
Snapshot Router - Evaluation Snapshot Endpoints

This module handles API endpoints for evaluation snapshots.
Snapshots are immutable copies of completed evaluations used
as the foundation for Coach Chat conversations.

Reference: Task 13.5 - Snapshot Router & Endpoints
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.schemas import (
    VALID_SNAPSHOT_STATUSES,
    SnapshotResponse,
    SnapshotListItem,
    SnapshotListResponse,
)
from backend.services.snapshot_service import (
    SnapshotNotFoundError,
    get_snapshot,
    list_snapshots,
    soft_delete_snapshot,
)


router = APIRouter()
logger = logging.getLogger(__name__)


# =====================================================
# GET /api/snapshots/ - List Snapshots
# =====================================================

@router.get("/", response_model=SnapshotListResponse)
async def list_snapshots_endpoint(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List evaluation snapshots with optional filtering and pagination.

    Returns active snapshots (deleted_at IS NULL) ordered by created_at DESC.
    Soft-deleted snapshots are excluded from results.

    Query Parameters:
        status: Optional filter by snapshot status ("active", "completed", "archived")
        limit: Maximum results per page (default: 20, max: 100)
        offset: Pagination offset (default: 0)

    Returns:
        SnapshotListResponse with items, total, page, per_page

    Raises:
        HTTPException 400: Invalid status or limit values
    """
    # Validate limit
    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="limit must be at least 1"
        )
    if limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit cannot exceed 100"
        )

    # Validate offset
    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="offset cannot be negative"
        )

    # Validate status if provided
    if status and status not in VALID_SNAPSHOT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{status}'. Valid values: {VALID_SNAPSHOT_STATUSES}"
        )

    # Call service
    snapshots, total = list_snapshots(
        db=db,
        status=status,
        limit=limit,
        offset=offset
    )

    # Map ORM objects to schema
    items = [
        SnapshotListItem(
            id=snap.id,
            created_at=snap.created_at,
            primary_metric=snap.primary_metric,
            category=snap.category,
            judge_meta_score=snap.judge_meta_score,
            status=snap.status,
            chat_turn_count=snap.chat_turn_count
        )
        for snap in snapshots
    ]

    # Calculate page number (1-based)
    page = (offset // limit) + 1 if limit > 0 else 1

    return SnapshotListResponse(
        items=items,
        total=total,
        page=page,
        per_page=limit
    )


# =====================================================
# GET /api/snapshots/{snapshot_id} - Get Snapshot Detail
# =====================================================

@router.get("/{snapshot_id}", response_model=SnapshotResponse)
async def get_snapshot_endpoint(
    snapshot_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single evaluation snapshot by ID.

    Returns complete snapshot data including:
    - Question and model answer
    - User and judge scores (slug format)
    - Evidence (if available)
    - Judge summary and meta score
    - Chat metadata

    Path Parameters:
        snapshot_id: Snapshot ID (format: snap_YYYYMMDD_HHMMSS_hex)

    Returns:
        SnapshotResponse with full snapshot data

    Raises:
        HTTPException 404: Snapshot not found or soft deleted
    """
    snapshot = get_snapshot(db, snapshot_id)

    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"Snapshot '{snapshot_id}' not found"
        )

    # Map ORM to response schema
    return SnapshotResponse(
        id=snapshot.id,
        created_at=snapshot.created_at,
        updated_at=snapshot.updated_at,
        question_id=snapshot.question_id,
        question=snapshot.question,
        model_answer=snapshot.model_answer,
        model_name=snapshot.model_name,
        judge_model=snapshot.judge_model,
        primary_metric=snapshot.primary_metric,
        bonus_metrics=list(snapshot.bonus_metrics) if snapshot.bonus_metrics else [],
        category=snapshot.category,
        user_scores_json=snapshot.user_scores_json,
        judge_scores_json=snapshot.judge_scores_json,
        evidence_json=snapshot.evidence_json,
        judge_meta_score=snapshot.judge_meta_score,
        weighted_gap=snapshot.weighted_gap,
        overall_feedback=snapshot.overall_feedback,
        user_evaluation_id=snapshot.user_evaluation_id,
        judge_evaluation_id=snapshot.judge_evaluation_id,
        chat_turn_count=snapshot.chat_turn_count,
        max_chat_turns=snapshot.max_chat_turns,
        status=snapshot.status,
        deleted_at=snapshot.deleted_at,
        is_chat_available=snapshot.is_chat_available
    )


# =====================================================
# DELETE /api/snapshots/{snapshot_id} - Soft Delete Snapshot
# =====================================================

@router.delete("/{snapshot_id}", status_code=204)
async def delete_snapshot_endpoint(
    snapshot_id: str,
    db: Session = Depends(get_db)
):
    """
    Soft delete an evaluation snapshot.

    Sets deleted_at timestamp and changes status to "archived".
    Snapshot data remains in database but is excluded from list results.

    Path Parameters:
        snapshot_id: Snapshot ID to soft delete

    Returns:
        204 No Content on success

    Raises:
        HTTPException 404: Snapshot not found or already deleted
    """
    success = soft_delete_snapshot(db, snapshot_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Snapshot '{snapshot_id}' not found or already deleted"
        )

    # FastAPI handles 204 No Content
    return None
