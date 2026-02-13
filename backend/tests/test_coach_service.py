"""
MentorMind - Coach Service Tests

Test suite for Coach Chat Service implementation.

Reference: Task 14.2 - Coach Chat Service Implementation
"""

import json
import uuid
import pytest
import asyncio
from unittest.mock import MagicMock, Mock, patch
from sqlalchemy.orm import Session

from backend.services.coach_service import (
    CoachService,
    ChatNotAvailableError,
    MaxTurnsExceededError,
    InvalidSelectedMetricsError,
    generate_message_id,
    get_snapshot_context,
    get_chat_history,
    handle_init_greeting,
    increment_chat_turn,
    get_remaining_turns,
    coach_service,
)
from backend.models.chat_message import ChatMessage


# =====================================================
# Test Fixtures
# =====================================================

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch("backend.services.coach_service.openai.OpenAI") as mock:
        yield mock


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("backend.services.coach_service.settings") as mock:
        mock.coach_model = "openai/gpt-4o-mini"
        mock.openrouter_api_key = "test-key"
        mock.max_chat_turns = 15
        mock.chat_history_window = 6
        mock.openrouter_base_url = "https://openrouter.ai/api/v1"
        yield mock


@pytest.fixture
def coach_service_instance(mock_openai_client, mock_settings):
    """Create a CoachService instance for testing."""
    return CoachService(api_key="test-key", timeout=60)


# =====================================================
# Test Message ID Generation
# =====================================================

class TestMessageIDGeneration:
    """Tests for generate_message_id function."""

    def test_generate_message_id_format(self):
        """Test that generated ID has correct format."""
        message_id = generate_message_id()

        assert message_id.startswith("msg_")
        # Format: msg_YYYYMMDD_HHMMSS_randomhex
        assert len(message_id) > 20

    def test_generate_message_id_unique(self):
        """Test that generated IDs are unique."""
        ids = [generate_message_id() for _ in range(100)]
        assert len(set(ids)) == 100  # All unique


# =====================================================
# Test CoachService Initialization
# =====================================================

class TestCoachServiceInit:
    """Tests for CoachService.__init__ method."""

    def test_init_with_defaults(self, mock_openai_client):
        """Test initialization with default values."""
        with patch("backend.services.coach_service.settings") as mock_settings:
            mock_settings.openrouter_api_key = "default-key"
            mock_settings.coach_model = "openai/gpt-4o-mini"
            mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"

            service = CoachService()

            assert service.api_key == "default-key"
            assert service.model == "openai/gpt-4o-mini"
            assert service.timeout == 60
            mock_openai_client.assert_called_once()

    def test_init_with_custom_values(self, mock_openai_client):
        """Test initialization with custom values."""
        service = CoachService(api_key="custom-key", timeout=120)

        assert service.api_key == "custom-key"
        assert service.timeout == 120


# =====================================================
# Test Snapshot Context Retrieval
# =====================================================

class TestGetSnapshotContext:
    """Tests for get_snapshot_context method."""

    def test_get_valid_snapshot(self, coach_service_instance, db_session, make_snapshot):
        """Test retrieving a valid snapshot."""
        snapshot = make_snapshot(status="active", chat_turn_count=0)

        result = coach_service_instance.get_snapshot_context(db_session, snapshot.id)

        assert result.id == snapshot.id
        assert result.status == "active"

    def test_get_nonexistent_snapshot(self, coach_service_instance, db_session):
        """Test retrieving a non-existent snapshot."""
        with pytest.raises(Exception) as exc_info:
            coach_service_instance.get_snapshot_context(db_session, "nonexistent")

        assert "Snapshot not found" in str(exc_info.value)

    def test_get_snapshot_max_turns_exceeded(self, coach_service_instance, db_session, make_snapshot):
        """Test that max turns exceeded raises error."""
        snapshot = make_snapshot(status="active", chat_turn_count=15, max_chat_turns=15)

        with pytest.raises(MaxTurnsExceededError) as exc_info:
            coach_service_instance.get_snapshot_context(db_session, snapshot.id)

        assert "Maximum chat turns exceeded" in str(exc_info.value)

    def test_get_snapshot_inactive_status(self, coach_service_instance, db_session, make_snapshot):
        """Test that inactive status raises error."""
        snapshot = make_snapshot(status="archived", chat_turn_count=0)

        with pytest.raises(ChatNotAvailableError) as exc_info:
            coach_service_instance.get_snapshot_context(db_session, snapshot.id)

        assert "not available" in str(exc_info.value)


# =====================================================
# Test Chat History Management
# =====================================================

class TestGetChatHistory:
    """Tests for get_chat_history method."""

    def test_get_empty_history(self, coach_service_instance, db_session, make_snapshot):
        """Test getting chat history when no messages exist."""
        snapshot = make_snapshot()

        history = coach_service_instance.get_chat_history(db_session, snapshot.id)

        assert history == []

    def test_get_chat_history_with_limit(self, coach_service_instance, db_session, make_snapshot):
        """Test getting chat history with custom limit."""
        snapshot = make_snapshot()

        # Create 3 messages
        for i in range(3):
            msg = ChatMessage(
                id=f"msg_test_{i}",
                client_message_id=f"client_{i}",
                snapshot_id=snapshot.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                is_complete=True
            )
            db_session.add(msg)
        db_session.flush()

        history = coach_service_instance.get_chat_history(
            db_session, snapshot.id, limit=2
        )

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Message 0"

    def test_get_chat_history_default_limit(self, coach_service_instance, db_session, make_snapshot):
        """Test that default limit from settings is used."""
        snapshot = make_snapshot()

        # Create 10 messages
        for i in range(10):
            msg = ChatMessage(
                id=f"msg_test_{i}",
                client_message_id=f"client_{i}",
                snapshot_id=snapshot.id,
                role="user",
                content=f"Message {i}",
                is_complete=True
            )
            db_session.add(msg)
        db_session.flush()

        history = coach_service_instance.get_chat_history(db_session, snapshot.id)

        # Default limit is settings.chat_history_window = 6
        assert len(history) == 6
        assert "id" in history[0]
        assert "created_at" in history[0]
        assert "snapshot_id" in history[0]
        assert "role" in history[0]


class TestIncrementChatTurn:
    """Tests for increment_chat_turn method."""

    def test_increment_chat_turn_success(self, coach_service_instance, db_session, make_snapshot):
        """Test incrementing chat turn count atomically."""
        snapshot = make_snapshot(chat_turn_count=0, max_chat_turns=15)

        success = coach_service_instance.increment_chat_turn(db_session, snapshot.id)

        db_session.refresh(snapshot)
        assert success is True
        assert snapshot.chat_turn_count == 1

    def test_increment_multiple_times(self, coach_service_instance, db_session, make_snapshot):
        """Test incrementing turn count multiple times."""
        snapshot = make_snapshot(chat_turn_count=0, max_chat_turns=15)

        coach_service_instance.increment_chat_turn(db_session, snapshot.id)
        coach_service_instance.increment_chat_turn(db_session, snapshot.id)
        success = coach_service_instance.increment_chat_turn(db_session, snapshot.id)

        db_session.refresh(snapshot)
        assert success is True
        assert snapshot.chat_turn_count == 3

    def test_increment_limit_reached(self, coach_service_instance, db_session, make_snapshot):
        """Test that incrementing fails when limit is reached."""
        snapshot = make_snapshot(chat_turn_count=5, max_chat_turns=5)

        success = coach_service_instance.increment_chat_turn(db_session, snapshot.id)

        db_session.refresh(snapshot)
        assert success is False
        assert snapshot.chat_turn_count == 5

    def test_increment_nonexistent_snapshot(self, coach_service_instance, db_session):
        """Test incrementing for non-existent snapshot."""
        success = coach_service_instance.increment_chat_turn(db_session, "nonexistent")
        assert success is False


class TestRemainingTurns:
    """Tests for get_remaining_turns method."""

    def test_get_remaining_turns(self, coach_service_instance, db_session, make_snapshot):
        """Test getting remaining turn count."""
        snapshot = make_snapshot(chat_turn_count=3, max_chat_turns=15)
        
        remaining = coach_service_instance.get_remaining_turns(db_session, snapshot.id)
        assert remaining == 12

    def test_get_remaining_turns_limit_reached(self, coach_service_instance, db_session, make_snapshot):
        """Test getting remaining turns when limit reached."""
        snapshot = make_snapshot(chat_turn_count=15, max_chat_turns=15)
        
        remaining = coach_service_instance.get_remaining_turns(db_session, snapshot.id)
        assert remaining == 0


# =====================================================
# Test Message Persistence & Update-In-Place
# =====================================================

class TestSaveUserMessage:
    """Tests for save_user_message method."""

    def test_save_user_message(self, coach_service_instance, db_session, make_snapshot):
        """Test saving a user message."""
        snapshot = make_snapshot()

        message = coach_service_instance.save_user_message(
            db=db_session,
            snapshot_id=snapshot.id,
            content="Test message",
            selected_metrics=["truthfulness", "clarity"],
            client_message_id=str(uuid.uuid4())
        )

        assert message.role == "user"
        assert message.content == "Test message"
        assert message.selected_metrics == ["truthfulness", "clarity"]

    def test_save_user_message_idempotency(self, coach_service_instance, db_session, make_snapshot):
        """Test that duplicate user messages are prevented by DB constraint."""
        snapshot = make_snapshot()
        client_id = str(uuid.uuid4())

        coach_service_instance.save_user_message(
            db=db_session,
            snapshot_id=snapshot.id,
            content="Msg 1",
            selected_metrics=["truthfulness"],
            client_message_id=client_id
        )

        # Second attempt with same client_id and role should fail
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            coach_service_instance.save_user_message(
                db=db_session,
                snapshot_id=snapshot.id,
                content="Msg 2",
                selected_metrics=["truthfulness"],
                client_message_id=client_id
            )


class TestSaveAssistantMessage:
    """Tests for save_assistant_message method with Update-In-Place."""

    def test_save_assistant_message_new(self, coach_service_instance, db_session, make_snapshot):
        """Test saving a new assistant message."""
        snapshot = make_snapshot()
        client_id = str(uuid.uuid4())

        message = coach_service_instance.save_assistant_message(
            db=db_session,
            snapshot_id=snapshot.id,
            content="Response",
            client_message_id=client_id,
            is_complete=True
        )

        assert message.role == "assistant"
        assert message.content == "Response"
        assert message.client_message_id == client_id

    def test_update_in_place_partial_message(self, coach_service_instance, db_session, make_snapshot):
        """Test that partial messages are updated instead of creating new ones."""
        snapshot = make_snapshot()
        client_id = str(uuid.uuid4())

        # 1. Create partial message
        msg1 = coach_service_instance.save_assistant_message(
            db=db_session,
            snapshot_id=snapshot.id,
            content="Partial...",
            client_message_id=client_id,
            is_complete=False
        )
        msg1_id = msg1.id

        # 2. Update same message (Update-In-Place)
        msg2 = coach_service_instance.save_assistant_message(
            db=db_session,
            snapshot_id=snapshot.id,
            content="Complete response",
            client_message_id=client_id,
            is_complete=True
        )

        assert msg2.id == msg1_id  # Same ID
        assert msg2.content == "Complete response"
        assert msg2.is_complete is True


# =====================================================
# Test Stream Coach Response (Logic Polish)
# =====================================================

class TestStreamCoachResponseLogic:
    """Tests for stream_coach_response with full logic (AD-4, AD-9)."""

    @pytest.mark.asyncio
    async def test_stream_response_idempotency(self, coach_service_instance, db_session, make_snapshot):
        """Test that duplicate requests return existing complete response."""
        snapshot = make_snapshot()
        client_id = str(uuid.uuid4())
        
        # Manually create a complete assistant message
        msg = ChatMessage(
            id="msg_existing",
            client_message_id=client_id,
            snapshot_id=snapshot.id,
            role="assistant",
            content="Existing complete answer",
            is_complete=True
        )
        db_session.add(msg)
        db_session.commit()

        # Mock the client so we can verify it was NOT called
        with patch.object(coach_service_instance, "client") as mock_client:
            chunks = []
            async for chunk in coach_service_instance.stream_coach_response(
                db=db_session,
                snapshot_id=snapshot.id,
                user_message="Test",
                selected_metrics=["truthfulness"],
                client_message_id=client_id
            ):
                chunks.append(chunk)

            # Should return existing content
            assert any("Existing complete answer" in c for c in chunks)
            # Should NOT call LLM
            mock_client.chat.completions.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_stream_response_reconnect_update_in_place(self, coach_service_instance, db_session, make_snapshot):
        """Test that partial messages trigger a restart and update existing record."""
        snapshot = make_snapshot()
        client_id = str(uuid.uuid4())
        
        # 1. Create partial message
        msg = ChatMessage(
            id="msg_partial",
            client_message_id=client_id,
            snapshot_id=snapshot.id,
            role="assistant",
            content="I was cut off...",
            is_complete=False
        )
        db_session.add(msg)
        db_session.commit()

        # 2. Mock streaming response
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta.content = "Restarted answer"
        mock_response = Mock()
        mock_response.__iter__ = Mock(return_value=iter([mock_chunk]))
        
        with patch.object(coach_service_instance.client.chat.completions, "create", return_value=mock_response):
            async for _ in coach_service_instance.stream_coach_response(
                db=db_session,
                snapshot_id=snapshot.id,
                user_message="Test",
                selected_metrics=["truthfulness"],
                client_message_id=client_id
            ):
                pass

            # 3. Verify record was updated in place
            updated_msg = db_session.query(ChatMessage).filter_by(id="msg_partial").first()
            assert updated_msg.content == "Restarted answer"
            assert updated_msg.is_complete is True


# =====================================================
# Test Global Service Instance
# =====================================================

class TestGlobalServiceInstance:
    """Tests for global convenience functions."""

    def test_global_increment_turn(self, db_session, make_snapshot):
        """Test global increment_chat_turn function."""
        snapshot = make_snapshot(chat_turn_count=0)
        success = increment_chat_turn(db_session, snapshot.id)
        assert success is True

    def test_global_remaining_turns(self, db_session, make_snapshot):
        """Test global get_remaining_turns function."""
        snapshot = make_snapshot(chat_turn_count=5, max_chat_turns=15)
        remaining = get_remaining_turns(db_session, snapshot.id)
        assert remaining == 10
