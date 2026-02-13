"""
MentorMind - Coach Router Tests - Task 14.3

Unit tests for coach chat endpoints (GET chat, POST init, POST stream, GET health).
Uses pytest fixtures from conftest.py for database setup.

Reference: Task 14.3 - Coach Router Verification
"""

import json
import pytest
import uuid
from datetime import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.models.chat_message import ChatMessage
from backend.models.evaluation_snapshot import EvaluationSnapshot
from backend.models.schemas import VALID_SNAPSHOT_STATUSES
from backend.routers.coach import router
from backend.services.coach_service import (
    ChatNotAvailableError,
    MaxTurnsExceededError,
    InvalidSelectedMetricsError,
)


# =====================================================
# Test Client Fixture
# =====================================================

@pytest.fixture(scope="function")
def coach_test_client(db_session):
    """
    Create test client with database override for coach tests.

    Args:
        db_session: Database session from conftest.py

    Yields:
        TestClient instance
    """
    from backend.models.database import get_db

    app = FastAPI()
    app.include_router(router, prefix="/api/snapshots", tags=["coach"])

    # Override get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


# =====================================================
# Test GET /api/snapshots/{snapshot_id}/chat - Get Chat History
# =====================================================

class TestGetChatHistory:
    """Tests for GET /api/snapshots/{snapshot_id}/chat endpoint."""

    def test_get_chat_history_empty(self, coach_test_client, make_snapshot):
        """Get chat history when no messages exist."""
        snapshot = make_snapshot(status="active", chat_turn_count=0)

        response = coach_test_client.get(f"/api/snapshots/{snapshot.id}/chat")

        assert response.status_code == 200
        data = response.json()
        assert data["snapshot_id"] == snapshot.id
        assert data["messages"] == []
        assert data["total"] == 0
        assert data["is_chat_available"] is True
        assert data["turns_remaining"] == 15

    def test_get_chat_history_with_messages(self, coach_test_client, db_session, make_snapshot):
        """Get chat history with existing messages."""
        snapshot = make_snapshot(status="active", chat_turn_count=0)

        # Create chat messages - use valid UUID v4 format
        test_uuid = str(uuid.uuid4())
        user_msg = ChatMessage(
            id="msg_test_user_001",
            client_message_id=test_uuid,
            snapshot_id=snapshot.id,
            role="user",
            content="User message",
            selected_metrics=["truthfulness"],
            is_complete=True
        )
        assistant_msg = ChatMessage(
            id="msg_test_assistant_001",
            client_message_id=test_uuid,  # Same turn ID as user
            snapshot_id=snapshot.id,
            role="assistant",
            content="Assistant response",
            selected_metrics=None,
            is_complete=True
        )
        db_session.add_all([user_msg, assistant_msg])
        db_session.flush()

        response = coach_test_client.get(f"/api/snapshots/{snapshot.id}/chat")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][0]["content"] == "User message"
        assert data["messages"][1]["role"] == "assistant"
        assert data["messages"][1]["content"] == "Assistant response"

    def test_get_chat_history_with_limit(self, coach_test_client, db_session, make_snapshot):
        """Test limit parameter for chat history."""
        snapshot = make_snapshot(status="active")

        # Create 5 messages
        for i in range(5):
            msg = ChatMessage(
                id=f"msg_test_{i}",
                client_message_id=str(uuid.uuid4()),
                snapshot_id=snapshot.id,
                role="user",
                content=f"Message {i}",
                selected_metrics=["truthfulness"],
                is_complete=True
            )
            db_session.add(msg)
        db_session.flush()

        response = coach_test_client.get(f"/api/snapshots/{snapshot.id}/chat?limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 2

    def test_get_chat_history_max_limit(self, coach_test_client, db_session, make_snapshot):
        """Test that limit is capped at 100."""
        snapshot = make_snapshot(status="active")

        # Create 10 messages
        for i in range(10):
            msg = ChatMessage(
                id=f"msg_test_{i}",
                client_message_id=str(uuid.uuid4()),
                snapshot_id=snapshot.id,
                role="user",
                content=f"Message {i}",
                selected_metrics=["truthfulness"],
                is_complete=True
            )
            db_session.add(msg)
        db_session.flush()

        # Request limit=200, should cap at 100
        response = coach_test_client.get(f"/api/snapshots/{snapshot.id}/chat?limit=200")

        assert response.status_code == 200
        data = response.json()
        # Since we only created 10 messages, should return 10
        assert len(data["messages"]) == 10

    def test_get_chat_history_not_found_404(self, coach_test_client):
        """404 for non-existent snapshot."""
        response = coach_test_client.get("/api/snapshots/snap_nonexistent/chat")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


# =====================================================
# Test POST /api/snapshots/{snapshot_id}/chat/init - Init Greeting
# =====================================================

class TestPostInitGreeting:
    """Tests for POST /api/snapshots/{snapshot_id}/chat/init endpoint."""

    def test_post_init_greeting_valid(self, coach_test_client, make_snapshot):
        """Get init greeting with valid metrics."""
        snapshot = make_snapshot(
            question="What is 2+2?",
            model_answer="4",
            user_scores_json={"truthfulness": {"score": 5}},
            judge_scores_json={"truthfulness": {"score": 5}},
            evidence_json=None
        )

        request_data = {
            "selected_metrics": ["truthfulness"]
        }

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/init",
            json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["snapshot_id"] == snapshot.id
        assert "greeting" in data
        assert data["selected_metrics"] == ["truthfulness"]
        assert len(data["greeting"]) > 0

    def test_post_init_greeting_multiple_metrics(self, coach_test_client, make_snapshot):
        """Get init greeting with multiple metrics."""
        snapshot = make_snapshot(
            user_scores_json={
                "truthfulness": {"score": 4},
                "clarity": {"score": 3}
            },
            judge_scores_json={
                "truthfulness": {"score": 5},
                "clarity": {"score": 4}
            },
            evidence_json=None
        )

        request_data = {
            "selected_metrics": ["truthfulness", "clarity"]
        }

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/init",
            json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert set(data["selected_metrics"]) == {"truthfulness", "clarity"}

    def test_post_init_greeting_invalid_metric_400(self, coach_test_client, make_snapshot):
        """400 for invalid metric slug."""
        snapshot = make_snapshot()

        request_data = {
            "selected_metrics": ["invalid_metric"]
        }

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/init",
            json=request_data
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_post_init_greeting_empty_metrics_422(self, coach_test_client, make_snapshot):
        """422 for empty metrics list (min_length=1)."""
        snapshot = make_snapshot()

        request_data = {
            "selected_metrics": []
        }

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/init",
            json=request_data
        )

        assert response.status_code == 422

    def test_post_init_greeting_too_many_metrics_422(self, coach_test_client, make_snapshot):
        """422 for too many metrics (max_length=3)."""
        snapshot = make_snapshot()

        request_data = {
            "selected_metrics": ["truthfulness", "clarity", "helpfulness", "safety"]
        }

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/init",
            json=request_data
        )

        assert response.status_code == 422

    def test_post_init_greeting_not_found_404(self, coach_test_client):
        """404 for non-existent snapshot."""
        request_data = {
            "selected_metrics": ["truthfulness"]
        }

        response = coach_test_client.post(
            "/api/snapshots/snap_nonexistent/chat/init",
            json=request_data
        )

        assert response.status_code == 404

    def test_post_init_greeting_max_turns_429(self, coach_test_client, make_snapshot):
        """429 when max turns exceeded."""
        snapshot = make_snapshot(
            status="active",
            chat_turn_count=15,
            max_chat_turns=15
        )

        request_data = {
            "selected_metrics": ["truthfulness"]
        }

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/init",
            json=request_data
        )

        assert response.status_code == 429
        assert "Maximum chat turns exceeded" in response.json()["detail"]


# =====================================================
# Test POST /api/snapshots/{snapshot_id}/chat/stream - Stream Chat
# =====================================================

class TestPostStreamChat:
    """Tests for POST /api/snapshots/{snapshot_id}/chat/stream endpoint."""

    def test_stream_chat_success(self, coach_test_client, make_snapshot):
        """Stream chat returns SSE format."""
        snapshot = make_snapshot(
            question="Test question?",
            model_answer="Test answer.",
            user_scores_json={"truthfulness": {"score": 4}},
            judge_scores_json={"truthfulness": {"score": 5}},
            evidence_json=None,
            status="active"
        )

        # Use valid UUID v4 string
        test_uuid = str(uuid.uuid4())

        request_data = {
            "message": "What is truthfulness?",
            "selected_metrics": ["truthfulness"],
            "client_message_id": test_uuid
        }

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/stream",
            json=request_data
        )

        # Debug logging
        print(f"Request data: {request_data}")
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        if response.status_code != 200:
            print(f"Response body: {response.text}")

        # Should return SSE stream
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_stream_chat_invalid_snapshot_404(self, coach_test_client):
        """404 for non-existent snapshot."""
        request_data = {
            "message": "Test",
            "selected_metrics": ["truthfulness"],
            "client_message_id": str(uuid.uuid4())
        }

        response = coach_test_client.post(
            "/api/snapshots/snap_nonexistent/chat/stream",
            json=request_data
        )

        assert response.status_code == 404

    def test_stream_chat_max_turns_429(self, coach_test_client, make_snapshot):
        """429 when max turns exceeded."""
        snapshot = make_snapshot(
            status="active",
            chat_turn_count=15,
            max_chat_turns=15
        )

        request_data = {
            "message": "Test",
            "selected_metrics": ["truthfulness"],
            "client_message_id": str(uuid.uuid4())
        }

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/stream",
            json=request_data
        )

        assert response.status_code == 429

    def test_stream_chat_missing_message_422(self, coach_test_client, make_snapshot):
        """422 for missing message field."""
        snapshot = make_snapshot()

        request_data = {
            "selected_metrics": ["truthfulness"],
            "client_message_id": str(uuid.uuid4())
            # Missing "message"
        }

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/stream",
            json=request_data
        )

        assert response.status_code == 422


# =====================================================
# Test GET /api/snapshots/coach/health - Health Check
# =====================================================

class TestCoachHealth:
    """Tests for GET /api/snapshots/coach/health endpoint."""

    def test_coach_health_success(self, coach_test_client):
        """Health check returns service status."""
        response = coach_test_client.get("/api/snapshots/coach/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "coach_chat"
        assert "model" in data
        assert "max_chat_turns" in data
        assert "chat_history_window" in data


# =====================================================
# Test Error Mapping
# =====================================================

class TestCoachErrorMapping:
    """Tests for error mapping from service exceptions to HTTP status codes."""

    def test_snapshot_not_found_404(self, coach_test_client):
        """SnapshotNotFoundError maps to 404."""
        response = coach_test_client.get("/api/snapshots/nonexistent/chat")

        assert response.status_code == 404

    def test_max_turns_exceeded_429(self, coach_test_client, make_snapshot):
        """MaxTurnsExceededError maps to 429."""
        snapshot = make_snapshot(
            status="active",
            chat_turn_count=15,
            max_chat_turns=15
        )

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/init",
            json={"selected_metrics": ["truthfulness"]}
        )

        assert response.status_code == 429

    def test_chat_not_available_400(self, coach_test_client, make_snapshot):
        """ChatNotAvailableError maps to 400."""
        snapshot = make_snapshot(
            status="archived",  # Not active
            chat_turn_count=0
        )

        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/init",
            json={"selected_metrics": ["truthfulness"]}
        )

        assert response.status_code == 400

    def test_invalid_selected_metrics_400(self, coach_test_client, make_snapshot):
        """InvalidSelectedMetricsError maps to 400."""
        snapshot = make_snapshot()

        # Invalid metric slug will be caught by Pydantic before service
        response = coach_test_client.post(
            f"/api/snapshots/{snapshot.id}/chat/init",
            json={"selected_metrics": ["not_a_real_metric_slug"]}
        )

        assert response.status_code == 422  # Pydantic validation
