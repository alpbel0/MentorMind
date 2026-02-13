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
    ) -> bool:
        """
        Increment chat turn count atomically.

        Uses atomic SQL UPDATE with WHERE clause to prevent race conditions
        and enforce turn limit at the database level (AD-9).

        Args:
            db: Database session
            snapshot_id: Snapshot ID

        Returns:
            True if incremented successfully, False if limit reached or not found
        """
        from sqlalchemy import update

        # Atomic update with turn limit check
        stmt = (
            update(EvaluationSnapshot)
            .where(EvaluationSnapshot.id == snapshot_id)
            .where(EvaluationSnapshot.deleted_at.is_(None))
            .where(EvaluationSnapshot.chat_turn_count < EvaluationSnapshot.max_chat_turns)
            .values(chat_turn_count=EvaluationSnapshot.chat_turn_count + 1)
        )

        result = db.execute(stmt)
        db.commit()

        success = result.rowcount > 0
        if success:
            logger.info(f"Chat turn count incremented atomically for {snapshot_id}")
        else:
            logger.warning(f"Failed to increment turn count for {snapshot_id} (limit reached or not found)")

        return success

    def get_existing_assistant_message(
        self,
        db: Session,
        snapshot_id: str,
        client_message_id: str
    ) -> ChatMessage | None:
        """
        Check if an assistant message already exists for this turn.

        Used for idempotency and reconnection (AD-4).

        Args:
            db: Database session
            snapshot_id: Snapshot ID
            client_message_id: Shared Turn ID

        Returns:
            ChatMessage object if found, else None
        """
        return db.query(ChatMessage).filter(
            ChatMessage.snapshot_id == snapshot_id,
            ChatMessage.client_message_id == client_message_id,
            ChatMessage.role == "assistant"
        ).first()

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
        Save or update an assistant message (Update-In-Place for AD-4).

        If a partial message exists for this client_message_id, it updates
        the existing record. Otherwise, it creates a new one.

        Args:
            db: Database session
            snapshot_id: Snapshot ID
            content: Message content
            client_message_id: Shared Turn ID
            is_complete: True if fully delivered, False if streaming

        Returns:
            Created or updated ChatMessage object
        """
        # Check for existing partial message (Update-In-Place)
        existing = self.get_existing_assistant_message(db, snapshot_id, client_message_id)

        if existing:
            existing.content = content
            existing.is_complete = is_complete
            existing.updated_at = datetime.now()
            message = existing
            logger.debug(f"Assistant message updated (Update-In-Place): {message.id}")
        else:
            # Create new message
            message_id = generate_message_id()
            message = ChatMessage(
                id=message_id,
                client_message_id=client_message_id,
                snapshot_id=snapshot_id,
                role="assistant",
                content=content,
                selected_metrics=None,
                is_complete=is_complete,
                token_count=0
            )
            db.add(message)
            logger.debug(f"New assistant message saved: {message_id}")

        db.commit()
        db.refresh(message)
        return message

    def get_remaining_turns(
        self,
        db: Session,
        snapshot_id: str
    ) -> int:
        """
        Get remaining chat turns for a snapshot.

        Args:
            db: Database session
            snapshot_id: Snapshot ID

        Returns:
            Number of turns remaining
        """
        snapshot = get_snapshot(db, snapshot_id)
        if not snapshot:
            return 0
        
        remaining = snapshot.max_chat_turns - snapshot.chat_turn_count
        return max(0, remaining)

    # =====================================================
    # Init Greeting (Idempotent & Streaming)
    # =====================================================

    async def handle_init_greeting(
        self,
        db: Session,
        snapshot_id: str,
        selected_metrics: list[str]
    ) -> AsyncGenerator[str, None]:
        """
        Handle initial greeting with idempotency and streaming (AD-4).

        1. Check if init greeting already exists in DB.
        2. If exists: Stream the cached response.
        3. If not: Generate via LLM (streaming), save to DB.
        4. Does NOT increment chat turn count (bonus message).
        """
        client_message_id = f"init_{snapshot_id}"
        
        # 1. Check for existing cached greeting
        existing = self.get_existing_assistant_message(db, snapshot_id, client_message_id)
        
        if existing and existing.is_complete:
            logger.info(f"Returning cached init greeting for snapshot {snapshot_id}")
            sse_chunk = json.dumps({"content": existing.content})
            yield f"data: {sse_chunk}\n\n"
            yield "data: [DONE]\n\n"
            return

        # 2. Get snapshot context
        snapshot = self.get_snapshot_context(db, snapshot_id)

        # 3. Build Prompt Context
        # Note: Init greeting uses render_coach_init_greeting template
        prompt_content = render_coach_init_greeting(
            question=snapshot.question,
            model_answer=snapshot.model_answer,
            user_scores=snapshot.user_scores_json,
            judge_scores=snapshot.judge_scores_json,
            evidence_json=snapshot.evidence_json,
            selected_metrics=selected_metrics
        )

        messages = [
            {"role": "system", "content": COACH_SYSTEM_PROMPT},
            {"role": "user", "content": prompt_content}
        ]

        full_response = ""
        start_time = time.time()

        try:
            # Initialize partial record if not exists
            if not existing:
                self.save_assistant_message(
                    db=db,
                    snapshot_id=snapshot_id,
                    content="",
                    client_message_id=client_message_id,
                    is_complete=False
                )

            # 4. Stream from LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                timeout=self.timeout
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"data: {json.dumps({'content': content})}\n\n"

            yield "data: [DONE]\n\n"

            # 5. Final Save (Complete)
            self.save_assistant_message(
                db=db,
                snapshot_id=snapshot_id,
                content=full_response,
                client_message_id=client_message_id,
                is_complete=True
            )

            log_llm_call(
                provider="openai",
                model=self.model,
                purpose="coach_init_greeting",
                duration_seconds=time.time() - start_time,
                success=True
            )

        except Exception as e:
            logger.error(f"Coach Init API call failed: {e}")
            raise ValueError(f"Coach Init API call failed: {e}") from e

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
        Stream coach response using SSE format with full logic (AD-4, AD-9).

        1. Idempotency Check: If complete assistant message exists for this ID, return it.
        2. Reconnect Logic: If partial assistant message exists, restart and update.
        3. Turn Limit: Atomically increment turn count.
        4. LLM Generation: Stream from OpenRouter.
        5. Persistence: Update-In-Place DB record.
        """
        # 1. & 2. Idempotency and Reconnect Logic
        existing_assistant = self.get_existing_assistant_message(db, snapshot_id, client_message_id)
        
        if existing_assistant and existing_assistant.is_complete:
            logger.info(f"Duplicate request detected for {client_message_id}, returning existing response.")
            sse_chunk = json.dumps({"content": existing_assistant.content})
            yield f"data: {sse_chunk}\n\n"
            yield "data: [DONE]\n\n"
            return

        # 3. Get and validate snapshot
        snapshot = self.get_snapshot_context(db, snapshot_id)

        # 4. Atomic Turn Increment (only for new messages, not for reconnects)
        if not existing_assistant:
            success = self.increment_chat_turn(db, snapshot_id)
            if not success:
                # This should have been caught by get_snapshot_context, 
                # but atomic check is the final authority.
                raise MaxTurnsExceededError(f"Turn limit reached for snapshot {snapshot_id}")

        # 5. Save/Verify User Message
        try:
            self.save_user_message(
                db=db,
                snapshot_id=snapshot_id,
                content=user_message,
                selected_metrics=selected_metrics,
                client_message_id=client_message_id
            )
        except Exception:
            # UNIQUE index prevents duplicates, we can safely continue
            pass

        # 6. Build LLM Context
        history_limit = min(settings.chat_history_window, snapshot.chat_turn_count + 1)
        chat_history = self.get_chat_history(db, snapshot_id, limit=history_limit)
        
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

        # 7. Call OpenRouter API with streaming
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        full_response = ""
        start_time = time.time()

        try:
            # Initialize record as incomplete if it doesn't exist
            if not existing_assistant:
                self.save_assistant_message(
                    db=db,
                    snapshot_id=snapshot_id,
                    content="",
                    client_message_id=client_message_id,
                    is_complete=False
                )

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

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"data: {json.dumps({'content': content})}\n\n"

            yield "data: [DONE]\n\n"

            # 8. Final Save (Complete)
            self.save_assistant_message(
                db=db,
                snapshot_id=snapshot_id,
                content=full_response,
                client_message_id=client_message_id,
                is_complete=True
            )

            log_llm_call(
                provider="openai",
                model=self.model,
                purpose="coach_chat",
                duration_seconds=time.time() - start_time,
                success=True
            )

        except Exception as e:
            logger.error(f"Coach API call failed: {e}")
            log_llm_call(
                provider="openai",
                model=self.model,
                purpose="coach_chat",
                duration_seconds=time.time() - start_time,
                success=False,
                error=str(e)
            )
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


def increment_chat_turn(
    db: Session,
    snapshot_id: str
) -> bool:
    """
    Increment chat turn count using global service instance.

    Args:
        db: Database session
        snapshot_id: Snapshot ID

    Returns:
        True if incremented, False otherwise
    """
    return coach_service.increment_chat_turn(db, snapshot_id)


def get_remaining_turns(
    db: Session,
    snapshot_id: str
) -> int:
    """
    Get remaining turns using global service instance.

    Args:
        db: Database session
        snapshot_id: Snapshot ID

    Returns:
        Number of turns remaining
    """
    return coach_service.get_remaining_turns(db, snapshot_id)


async def handle_init_greeting(
    db: Session,
    snapshot_id: str,
    selected_metrics: list[str]
) -> AsyncGenerator[str, None]:
    """
    Handle init greeting using global service instance.

    Args:
        db: Database session
        snapshot_id: Snapshot ID
        selected_metrics: List of metric slugs

    Yields:
        SSE response chunks
    """
    async for chunk in coach_service.handle_init_greeting(db, snapshot_id, selected_metrics):
        yield chunk
