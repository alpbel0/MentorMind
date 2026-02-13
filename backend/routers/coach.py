"""
MentorMind - Coach Chat Router

FastAPI router for Coach Chat endpoints.
Implements SSE streaming for real-time AI conversation.

Reference: Task 14.2 - Coach Chat Service Implementation
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.models.database import get_db
from backend.models.schemas import (
    ChatHistoryResponse,
    ChatRequest,
    ChatMessageResponse,
    SnapshotResponse,
)
from backend.services.coach_service import (
    ChatNotAvailableError,
    InvalidSelectedMetricsError,
    MaxTurnsExceededError,
    SnapshotNotFoundError,
    coach_service,
)

logger = logging.getLogger(__name__)


# =====================================================
# Router Setup
# =====================================================

router = APIRouter(tags=["coach"])


# =====================================================
# Request/Response Schemas
# =====================================================

class InitGreetingRequest(BaseModel):
    """Request model for init greeting."""
    selected_metrics: list[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="List of metric slugs to discuss (1-3 metrics)"
    )

    @field_validator("selected_metrics")
    @classmethod
    def validate_metrics(cls, v: list[str]) -> list[str]:
        """Validate metric slugs."""
        valid_metrics = {
            "truthfulness", "helpfulness", "safety", "bias",
            "clarity", "consistency", "efficiency", "robustness"
        }
        for metric in v:
            if metric not in valid_metrics:
                raise ValueError(
                    f"Invalid metric slug: '{metric}'. "
                    f"Valid options: {valid_metrics}"
                )
        return v


class InitGreetingResponse(BaseModel):
    """Response model for init greeting."""
    snapshot_id: str
    greeting: str
    selected_metrics: list[str]


class ChatStreamResponse(BaseModel):
    """Response model for SSE stream data."""
    content: str
    done: bool = False


# =====================================================
# Error Helpers
# =====================================================

def map_coach_error_to_http_status(error: Exception) -> tuple[int, str]:
    """
    Map Coach service errors to HTTP status codes.

    Args:
        error: Exception from coach service

    Returns:
        Tuple of (status_code, detail_message)
    """
    if isinstance(error, SnapshotNotFoundError):
        return status.HTTP_404_NOT_FOUND, str(error)
    elif isinstance(error, MaxTurnsExceededError):
        return status.HTTP_429_TOO_MANY_REQUESTS, str(error)
    elif isinstance(error, ChatNotAvailableError):
        return status.HTTP_400_BAD_REQUEST, str(error)
    elif isinstance(error, InvalidSelectedMetricsError):
        return status.HTTP_400_BAD_REQUEST, str(error)
    elif isinstance(error, ValueError):
        return status.HTTP_502_BAD_GATEWAY, str(error)
    else:
        logger.error(f"Unexpected error in coach endpoint: {error}")
        return status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"


# =====================================================
# Endpoints
# =====================================================

@router.get(
    "/{snapshot_id}/chat",
    response_model=ChatHistoryResponse,
    summary="Get Chat History",
    description="Retrieve chat history for a snapshot's coach conversation."
)
def get_chat_history(
    snapshot_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> ChatHistoryResponse:
    """
    Get chat history for a snapshot.

    Returns recent messages between user and Coach AI.
    """
    try:
        # Validate snapshot exists
        snapshot = coach_service.get_snapshot_context(db, snapshot_id)

        # Get chat history
        history = coach_service.get_chat_history(
            db, snapshot_id, limit=min(limit, 100)
        )

        # Convert to response format using unpacking
        messages = [
            ChatMessageResponse(**msg)
            for msg in history
        ]

        return ChatHistoryResponse(
            snapshot_id=snapshot_id,
            messages=messages,
            total=len(messages),
            is_chat_available=snapshot.is_chat_available,
            turns_remaining=snapshot.max_chat_turns - snapshot.chat_turn_count
        )

    except Exception as e:
        status_code, detail = map_coach_error_to_http_status(e)
        raise HTTPException(status_code=status_code, detail=detail)


@router.post(
    "/{snapshot_id}/chat/init",
    summary="Get Init Greeting",
    description="Get idempotent initial greeting message via SSE streaming."
)
async def get_init_greeting(
    snapshot_id: str,
    request: InitGreetingRequest,
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """
    Get initial greeting message for conversation start via SSE.

    The greeting is idempotent - same inputs produce same greeting.
    Includes selected metrics that are locked for this conversation.
    """
    # Validasyon (Stream öncesi gerçek 404/400 için)
    try:
        coach_service.get_snapshot_context(db, snapshot_id)
    except Exception as e:
        status_code, detail = map_coach_error_to_http_status(e)
        raise HTTPException(status_code=status_code, detail=detail)

    async def generate() -> AsyncGenerator[str, None]:
        try:
            async for chunk in coach_service.handle_init_greeting(
                db=db,
                snapshot_id=snapshot_id,
                selected_metrics=request.selected_metrics
            ):
                yield chunk
        except Exception as e:
            status_code, detail = map_coach_error_to_http_status(e)
            yield f"data: {json.dumps({'error': detail, 'status': status_code})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )


@router.post(
    "/{snapshot_id}/chat/stream",
    summary="Stream Coach Response",
    description="Stream coach response via Server-Sent Events (SSE)."
)
async def stream_coach_response(
    snapshot_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """
    Stream coach response using SSE.

    This endpoint streams the Coach AI's response in real-time.
    Client should handle Server-Sent Events format.

    SSE Format:
        data: {"content": "partial text"}\n\n
        data: [DONE]\n\n

    Example curl:
        curl -N -H "Accept: text/event-stream" \\
             http://localhost:8000/api/snapshots/{id}/chat/stream
    """
    # ✅ EARLY VALIDATION: Check snapshot exists BEFORE opening stream
    # This ensures proper 404 response instead of 200 OK with error in stream
    try:
        coach_service.get_snapshot_context(db, snapshot_id)
    except Exception as e:
        status_code, detail = map_coach_error_to_http_status(e)
        raise HTTPException(status_code=status_code, detail=detail)

    async def generate() -> AsyncGenerator[str, None]:
        """Generator function for SSE streaming."""
        try:
            # Stream response from coach service
            async for chunk in coach_service.stream_coach_response(
                db=db,
                snapshot_id=snapshot_id,
                user_message=request.message,
                selected_metrics=request.selected_metrics,
                client_message_id=request.client_message_id
            ):
                yield chunk

        except Exception as e:
            status_code, detail = map_coach_error_to_http_status(e)
            # Send error as SSE message
            error_json = json.dumps({
                "error": detail,
                "status": status_code
            })
            yield f"data: {error_json}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
            "Connection": "keep-alive",
        }
    )


# =====================================================
# Health Check
# =====================================================

@router.get(
    "/coach/health",
    summary="Coach Service Health",
    description="Health check for coach service."
)
def coach_health() -> dict:
    """
    Health check endpoint for coach service.

    Returns service status and configuration.
    """
    return {
        "status": "healthy",
        "service": "coach_chat",
        "model": settings.coach_model,
        "max_chat_turns": settings.max_chat_turns,
        "chat_history_window": settings.chat_history_window,
    }
