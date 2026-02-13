"""
MentorMind - Coach Integration Tests

Integration tests for Coach Chat endpoints.
Tests the full workflow from snapshot creation to chat interaction.
Requires OPENROUTER_API_KEY to run.

Reference: Task 14.4 - Coach Chat Integration Tests
"""

import asyncio
import json
import uuid
import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.orm import Session

from backend.models.chat_message import ChatMessage
from backend.models.evaluation_snapshot import EvaluationSnapshot
from backend.routers.coach import router
from backend.models.database import get_db

# Mark all tests in this file as requiring live API and being async
pytestmark = [pytest.mark.live_api, pytest.mark.asyncio]


@pytest.fixture(scope="function")
async def async_client(db_session: Session):
    """Create an async httpx client for testing SSE endpoints."""
    app = FastAPI()
    app.include_router(router, prefix="/api/snapshots")

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
def integration_snapshot(db_session: Session, make_snapshot):
    """Create a snapshot for integration testing using the conftest fixture."""
    # make_snapshot is a fixture from conftest.py
    snapshot = make_snapshot(
        id=f"snap_int_{uuid.uuid4().hex[:8]}",
        status="active"
    )
    return snapshot


class TestFullCoachWorkflow:
    """Test full coach workflow: init greeting → chat turn → verify DB."""

    async def test_full_workflow(
        self, 
        async_client: httpx.AsyncClient, 
        db_session: Session, 
        integration_snapshot: EvaluationSnapshot
    ):
        """
        Test complete workflow: init greeting, chat turn, and persistence.
        Uses LIVE OpenAI API via OpenRouter.
        """
        snapshot_id = integration_snapshot.id
        
        # 1. Init Greeting
        # -------------------------------------------------
        greeting_response = await async_client.post(
            f"/api/snapshots/{snapshot_id}/chat/init",
            json={"selected_metrics": ["truthfulness"]}
        )
        
        assert greeting_response.status_code == 200
        data = greeting_response.json()
        assert "greeting" in data
        assert len(data["greeting"]) > 10
        print(f"\n[INIT GREETING]: {data['greeting'][:50]}...")

        # 2. Chat Turn (Streaming)
        # -------------------------------------------------
        client_msg_id = str(uuid.uuid4())
        chat_request = {
            "message": "Neden truthfulness puanım 4?",
            "selected_metrics": ["truthfulness"],
            "client_message_id": client_msg_id
        }
        
        # We use a POST request with stream handling
        async with async_client.stream(
            "POST", 
            f"/api/snapshots/{snapshot_id}/chat/stream",
            json=chat_request
        ) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]
            
            content_chunks = []
            async for line in response.aiter_lines():
                if not line or line.strip() == "":
                    continue
                
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        chunk_json = json.loads(data_str)
                        if "content" in chunk_json:
                            content_chunks.append(chunk_json["content"])
                    except json.JSONDecodeError:
                        continue

            full_reply = "".join(content_chunks)
            assert len(full_reply) > 0
            print(f"[COACH REPLY]: {full_reply[:50]}...")

        # 3. Verify Database Persistence via API
        # -------------------------------------------------
        # Query chat history through API (better integration test)
        history_response = await async_client.get(
            f"/api/snapshots/{snapshot_id}/chat"
        )
        
        assert history_response.status_code == 200
        history_data = history_response.json()
        
        # Should have 2 messages: user + assistant
        messages = history_data["messages"]
        assert len(messages) == 2
        
        # Verify user message
        user_msg = next((m for m in messages if m["role"] == "user"), None)
        assert user_msg is not None
        assert user_msg["content"] == chat_request["message"]
        assert user_msg["client_message_id"] == client_msg_id

        # Verify assistant message
        assistant_msg = next((m for m in messages if m["role"] == "assistant"), None)
        assert assistant_msg is not None
        assert len(assistant_msg["content"]) > 0
        assert assistant_msg["is_complete"] is True
        assert assistant_msg["client_message_id"] == client_msg_id
        
        # Verify turn count incremented (via snapshot info in history)
        assert history_data["total"] == 2


class TestCoachChatRules:
    """Test business rules like turn limits and idempotency."""

    async def test_turn_limit_enforcement(
        self, 
        async_client: httpx.AsyncClient, 
        db_session: Session, 
        integration_snapshot: EvaluationSnapshot
    ):
        """Verify that chat turns are limited to max_chat_turns."""
        # Manually set turn count to max
        integration_snapshot.chat_turn_count = integration_snapshot.max_chat_turns
        db_session.commit()
        
        chat_request = {
            "message": "Too many questions",
            "selected_metrics": ["truthfulness"],
            "client_message_id": str(uuid.uuid4())
        }
        
        # Should return 429 via the router's early validation
        response = await async_client.post(
            f"/api/snapshots/{integration_snapshot.id}/chat/stream",
            json=chat_request
        )
        
        assert response.status_code == 429
        assert "exceeded" in response.text.lower()

    async def test_init_greeting_idempotency(
        self, 
        async_client: httpx.AsyncClient, 
        integration_snapshot: EvaluationSnapshot
    ):
        """Verify that multiple init calls for same metrics return same greeting."""
        payload = {"selected_metrics": ["truthfulness", "clarity"]}
        
        # First call
        resp1 = await async_client.post(
            f"/api/snapshots/{integration_snapshot.id}/chat/init",
            json=payload
        )
        greeting1 = resp1.json()["greeting"]
        
        # Second call
        resp2 = await async_client.post(
            f"/api/snapshots/{integration_snapshot.id}/chat/init",
            json=payload
        )
        greeting2 = resp2.json()["greeting"]
        
        assert greeting1 == greeting2
        assert resp1.status_code == 200
        assert resp2.status_code == 200
