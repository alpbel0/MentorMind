"""
MentorMind - Coach Chat Service

This module handles Coach AI conversations for evaluation mentoring.
Provides SSE streaming responses, chat history management, and idempotent init greetings.

Reference: Task 14.2 - Coach Chat Service Implementation
"""

import json
import logging
import secrets
import time
from datetime import datetime
from typing import Any, AsyncGenerator

import openai
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.models.chat_message import ChatMessage
from backend.models.evaluation_snapshot import EvaluationSnapshot
from backend.prompts.coach_prompts import (
    COACH_SYSTEM_PROMPT,
    COACH_MAX_HISTORY_WINDOW,
    render_coach_init_greeting,
    render_coach_user_prompt,
)
from backend.services.snapshot_service import SnapshotNotFoundError, get_snapshot
from backend.services.llm_logger import log_llm_call

logger = logging.getLogger(__name__)


# =====================================================
# Exceptions
# =====================================================

class ChatNotAvailableError(Exception):
    """Chat is not available for this snapshot."""
    pass


class MaxTurnsExceededError(Exception):
    """Maximum chat turns exceeded for this snapshot."""
    pass


class InvalidSelectedMetricsError(Exception):
    """Invalid selected metrics provided."""
    pass


# =====================================================
# Message ID Generation
# =====================================================

def generate_message_id() -> str:
    """
    Generate unique message ID.

    Format: msg_YYYYMMDD_HHMMSS_randomhex
    Example: msg_20260213_143052_abc123def

    Returns:
        Unique message ID string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_hex = secrets.token_hex(6)
    return f"msg_{timestamp}_{random_hex}"


# =====================================================
# Coach Service Class
# =====================================================

class CoachService:
    """
    Service for Coach Chat with SSE streaming.

    Handles:
    - Snapshot retrieval and validation
    - Chat history management
    - Init greeting generation (idempotent)
    - Chat turn streaming via OpenRouter
    - Message persistence
    - Turn count enforcement

    Uses:
    - OpenRouter API (via OpenAI client) with streaming=True
    - GPT-4o-mini model (settings.coach_model)
    - Turkish response language
    - Selected metrics constraint (AD-10)
    """

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 60
    ):
        """
        Initialize Coach service.

        Args:
            api_key: OpenRouter API key (defaults to settings.openrouter_api_key)
            timeout: Request timeout in seconds (default: 60)
        """
        self.api_key = api_key or settings.openrouter_api_key
        self.timeout = timeout
        self.model = settings.coach_model  # "openai/gpt-4o-mini"

        # Initialize OpenAI client with OpenRouter base URL
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=settings.openrouter_base_url,
            timeout=self.timeout
        )

        logger.info(f"CoachService initialized with model={self.model}, timeout={timeout}s")

    # =====================================================
    # Snapshot Context
    # =====================================================

    def get_snapshot_context(
        self,
        db: Session,
        snapshot_id: str
    ) -> EvaluationSnapshot:
        """
        Fetch snapshot and validate chat availability.

        Args:
            db: Database session
            snapshot_id: Snapshot ID to retrieve

        Returns:
            EvaluationSnapshot object

        Raises:
            SnapshotNotFoundError: If snapshot not found or soft deleted
            ChatNotAvailableError: If chat is not available (status/turn count)
        """
        snapshot = get_snapshot(db, snapshot_id)

        if not snapshot:
            raise SnapshotNotFoundError(f"Snapshot not found: {snapshot_id}")

        # Check if chat is available
        if not snapshot.is_chat_available:
            if snapshot.chat_turn_count >= snapshot.max_chat_turns:
                raise MaxTurnsExceededError(
                    f"Maximum chat turns exceeded ({snapshot.chat_turn_count}/{snapshot.max_chat_turns})"
                )
            elif snapshot.status != "active":
                raise ChatNotAvailableError(
                    f"Snapshot status is '{snapshot.status}', chat not available"
                )
            else:
                raise ChatNotAvailableError(
                    f"Chat not available for snapshot {snapshot_id}"
                )

        return snapshot

    # =====================================================
    # Chat History Management
    # =====================================================

    def get_chat_history(
        self,
        db: Session,
        snapshot_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Fetch chat history for a snapshot.

        Args:
            db: Database session
            snapshot_id: Snapshot ID
            limit: Max messages to return (defaults to settings.chat_history_window)

        Returns:
            List of message dicts with 'role' and 'content'
        """
        if limit is None:
            limit = settings.chat_history_window  # AD-4: Default 6

        messages = db.query(ChatMessage).filter(
            ChatMessage.snapshot_id == snapshot_id
        ).order_by(
            ChatMessage.created_at.asc()
        ).limit(limit).all()

        return [
            {
                "id": msg.id,
                "snapshot_id": msg.snapshot_id,
                "client_message_id": msg.client_message_id,
                "role": msg.role,
                "content": msg.content,
                "is_complete": msg.is_complete,
                "selected_metrics": msg.selected_metrics,
                "token_count": msg.token_count,
                "created_at": msg.created_at
            }
            for msg in messages
        ]

    def increment_chat_turn(
        self,
        db: Session,
        snapshot_id: str
    ) -> EvaluationSnapshot:
        """
        Increment chat turn count for a snapshot.

        Args:
            db: Database session
            snapshot_id: Snapshot ID

        Returns:
            Updated snapshot object
        """
        snapshot = get_snapshot(db, snapshot_id)
        if not snapshot:
            raise SnapshotNotFoundError(f"Snapshot not found: {snapshot_id}")

        snapshot.chat_turn_count += 1
        db.commit()
        db.refresh(snapshot)

        logger.info(f"Chat turn count incremented to {snapshot.chat_turn_count} for {snapshot_id}")
        return snapshot

    # =====================================================
    # Message Persistence
    # =====================================================

    def save_user_message(
        self,
        db: Session,
        snapshot_id: str,
        content: str,
        selected_metrics: list[str],
        client_message_id: str
    ) -> ChatMessage:
        """
        Save a user message to database.

        Args:
            db: Database session
            snapshot_id: Snapshot ID
            content: Message content
            selected_metrics: List of metric slugs user selected
            client_message_id: Client-generated UUID for idempotency

        Returns:
            Created ChatMessage object
        """
        message_id = generate_message_id()

        message = ChatMessage(
            id=message_id,
            client_message_id=client_message_id,
            snapshot_id=snapshot_id,
            role="user",
            content=content,
            selected_metrics=selected_metrics,
            is_complete=True,
            token_count=0  # TODO: Calculate actual token count
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        logger.debug(f"User message saved: {message_id} for snapshot {snapshot_id}")
        return message

    def save_assistant_message(
        self,
        db: Session,
        snapshot_id: str,
        content: str,
        client_message_id: str,
        is_complete: bool = True
    ) -> ChatMessage:
        """
        Save an assistant message to database.

        Args:
            db: Database session
            snapshot_id: Snapshot ID
            content: Message content
            client_message_id: Shared Turn ID (same as user message)
            is_complete: True if fully delivered, False if streaming

        Returns:
            Created ChatMessage object
        """
        message_id = generate_message_id()

        message = ChatMessage(
            id=message_id,
            client_message_id=client_message_id,  # Shared Turn ID
            snapshot_id=snapshot_id,
            role="assistant",
            content=content,
            selected_metrics=None,
            is_complete=is_complete,
            token_count=0  # TODO: Calculate actual token count
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        logger.debug(f"Assistant message saved: {message_id} for snapshot {snapshot_id}")
        return message

    # =====================================================
    # Init Greeting (Idempotent)
    # =====================================================

    def generate_init_greeting(
        self,
        db: Session,
        snapshot_id: str,
        selected_metrics: list[str]
    ) -> str:
        """
        Generate idempotent init greeting for conversation start.

        The greeting is deterministic based on snapshot content and
        selected metrics - same inputs always produce same greeting.

        Args:
            db: Database session
            snapshot_id: Snapshot ID
            selected_metrics: List of metric slugs user wants to discuss

        Returns:
            Greeting message string in Turkish

        Raises:
            SnapshotNotFoundError: If snapshot not found
            InvalidSelectedMetricsError: If selected metrics are invalid
        """
        snapshot = self.get_snapshot_context(db, snapshot_id)

        # Validate selected metrics
        for metric in selected_metrics:
            # Check if metric slug is valid (basic check)
            if not isinstance(metric, str) or metric not in [
                "truthfulness", "helpfulness", "safety", "bias",
                "clarity", "consistency", "efficiency", "robustness"
            ]:
                raise InvalidSelectedMetricsError(f"Invalid metric slug: {metric}")

        # Render greeting using coach prompts
        greeting = render_coach_init_greeting(
            question=snapshot.question,
            model_answer=snapshot.model_answer,
            user_scores=snapshot.user_scores_json,
            judge_scores=snapshot.judge_scores_json,
            evidence_json=snapshot.evidence_json,
            selected_metrics=selected_metrics
        )

        logger.info(f"Init greeting generated for snapshot {snapshot_id}")
        return greeting

    # =====================================================
    # Chat Turn Streaming
    # =====================================================

    async def stream_coach_response(
        self,
        db: Session,
        snapshot_id: str,
        user_message: str,
        selected_metrics: list[str],
        client_message_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream coach response using SSE format.

        Process:
        1. Get snapshot and validate chat availability
        2. Get chat history (last N messages)
        3. Save user message to database
        4. Build chat context for LLM
        5. Call OpenRouter API with streaming=True
        6. Yield SSE-formatted chunks
        7. Save complete assistant message
        8. Increment chat turn count

        Args:
            db: Database session
            snapshot_id: Snapshot ID
            user_message: User's message text
            selected_metrics: List of metric slugs user selected
            client_message_id: Client UUID for idempotency

        Yields:
            SSE-formatted response chunks (strings starting with "data: ")

        Raises:
            SnapshotNotFoundError: If snapshot not found
            ChatNotAvailableError: If chat not available
            MaxTurnsExceededError: If max turns exceeded
            InvalidSelectedMetricsError: If metrics invalid
            ValueError: If API call fails
        """
        # 1. Get and validate snapshot
        snapshot = self.get_snapshot_context(db, snapshot_id)

        # 2. Get chat history
        history_limit = min(settings.chat_history_window, snapshot.chat_turn_count + 1)
        chat_history = self.get_chat_history(db, snapshot_id, limit=history_limit)

        # 3. Save user message
        try:
            self.save_user_message(
                db=db,
                snapshot_id=snapshot_id,
                content=user_message,
                selected_metrics=selected_metrics,
                client_message_id=client_message_id
            )
        except Exception as e:
            logger.warning(f"Failed to save user message (may be duplicate): {e}")
            # Continue - idempotency handles duplicates

        # 4. Build chat context
        system_prompt = COACH_SYSTEM_PROMPT

        user_prompt = render_coach_user_prompt(
            question=snapshot.question,
            model_answer=snapshot.model_answer,
            user_scores=snapshot.user_scores_json,
            judge_scores=snapshot.judge_scores_json,
            evidence_json=snapshot.evidence_json,
            chat_history=chat_history,
            user_message=user_message,
            selected_metrics=selected_metrics,
            history_window=settings.chat_history_window
        )

        # 5. Call OpenRouter API with streaming
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        full_response = ""
        start_time = time.time()

        try:
            # Make streaming API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                timeout=self.timeout,
                extra_headers={
                    "HTTP-Referer": "https://github.com/yigitalp/MentorMind",
                    "X-Title": "MentorMind"
                }
            )

            # Stream response chunks
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content

                    # Yield SSE formatted chunk
                    sse_chunk = json.dumps({"content": content})
                    yield f"data: {sse_chunk}\n\n"

            # Send final done message
            yield "data: [DONE]\n\n"

            duration = time.time() - start_time

            # Log successful LLM call
            log_llm_call(
                provider="openai",  # Using OpenAI client for OpenRouter
                model=self.model,
                purpose="coach_chat",
                duration_seconds=duration,
                success=True
            )

            # 6. Save assistant message
            self.save_assistant_message(
                db=db,
                snapshot_id=snapshot_id,
                content=full_response,
                client_message_id=client_message_id,
                is_complete=True
            )

            # 7. Increment chat turn count
            self.increment_chat_turn(db, snapshot_id)

            logger.info(
                f"Coach response streamed for snapshot {snapshot_id}, "
                f"turn_count={snapshot.chat_turn_count + 1}, "
                f"duration={duration:.2f}s"
            )

        except Exception as e:
            duration = time.time() - start_time

            # Log failed LLM call
            log_llm_call(
                provider="openai",
                model=self.model,
                purpose="coach_chat",
                duration_seconds=duration,
                success=False,
                error=str(e)
            )

            logger.error(f"Coach API call failed: {e}")
            raise ValueError(f"Coach API call failed: {e}") from e


# =====================================================
# Global Service Instance
# =====================================================

coach_service = CoachService()


# =====================================================
# Convenience Functions
# =====================================================

def get_snapshot_context(
    db: Session,
    snapshot_id: str
) -> EvaluationSnapshot:
    """
    Get snapshot context using global service instance.

    Args:
        db: Database session
        snapshot_id: Snapshot ID

    Returns:
        EvaluationSnapshot object
    """
    return coach_service.get_snapshot_context(db, snapshot_id)


def get_chat_history(
    db: Session,
    snapshot_id: str,
    limit: int | None = None
) -> list[dict[str, Any]]:
    """
    Get chat history using global service instance.

    Args:
        db: Database session
        snapshot_id: Snapshot ID
        limit: Max messages to return

    Returns:
        List of message dicts
    """
    return coach_service.get_chat_history(db, snapshot_id, limit)


def generate_init_greeting(
    db: Session,
    snapshot_id: str,
    selected_metrics: list[str]
) -> str:
    """
    Generate init greeting using global service instance.

    Args:
        db: Database session
        snapshot_id: Snapshot ID
        selected_metrics: List of metric slugs

    Returns:
        Greeting message string
    """
    return coach_service.generate_init_greeting(db, snapshot_id, selected_metrics)
