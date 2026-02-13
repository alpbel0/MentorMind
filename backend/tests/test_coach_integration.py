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
import pytest_asyncio
import httpx
from fastapi import FastAPI
from sqlalchemy.orm import Session

from backend.models.chat_message import ChatMessage
from backend.models.evaluation_snapshot import EvaluationSnapshot
from backend.routers.coach import router
from backend.models.database import get_db

# Mark all tests in this file as requiring live API and being async
pytestmark = [pytest.mark.live_api, pytest.mark.asyncio]


@pytest_asyncio.fixture(scope="function")
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
        
        # 1. Init Greeting (Streaming)
        # -------------------------------------------------
        greeting_content = ""
        async with async_client.stream(
            "POST",
            f"/api/snapshots/{snapshot_id}/chat/init",
            json={"selected_metrics": ["truthfulness"]}
        ) as greeting_response:
            assert greeting_response.status_code == 200
            assert "text/event-stream" in greeting_response.headers["content-type"]
            
            async for line in greeting_response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        if "content" in chunk:
                            greeting_content += chunk["content"]
                    except json.JSONDecodeError:
                        continue
        
        assert len(greeting_content) > 10
        print(f"\n[INIT GREETING]: {greeting_content[:50]}...")

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
        
        # Should have 3 messages: init greeting + user + assistant
        messages = history_data["messages"]
        assert len(messages) == 3
        
        # Verify init greeting (first assistant message)
        init_msg = messages[0]
        assert init_msg["role"] == "assistant"
        assert init_msg["client_message_id"] == f"init_{snapshot_id}"
        assert len(init_msg["content"]) > 0
        
        # Verify user message
        user_msg = next((m for m in messages if m["role"] == "user"), None)
        assert user_msg is not None
        assert user_msg["content"] == chat_request["message"]
        assert user_msg["client_message_id"] == client_msg_id

        # Verify assistant message (NOT init greeting - filter by client_message_id)
        assistant_msg = next(
            (m for m in messages 
             if m["role"] == "assistant" 
             and m["client_message_id"] != f"init_{snapshot_id}"), 
            None
        )
        assert assistant_msg is not None
        assert assistant_msg["client_message_id"] == client_msg_id
        assert len(assistant_msg["content"]) > 0
        assert assistant_msg["is_complete"] is True
        
        # Verify turn count incremented (via snapshot info in history)
        assert history_data["total"] == 3
        
        # Verify first message is init greeting
        init_greeting = messages[0]
        assert init_greeting["role"] == "assistant"
        assert init_greeting["client_message_id"] == f"init_{snapshot_id}"


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
        """Verify that multiple init calls for same metrics return same greeting (via SSE)."""
        payload = {"selected_metrics": ["truthfulness", "clarity"]}
        
        # First call (streaming)
        greeting1 = ""
        async with async_client.stream(
            "POST",
            f"/api/snapshots/{integration_snapshot.id}/chat/init",
            json=payload
        ) as resp1:
            assert resp1.status_code == 200
            assert "text/event-stream" in resp1.headers["content-type"]
            
            async for line in resp1.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        if "content" in chunk:
                            greeting1 += chunk["content"]
                    except json.JSONDecodeError:
                        continue
        
        # Second call (should return cached, streaming)
        greeting2 = ""
        async with async_client.stream(
            "POST",
            f"/api/snapshots/{integration_snapshot.id}/chat/init",
            json=payload
        ) as resp2:
            assert resp2.status_code == 200
            
            async for line in resp2.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        if "content" in chunk:
                            greeting2 += chunk["content"]
                    except json.JSONDecodeError:
                        continue
        
        assert len(greeting1) > 0
        assert greeting1 == greeting2  # Idempotent
