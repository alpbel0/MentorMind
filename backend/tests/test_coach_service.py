"""
MentorMind - Coach Service Tests

Test suite for Coach Chat Service implementation.

Reference: Task 14.2 - Coach Chat Service Implementation
"""

import json
import uuid
import pytest
from unittest.mock import MagicMock, Mock, patch

from backend.services.coach_service import (
    CoachService,
    ChatNotAvailableError,
    MaxTurnsExceededError,
    InvalidSelectedMetricsError,
    generate_message_id,
    get_snapshot_context,
    get_chat_history,
    generate_init_greeting,
    coach_service,
)


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
        # Format: msg_YYYYMMDD_HHMMSS_randomhex (8 + 1 + 6 + 1 + 12 = ~28 chars)
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
        from backend.models.chat_message import ChatMessage

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
        from backend.models.chat_message import ChatMessage

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

    def test_increment_chat_turn(self, coach_service_instance, db_session, make_snapshot):
        """Test incrementing chat turn count."""
        snapshot = make_snapshot(chat_turn_count=0)

        result = coach_service_instance.increment_chat_turn(db_session, snapshot.id)

        assert result.chat_turn_count == 1

    def test_increment_multiple_times(self, coach_service_instance, db_session, make_snapshot):
        """Test incrementing turn count multiple times."""
        snapshot = make_snapshot(chat_turn_count=0)

        coach_service_instance.increment_chat_turn(db_session, snapshot.id)
        coach_service_instance.increment_chat_turn(db_session, snapshot.id)
        result = coach_service_instance.increment_chat_turn(db_session, snapshot.id)

        assert result.chat_turn_count == 3

    def test_increment_nonexistent_snapshot(self, coach_service_instance, db_session):
        """Test incrementing for non-existent snapshot."""
        with pytest.raises(Exception):
            coach_service_instance.increment_chat_turn(db_session, "nonexistent")


# =====================================================
# Test Message Persistence
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
            client_message_id="client-uuid-123"
        )

        assert message.role == "user"
        assert message.content == "Test message"
        assert message.selected_metrics == ["truthfulness", "clarity"]
        assert message.client_message_id == "client-uuid-123"

    def test_save_user_message_generates_id(self, coach_service_instance, db_session, make_snapshot):
        """Test that saving generates unique message ID."""
        snapshot = make_snapshot()

        msg1 = coach_service_instance.save_user_message(
            db=db_session,
            snapshot_id=snapshot.id,
            content="Message 1",
            selected_metrics=["truthfulness"],
            client_message_id="client-1"
        )

        msg2 = coach_service_instance.save_user_message(
            db=db_session,
            snapshot_id=snapshot.id,
            content="Message 2",
            selected_metrics=["clarity"],
            client_message_id="client-2"
        )

        assert msg1.id != msg2.id


class TestSaveAssistantMessage:
    """Tests for save_assistant_message method."""

    def test_save_assistant_message(self, coach_service_instance, db_session, make_snapshot):
        """Test saving an assistant message."""
        snapshot = make_snapshot()
        client_msg_id = str(uuid.uuid4())

        message = coach_service_instance.save_assistant_message(
            db=db_session,
            snapshot_id=snapshot.id,
            content="Assistant response",
            client_message_id=client_msg_id,
            is_complete=True
        )

        assert message.role == "assistant"
        assert message.content == "Assistant response"
        assert message.client_message_id == client_msg_id
        assert message.is_complete is True
        assert message.selected_metrics is None

    def test_save_assistant_message_streaming(self, coach_service_instance, db_session, make_snapshot):
        """Test saving assistant message with is_complete=False."""
        snapshot = make_snapshot()
        client_msg_id = str(uuid.uuid4())

        message = coach_service_instance.save_assistant_message(
            db=db_session,
            snapshot_id=snapshot.id,
            content="Partial response",
            client_message_id=client_msg_id,
            is_complete=False
        )

        assert message.client_message_id == client_msg_id
        assert message.is_complete is False


# =====================================================
# Test Init Greeting Generation
# =====================================================

class TestGenerateInitGreeting:
    """Tests for generate_init_greeting method."""

    def test_generate_init_greeting(self, coach_service_instance, db_session, make_snapshot):
        """Test generating init greeting."""
        snapshot = make_snapshot(
            question="What is 2+2?",
            model_answer="The answer is 5.",
            user_scores_json={"truthfulness": {"score": 4, "reasoning": "Good"}},
            judge_scores_json={"truthfulness": {"score": 5, "rationale": "Perfect"}},
            evidence_json=None
        )

        greeting = coach_service_instance.generate_init_greeting(
            db=db_session,
            snapshot_id=snapshot.id,
            selected_metrics=["truthfulness"]
        )

        assert isinstance(greeting, str)
        assert len(greeting) > 0
        # Should contain Turkish text
        assert "değerlendirmeyi" in greeting.lower() or "metrik" in greeting.lower()

    def test_generate_init_greeting_invalid_metric(self, coach_service_instance, db_session, make_snapshot):
        """Test that invalid metric raises error."""
        snapshot = make_snapshot()

        with pytest.raises(InvalidSelectedMetricsError):
            coach_service_instance.generate_init_greeting(
                db=db_session,
                snapshot_id=snapshot.id,
                selected_metrics=["invalid_metric"]
            )

    def test_generate_init_greeting_multiple_metrics(self, coach_service_instance, db_session, make_snapshot):
        """Test generating greeting with multiple metrics."""
        snapshot = make_snapshot(
            user_scores_json={
                "truthfulness": {"score": 4},
                "clarity": {"score": 3}
            },
            judge_scores_json={
                "truthfulness": {"score": 5},
                "clarity": {"score": 4}
            }
        )

        greeting = coach_service_instance.generate_init_greeting(
            db=db_session,
            snapshot_id=snapshot.id,
            selected_metrics=["truthfulness", "clarity"]
        )

        assert isinstance(greeting, str)
        assert len(greeting) > 0


# =====================================================
# Test Stream Coach Response
# =====================================================

class TestStreamCoachResponse:
    """Tests for stream_coach_response method."""

    @pytest.mark.asyncio
    async def test_stream_response_success(self, coach_service_instance, db_session, make_snapshot):
        """Test successful streaming response."""
        from unittest.mock import AsyncMock

        snapshot = make_snapshot(
            question="Test question?",
            model_answer="Test answer.",
            user_scores_json={"truthfulness": {"score": 4}},
            judge_scores_json={"truthfulness": {"score": 5}},
            evidence_json=None
        )

        # Mock the streaming response
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta.content = "Hello"

        mock_response = Mock()
        mock_response.__iter__ = Mock(return_value=iter([mock_chunk, mock_chunk]))

        mock_stream = Mock()
        mock_stream.chat.completions.create = Mock(return_value=mock_response)

        with patch.object(coach_service_instance, "client", mock_stream):
            chunks = []
            async for chunk in coach_service_instance.stream_coach_response(
                db=db_session,
                snapshot_id=snapshot.id,
                user_message="What is truthfulness?",
                selected_metrics=["truthfulness"],
                client_message_id="client-uuid"
            ):
                chunks.append(chunk)

            # Should have content chunks + [DONE]
            assert len(chunks) >= 2
            assert any("Hello" in c for c in chunks)
            assert any("[DONE]" in c for c in chunks)

    @pytest.mark.asyncio
    async def test_stream_response_max_turns_exceeded(self, coach_service_instance, db_session, make_snapshot):
        """Test that streaming fails when max turns exceeded."""
        snapshot = make_snapshot(
            status="active",
            chat_turn_count=15,
            max_chat_turns=15
        )

        with pytest.raises(MaxTurnsExceededError):
            async for _ in coach_service_instance.stream_coach_response(
                db=db_session,
                snapshot_id=snapshot.id,
                user_message="Test",
                selected_metrics=["truthfulness"],
                client_message_id="client-uuid"
            ):
                pass


# =====================================================
# Test Live API (requires OPENROUTER_API_KEY)
# =====================================================

@pytest.mark.live_api
class TestCoachServiceLiveAPI:
    """Live API tests requiring OPENROUTER_API_KEY."""

    def test_live_init_greeting(self, db_session, make_snapshot):
        """Test init greeting with real service instance."""
        snapshot = make_snapshot(
            question="What is the capital of France?",
            model_answer="The capital of France is Paris.",
            user_scores_json={"truthfulness": {"score": 5, "reasoning": "Correct"}},
            judge_scores_json={"truthfulness": {"score": 5, "rationale": "Perfect"}},
            evidence_json=None,
            status="active"
        )

        greeting = coach_service.generate_init_greeting(
            db=db_session,
            snapshot_id=snapshot.id,
            selected_metrics=["truthfulness"]
        )

        assert isinstance(greeting, str)
        assert len(greeting) > 20  # Should have substantial content

    @pytest.mark.asyncio
    async def test_live_stream_response_short(self, db_session, make_snapshot):
        """Test live streaming with simple question."""
        snapshot = make_snapshot(
            question="What is 2+2?",
            model_answer="The answer is 4.",
            user_scores_json={"truthfulness": {"score": 5, "reasoning": "Correct"}},
            judge_scores_json={"truthfulness": {"score": 5, "rationale": "Perfect"}},
            evidence_json=None,
            status="active"
        )

        chunks = []
        async for chunk in coach_service.stream_coach_response(
            db=db_session,
            snapshot_id=snapshot.id,
            user_message="Why is truthfulness important?",
            selected_metrics=["truthfulness"],
            client_message_id="test-client-uuid-123"
        ):
            chunks.append(chunk)
            if len(chunks) > 5:  # Limit for testing
                break

        assert len(chunks) > 0


# =====================================================
# Test Global Service Instance
# =====================================================

class TestGlobalServiceInstance:
    """Tests for global convenience functions."""

    def test_global_get_snapshot_context(self, db_session, make_snapshot):
        """Test global get_snapshot_context function."""
        snapshot = make_snapshot()

        result = get_snapshot_context(db_session, snapshot.id)

        assert result.id == snapshot.id

    def test_global_get_chat_history(self, db_session, make_snapshot):
        """Test global get_chat_history function."""
        snapshot = make_snapshot()

        history = get_chat_history(db_session, snapshot.id)

        assert isinstance(history, list)

    def test_global_generate_init_greeting(self, db_session, make_snapshot):
        """Test global generate_init_greeting function."""
        snapshot = make_snapshot(
            user_scores_json={"truthfulness": {"score": 4}},
            judge_scores_json={"truthfulness": {"score": 5}},
            evidence_json=None
        )

        greeting = generate_init_greeting(
            db_session,
            snapshot.id,
            ["truthfulness"]
        )

        assert isinstance(greeting, str)
        assert len(greeting) > 0
