"""
ChatMessage ORM Model

Chat history for Coach conversations. Uses Shared Turn ID for idempotency.
is_complete enables SSE reconnection with Update-In-Place pattern.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from backend.models.database import Base

if TYPE_CHECKING:
    from backend.models.evaluation_snapshot import EvaluationSnapshot


class ChatMessage(Base):
    """
    ChatMessage ORM Model

    Represents a single message in a Coach Chat conversation.
    Uses Shared Turn ID (client_message_id) for idempotency - both user
    and assistant messages in the same turn share this ID.

    Attributes:
        id: Primary key (custom format: msg_YYYYMMDD_HHMMSS_randomhex)
        client_message_id: Client-generated UUID (Shared Turn ID)
        is_complete: True if message fully delivered, False if streaming
        snapshot_id: Foreign key to evaluation_snapshots table
        role: Message role ('user' or 'assistant')
        content: Message content text
        selected_metrics: Array of metric slugs (user messages only)
        token_count: Token count for analytics
        created_at: Timestamp when message was created
    """

    __tablename__ = "chat_messages"

    # =====================================================
    # Primary Key (custom format - service generated)
    # =====================================================

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    """Custom ID format: msg_YYYYMMDD_HHMMSS_randomhex"""

    # =====================================================
    # Shared Turn ID (for idempotency - AD-4)
    # =====================================================

    client_message_id: Mapped[str] = mapped_column(String(50))
    """
    Client-generated UUID (Shared Turn ID).

    Both user and assistant messages in the same turn share this ID.
    Enables idempotency and deduplication via unique constraint:
    UNIQUE (snapshot_id, client_message_id, role)
    """

    is_complete: Mapped[bool] = mapped_column(Boolean, default=True)
    """
    Completion flag for SSE reconnection (AD-4).

    True: Message fully delivered
    False: Streaming in progress (allows Update-In-Place on reconnect)
    """

    # =====================================================
    # Foreign key to snapshot (ON DELETE CASCADE in DB)
    # =====================================================

    snapshot_id: Mapped[str] = mapped_column(String(50))
    """
    Foreign key to evaluation_snapshots table.

    Note: ForeignKey constraint enforced at database level with
    ON DELETE CASCADE - deleting a snapshot deletes all its messages.
    Not using ORM relationship to avoid circular dependency issues.
    """

    # =====================================================
    # Message content
    # =====================================================

    role: Mapped[str] = mapped_column(String(20))
    """
    Message role: 'user' or 'assistant'.

    Enforced by CHECK constraint at database level:
    CHECK (role IN ('user', 'assistant'))
    """

    content: Mapped[str] = mapped_column(Text, default="")
    """Message content text"""

    # =====================================================
    # Selected metrics (for user messages only)
    # =====================================================

    selected_metrics: Mapped[Optional[list[str]]] = mapped_column(JSONB, nullable=True)
    """
    Array of metric slugs selected for this conversation turn.
    User messages only - NULL for assistant messages.

    Example: ["truthfulness", "clarity"]
    """

    # =====================================================
    # Token count (for analytics)
    # =====================================================

    token_count: Mapped[int] = mapped_column(Integer, default=0)
    """
    Token count for the message.

    Used for analytics and cost tracking.
    """

    # =====================================================
    # Timestamp
    # =====================================================

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    """Timestamp when message was created"""

    # =====================================================
    # Properties
    # =====================================================

    @property
    def is_user_message(self) -> bool:
        """
        Check if this is a user message.

        Returns:
            bool: True if role is 'user', False otherwise
        """
        return self.role == "user"

    @property
    def is_assistant_message(self) -> bool:
        """
        Check if this is an assistant message.

        Returns:
            bool: True if role is 'assistant', False otherwise
        """
        return self.role == "assistant"

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<ChatMessage(id={self.id}, role={self.role}, "
            f"snapshot_id={self.snapshot_id}, is_complete={self.is_complete})>"
        )
