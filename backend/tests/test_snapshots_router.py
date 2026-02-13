"""
Snapshot Router Tests - Task 13.5

Unit tests for snapshot endpoints (GET /, GET /{id}, DELETE /{id}).
Uses pytest fixtures from conftest.py for database setup.
"""

import pytest
from datetime import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.models.evaluation_snapshot import EvaluationSnapshot
from backend.models.schemas import VALID_SNAPSHOT_STATUSES
from backend.routers.snapshots import router


# =====================================================
# Test Client Fixture
# =====================================================

@pytest.fixture(scope="function")
def snapshot_test_client(db_session):
    """
    Create test client with database override for snapshot tests.

    Args:
        db_session: Database session from conftest.py

    Yields:
        TestClient instance
    """
    from backend.models.database import get_db

    app = FastAPI()
    app.include_router(router, prefix="/api/snapshots", tags=["snapshots"])

    # Override get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


# =====================================================
# Test GET /api/snapshots/ - List Snapshots
# =====================================================

class TestListSnapshots:
    """Tests for GET /api/snapshots/ endpoint."""

    def test_list_snapshots_default(self, snapshot_test_client, make_snapshot):
        """List with default params, returns items."""
        # Create a snapshot
        make_snapshot(status="active")

        response = snapshot_test_client.get("/api/snapshots/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["page"] == 1
        assert data["per_page"] == 20

    def test_list_snapshots_with_status_filter(self, snapshot_test_client, make_snapshot):
        """Filter by status='active' returns active snapshots."""
        make_snapshot(status="active")
        make_snapshot(status="completed")

        response = snapshot_test_client.get("/api/snapshots/?status=active")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        # Verify all items have status=active
        for item in data["items"]:
            assert item["status"] == "active"

    def test_list_snapshots_invalid_status(self, snapshot_test_client):
        """Invalid status returns 400."""
        response = snapshot_test_client.get("/api/snapshots/?status=invalid")

        assert response.status_code == 400
        assert "Invalid status" in response.json()["detail"]

    def test_list_snapshots_pagination(self, snapshot_test_client, make_snapshot):
        """Test offset/limit works correctly."""
        # Create multiple snapshots
        for _ in range(5):
            make_snapshot(status="active")

        # First page with limit=2
        response = snapshot_test_client.get("/api/snapshots/?limit=2&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1

        # Second page
        response2 = snapshot_test_client.get("/api/snapshots/?limit=2&offset=2")

        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["items"]) == 2
        assert data2["page"] == 2

    def test_list_snapshots_limit_validation(self, snapshot_test_client):
        """Limit validation rejects invalid values."""
        # limit < 1
        response = snapshot_test_client.get("/api/snapshots/?limit=0")
        assert response.status_code == 400
        assert "limit must be at least 1" in response.json()["detail"]

        # limit > 100
        response = snapshot_test_client.get("/api/snapshots/?limit=101")
        assert response.status_code == 400
        assert "limit cannot exceed 100" in response.json()["detail"]

    def test_list_snapshots_offset_validation(self, snapshot_test_client):
        """Negative offset returns 400."""
        response = snapshot_test_client.get("/api/snapshots/?offset=-1")

        assert response.status_code == 400
        assert "offset cannot be negative" in response.json()["detail"]

    def test_list_snapshots_excludes_deleted(self, snapshot_test_client, db_session):
        """Soft-deleted snapshots not in list."""
        # Create snapshot and soft delete it
        snapshot = EvaluationSnapshot(
            id="snap_deleted_test",
            question_id="q_deleted",
            question="Deleted?",
            model_answer="Yes",
            model_name="openai/gpt-3.5-turbo",
            judge_model="gpt-4o",
            primary_metric="truthfulness",
            bonus_metrics=[],
            category="General",
            user_scores_json={},
            judge_scores_json={},
            evidence_json=None,
            judge_meta_score=3,
            weighted_gap=1.0,
            overall_feedback="Deleted",
            user_evaluation_id="eval_deleted",
            judge_evaluation_id="judge_deleted",
            chat_turn_count=0,
            max_chat_turns=15,
            status="archived",
            deleted_at=datetime.utcnow()
        )
        db_session.add(snapshot)
        db_session.flush()

        # List should not include deleted snapshot
        response = snapshot_test_client.get("/api/snapshots/")

        assert response.status_code == 200
        data = response.json()
        # Verify deleted snapshot is not in items
        item_ids = [item["id"] for item in data["items"]]
        assert "snap_deleted_test" not in item_ids


# =====================================================
# Test GET /api/snapshots/{snapshot_id} - Get Snapshot
# =====================================================

class TestGetSnapshot:
    """Tests for GET /api/snapshots/{snapshot_id} endpoint."""

    def test_get_snapshot_by_id(self, snapshot_test_client, make_snapshot):
        """Get single snapshot successfully."""
        snapshot = make_snapshot(status="active")

        response = snapshot_test_client.get(f"/api/snapshots/{snapshot.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == snapshot.id
        assert data["question"] == snapshot.question
        assert data["model_answer"] == snapshot.model_answer
        assert data["primary_metric"] == snapshot.primary_metric
        assert data["judge_meta_score"] == snapshot.judge_meta_score
        assert "is_chat_available" in data

    def test_get_snapshot_not_found_404(self, snapshot_test_client):
        """404 for non-existent ID."""
        response = snapshot_test_client.get("/api/snapshots/snap_nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_snapshot_deleted_404(self, snapshot_test_client, db_session):
        """404 for soft-deleted snapshot."""
        # Create and soft delete a snapshot
        snapshot = EvaluationSnapshot(
            id="snap_soft_deleted",
            question_id="q_soft_del",
            question="Soft deleted?",
            model_answer="Yes",
            model_name="openai/gpt-3.5-turbo",
            judge_model="gpt-4o",
            primary_metric="truthfulness",
            bonus_metrics=[],
            category="General",
            user_scores_json={},
            judge_scores_json={},
            evidence_json=None,
            judge_meta_score=3,
            weighted_gap=1.0,
            overall_feedback="Soft deleted",
            user_evaluation_id="eval_soft_del",
            judge_evaluation_id="judge_soft_del",
            chat_turn_count=0,
            max_chat_turns=15,
            status="archived",
            deleted_at=datetime.utcnow()
        )
        db_session.add(snapshot)
        db_session.flush()

        # Try to get soft-deleted snapshot
        response = snapshot_test_client.get("/api/snapshots/snap_soft_deleted")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


# =====================================================
# Test DELETE /api/snapshots/{snapshot_id} - Soft Delete
# =====================================================

class TestDeleteSnapshot:
    """Tests for DELETE /api/snapshots/{snapshot_id} endpoint."""

    def test_delete_snapshot_success(self, snapshot_test_client, db_session):
        """Soft delete returns 204."""
        # Create snapshot to delete
        snapshot = EvaluationSnapshot(
            id="snap_to_delete",
            question_id="q_to_delete",
            question="Delete me?",
            model_answer="Yes",
            model_name="openai/gpt-3.5-turbo",
            judge_model="gpt-4o",
            primary_metric="truthfulness",
            bonus_metrics=[],
            category="General",
            user_scores_json={},
            judge_scores_json={},
            evidence_json=None,
            judge_meta_score=3,
            weighted_gap=1.0,
            overall_feedback="Will be deleted",
            user_evaluation_id="eval_to_delete",
            judge_evaluation_id="judge_to_delete",
            chat_turn_count=0,
            max_chat_turns=15,
            status="active",
            deleted_at=None
        )
        db_session.add(snapshot)
        db_session.flush()

        # Delete snapshot
        response = snapshot_test_client.delete("/api/snapshots/snap_to_delete")

        assert response.status_code == 204
        assert response.content == b""

        # Verify deleted_at is set in database
        db_session.expire(snapshot)
        assert snapshot.deleted_at is not None
        assert snapshot.status == "archived"

    def test_delete_snapshot_not_found_404(self, snapshot_test_client):
        """404 when deleting non-existent snapshot."""
        response = snapshot_test_client.delete("/api/snapshots/snap_nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_snapshot_already_deleted_404(self, snapshot_test_client, db_session):
        """404 when deleting already soft-deleted snapshot."""
        # Create and soft delete snapshot
        snapshot = EvaluationSnapshot(
            id="snap_already_deleted",
            question_id="q_already_del",
            question="Already deleted?",
            model_answer="Yes",
            model_name="openai/gpt-3.5-turbo",
            judge_model="gpt-4o",
            primary_metric="truthfulness",
            bonus_metrics=[],
            category="General",
            user_scores_json={},
            judge_scores_json={},
            evidence_json=None,
            judge_meta_score=3,
            weighted_gap=1.0,
            overall_feedback="Already deleted",
            user_evaluation_id="eval_already_del",
            judge_evaluation_id="judge_already_del",
            chat_turn_count=0,
            max_chat_turns=15,
            status="archived",
            deleted_at=datetime.utcnow()
        )
        db_session.add(snapshot)
        db_session.flush()

        # Try to delete already deleted snapshot
        response = snapshot_test_client.delete("/api/snapshots/snap_already_deleted")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
