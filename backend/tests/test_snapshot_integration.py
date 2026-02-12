"""
Snapshot Integration Tests - Task 13.6

End-to-end integration tests for snapshot workflow.
Tests complete flow from question → response → user_eval → judge_eval → snapshot.

Uses conftest.py fixtures for database setup.
"""

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from backend.models.evaluation_snapshot import EvaluationSnapshot
from backend.models.judge_evaluation import JudgeEvaluation
from backend.services.snapshot_service import (
    create_evaluation_snapshot,
    list_snapshots,
    get_snapshot,
    soft_delete_snapshot,
)
from backend.services.judge_service import judge_service
from backend.constants.metrics import display_name_to_slug


# =====================================================
# Test: Full Workflow Snapshot Creation (Live API)
# =====================================================

class TestFullWorkflowSnapshotCreation:
    """Tests for complete snapshot creation workflow (LIVE API)."""

    @pytest.mark.live_api
    def test_full_workflow_snapshot_creation(
        self,
        db_session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """
        Complete workflow: question → response → user_eval → judge_eval → snapshot
        Uses LIVE OpenAI API call via judge_service.full_judge_evaluation.
        Requires OPENAI_API_KEY in environment.
        """
        # 1. Create test data chain using fixtures
        question = make_question(
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Helpfulness"],
            category="General"
        )
        model_response = make_model_response(
            question_id=question.id,
            response_text="This is a test response for evaluation."
        )
        user_eval = make_user_evaluation(
            response_id=model_response.id,
            evaluations={
                "Truthfulness": {"score": 4, "reasoning": "Seems accurate"},
                "Helpfulness": {"score": 3, "reasoning": "Somewhat helpful"},
                "Safety": {"score": 5, "reasoning": "Safe content"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Clarity": {"score": 4, "reasoning": "Clear enough"},
                "Consistency": {"score": 4, "reasoning": "Consistent"},
                "Efficiency": {"score": 3, "reasoning": "Could be shorter"},
                "Robustness": {"score": 4, "reasoning": "Handles edge cases"}
            }
        )

        # 2. Call full_judge_evaluation (LIVE API)
        # This includes: Stage 1 (with evidence) → Stage 2 → Snapshot creation
        judge_eval_id = judge_service.full_judge_evaluation(
            user_eval_id=user_eval.id,
            db=db_session
        )

        # 3. Verify judge evaluation created
        assert judge_eval_id is not None
        assert judge_eval_id.startswith("judge_")

        # 4. Verify snapshot created (query via ORM)
        from backend.models.evaluation_snapshot import EvaluationSnapshot
        db_snapshot = db_session.query(EvaluationSnapshot).filter(
            EvaluationSnapshot.user_evaluation_id == user_eval.id
        ).first()

        assert db_snapshot is not None
        assert db_snapshot.id.startswith("snap_")
        assert db_snapshot.question_id == question.id
        assert db_snapshot.judge_evaluation_id == judge_eval_id
        assert db_snapshot.primary_metric == display_name_to_slug("Truthfulness")
        assert db_snapshot.status == "active"
        assert db_snapshot.deleted_at is None

        # 5. Verify snapshot service can retrieve it
        snapshot = get_snapshot(db_session, db_snapshot.id)
        assert snapshot is not None
        assert snapshot.judge_meta_score is not None
        assert 1 <= snapshot.judge_meta_score <= 5

        # 6. Verify evidence JSON structure (if Stage 1 returned evidence)
        if snapshot.evidence_json:
            assert isinstance(snapshot.evidence_json, dict)
            # Evidence keys should be slugs
            for key in snapshot.evidence_json.keys():
                assert key in ["truthfulness", "helpfulness", "safety",
                              "bias", "clarity", "consistency", "efficiency", "robustness"]


# =====================================================
# Test: Pagination Edge Cases
# =====================================================

class TestSnapshotPaginationEdgeCases:
    """Tests for pagination edge cases (fixtures only)."""

    def test_list_snapshots_pagination_edge_cases(
        self,
        db_session,
        make_snapshot
    ):
        """Test edge cases: limit=0, limit=100, offset beyond total."""
        # Create 5 snapshots
        for i in range(5):
            make_snapshot(status="active")

        # Test 1: limit=0 returns empty list (but total is still 5)
        snapshots, total = list_snapshots(db_session, limit=0, offset=0)
        assert len(snapshots) == 0
        assert total == 5

        # Test 2: limit=100 returns all (max allowed)
        snapshots, total = list_snapshots(db_session, limit=100, offset=0)
        assert len(snapshots) == 5
        assert total == 5

        # Test 3: offset beyond total returns empty list
        snapshots, total = list_snapshots(db_session, limit=10, offset=100)
        assert len(snapshots) == 0
        assert total == 5

        # Test 4: exact offset returns remaining items
        snapshots, total = list_snapshots(db_session, limit=10, offset=3)
        assert len(snapshots) == 2
        assert total == 5


# =====================================================
# Test: Evidence JSON Serialization
# =====================================================

class TestSnapshotEvidenceSerialization:
    """Tests for evidence JSON handling (fixtures only)."""

    def test_get_snapshot_with_evidence(
        self,
        db_session,
        make_snapshot
    ):
        """
        Verify evidence_json properly serialized in response.
        Tests that nested evidence structure survives DB round-trip.
        """
        # Create snapshot with evidence
        snapshot = make_snapshot(
            status="active",
            evidence_json={
                "truthfulness": [{
                    "quote": "Test quote",
                    "start": 0,
                    "end": 10,
                    "why": "Test reason",
                    "better": "Better answer",
                    "verified": True,
                    "highlight_available": True
                }]
            }
        )

        # Get snapshot via service
        retrieved = get_snapshot(db_session, snapshot.id)

        # Verify evidence structure intact
        assert retrieved is not None
        assert retrieved.evidence_json is not None
        assert "truthfulness" in retrieved.evidence_json

        evidence_item = retrieved.evidence_json["truthfulness"][0]
        assert evidence_item["quote"] == "Test quote"
        assert evidence_item["start"] == 0
        assert evidence_item["end"] == 10
        assert evidence_item["why"] == "Test reason"
        assert evidence_item["better"] == "Better answer"
        assert evidence_item["verified"] is True
        assert evidence_item["highlight_available"] is True


# =====================================================
# Test: Soft Delete Cascade Effects
# =====================================================

class TestSnapshotSoftDeleteCascade:
    """Tests for soft delete effects (fixtures only)."""

    def test_soft_delete_cascade_effects(
        self,
        db_session,
        make_question,
        make_model_response,
        make_user_evaluation,
        make_snapshot
    ):
        """
        Verify soft delete doesn't affect source tables (user_evaluations, judge_evaluations, etc.).
        """
        # Create full data chain
        question = make_question()
        model_response = make_model_response(question_id=question.id)
        user_eval = make_user_evaluation(response_id=model_response.id)
        snapshot = make_snapshot(
            user_evaluation_id=user_eval.id,
            status="active"
        )

        # Verify snapshot exists
        assert get_snapshot(db_session, snapshot.id) is not None

        # Soft delete snapshot
        result = soft_delete_snapshot(db_session, snapshot.id)
        assert result is True

        # Verify snapshot is soft-deleted
        assert get_snapshot(db_session, snapshot.id) is None  # filtered by deleted_at

        # Verify source tables still exist (query raw without filter)
        raw_result = db_session.execute(text(
            "SELECT * FROM evaluation_snapshots WHERE id = :snap_id"
        ), {"snap_id": snapshot.id}).fetchone()
        assert raw_result is not None
        # Row object - use _asdict() or index access
        assert raw_result.deleted_at is not None

        # Verify user_evaluation still exists
        user_check = db_session.execute(text(
            "SELECT id FROM user_evaluations WHERE id = :eval_id"
        ), {"eval_id": user_eval.id}).fetchone()
        assert user_check is not None


# =====================================================
# Test: Concurrent Snapshot Creation (asyncio.gather)
# =====================================================

class TestConcurrentSnapshotCreation:
    """Tests for concurrent snapshot creation (asyncio.gather)."""

    @pytest.mark.asyncio
    async def test_concurrent_snapshot_creation(
        self,
        db_session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """
        Multiple snapshots created concurrently using asyncio.gather.
        Verifies no race conditions in ID generation or database writes.
        Uses TestSessionLocal with test_engine (not SessionLocal).
        """
        # Get test engine from db_session
        test_engine = db_session.bind

        # Pre-create data chains (serial phase)
        data_chains = []
        for i in range(3):
            question = make_question(primary_metric="Truthfulness")
            model_response = make_model_response(question_id=question.id)
            user_eval = make_user_evaluation(response_id=model_response.id)
            data_chains.append((question, model_response, user_eval))

        # Mock stage results (same for all)
        stage1_result = {
            "independent_scores": {
                metric: {"score": 4, "rationale": "OK"}
                for metric in ["Truthfulness", "Helpfulness", "Safety", "Bias",
                              "Clarity", "Consistency", "Efficiency", "Robustness"]
            }
        }
        stage2_result = {
            "alignment_analysis": {},
            "judge_meta_score": 4,
            "overall_feedback": "OK",
            "improvement_areas": [],
            "positive_feedback": [],
            "primary_metric_gap": 0.5,
            "weighted_gap": 0.8,
            "judge_evaluation_id": "judge_concurrent_001"
        }

        # Concurrent snapshot creation
        async def create_snapshot_async(chain, s1_res, s2_res, engine):
            """Run snapshot creation in thread pool with fresh TestSessionLocal."""
            loop = asyncio.get_event_loop()
            question, model_response, user_eval = chain

            # CRITICAL: Create fresh TestSessionLocal for each thread (not SessionLocal!)
            # SessionLocal uses production engine, we need test_engine (mentormind_test)
            TestSessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
            db = TestSessionLocal()

            try:
                snapshot = await loop.run_in_executor(
                    None,
                    lambda: create_evaluation_snapshot(
                        db=db,
                        stage1_result=s1_res,
                        stage2_result=s2_res,
                        user_eval=user_eval,
                        question=question,
                        model_response=model_response
                    )
                )
                db.commit()
                # Access ID immediately while still attached to session
                snapshot_id = snapshot.id
                return snapshot_id
            except Exception as e:
                db.rollback()
                raise
            finally:
                db.close()

        # Run all snapshot creations concurrently
        snapshot_ids = await asyncio.gather(*[
            create_snapshot_async(chain, stage1_result, stage2_result, test_engine)
            for chain in data_chains
        ])

        # Verify all snapshots created (returned IDs are strings)
        assert len(snapshot_ids) == 3

        # Verify unique IDs (no collision)
        assert len(set(snapshot_ids)) == 3

        # Verify all persisted to database (query via main db_session)
        for snapshot_id in snapshot_ids:
            snapshot = get_snapshot(db_session, snapshot_id)
            assert snapshot is not None
            assert snapshot.id.startswith("snap_")


# =====================================================
# Test: Status Transitions (All)
# =====================================================

class TestSnapshotStatusTransitions:
    """Tests for status transition logic (fixtures only)."""

    def test_snapshot_status_transitions(
        self,
        db_session,
        make_snapshot
    ):
        """
        Test ALL status transitions: active → completed → archived → deleted.
        Verifies is_chat_available property changes correctly.
        """
        # Create active snapshot
        snapshot = make_snapshot(
            status="active",
            chat_turn_count=0,
            max_chat_turns=15
        )

        # Initial state: active, chat available
        assert snapshot.status == "active"
        assert snapshot.is_chat_available is True

        # Transition 1: active → completed
        snapshot.status = "completed"
        db_session.commit()
        db_session.refresh(snapshot)

        assert snapshot.status == "completed"
        # Chat NOT available (only active status allows chat)
        assert snapshot.is_chat_available is False

        # Transition 2: completed → archived
        snapshot.status = "archived"
        db_session.commit()
        db_session.refresh(snapshot)

        assert snapshot.status == "archived"
        # Chat NOT available (archived)
        assert snapshot.is_chat_available is False

        # Transition 3: archived → deleted (soft delete)
        result = soft_delete_snapshot(db_session, snapshot.id)
        assert result is True

        # Verify soft-deleted snapshot has status=archived (set by soft_delete)
        # and is_chat_available=False
        db_session.expire(snapshot)
        snapshot = db_session.query(EvaluationSnapshot).filter(
            EvaluationSnapshot.id == snapshot.id
        ).first()

        assert snapshot.status == "archived"
        assert snapshot.deleted_at is not None
        assert snapshot.is_chat_available is False

        # Verify get_snapshot returns None (soft-deleted filtered)
        assert get_snapshot(db_session, snapshot.id) is None

        # Verify list_snapshots excludes deleted
        snapshots, total = list_snapshots(db_session)
        snapshot_ids = [s.id for s in snapshots]
        assert snapshot.id not in snapshot_ids
