"""
Tests for Snapshot Service (Task 13.1)

Tests for snapshot creation, ID generation, and slug conversion functions.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from backend.constants.metrics import display_name_to_slug, METRIC_SLUG_MAP
from backend.models.evaluation_snapshot import EvaluationSnapshot
from backend.models.user_evaluation import UserEvaluation
from backend.models.model_response import ModelResponse
from backend.models.question import Question
from backend.services.snapshot_service import (
    generate_snapshot_id,
    convert_user_scores_to_slugs,
    convert_judge_scores_to_slugs,
    convert_evidence_to_slugs,
    create_evaluation_snapshot,
    get_snapshot,
    list_snapshots
)


# =====================================================
# Test 1: generate_snapshot_id()
# =====================================================

class TestGenerateSnapshotId:
    """Tests for snapshot ID generation."""

    def test_id_starts_with_snap_prefix(self):
        """Verify ID starts with 'snap_' prefix."""
        snapshot_id = generate_snapshot_id()
        assert snapshot_id.startswith("snap_")

    def test_id_format_structure(self):
        """Verify ID format: snap_YYYYMMDD_HHMMSS_<hex>"""
        snapshot_id = generate_snapshot_id()
        # Remove prefix
        without_prefix = snapshot_id[5:]

        # Should have timestamp_hex format
        # Note: format is snap_YYYYMMDD_HHMMSS_<hex> which splits to 3 parts
        parts = without_prefix.split("_")
        assert len(parts) == 3  # date, time, hex

        # First part: YYYYMMDD (8 chars)
        date_part = parts[0]
        assert len(date_part) == 8
        assert date_part.isdigit()

        # Second part: HHMMSS (6 chars)
        time_part = parts[1]
        assert len(time_part) == 6
        assert time_part.isdigit()

        # Third part: hex (12 chars from token_hex(6))
        hex_part = parts[2]
        assert len(hex_part) == 12
        int(hex_part, 16)  # Should be valid hex

    def test_ids_are_unique(self):
        """Verify multiple calls generate unique IDs."""
        ids = [generate_snapshot_id() for _ in range(100)]
        assert len(set(ids)) == 100  # All unique


# =====================================================
# Test 2: convert_user_scores_to_slugs()
# =====================================================

class TestConvertUserScoresToSlugs:
    """Tests for user score slug conversion."""

    def test_convert_all_8_metrics(self, db_session: Session):
        """Test conversion with all 8 metrics."""
        user_scores = {
            "Truthfulness": {"score": 4, "reasoning": "Good accuracy"},
            "Helpfulness": {"score": 3, "reasoning": "Somewhat helpful"},
            "Safety": {"score": 5, "reasoning": "Safe content"},
            "Bias": {"score": None, "reasoning": "N/A"},
            "Clarity": {"score": 4, "reasoning": "Clear"},
            "Consistency": {"score": 3, "reasoning": "Mostly consistent"},
            "Efficiency": {"score": 5, "reasoning": "Concise"},
            "Robustness": {"score": 2, "reasoning": "Fails edge cases"}
        }

        result = convert_user_scores_to_slugs(user_scores)

        # Verify all keys converted to slugs
        assert set(result.keys()) == set(METRIC_SLUG_MAP.values())

        # Verify score and reasoning preserved
        assert result["truthfulness"]["score"] == 4
        assert result["truthfulness"]["reasoning"] == "Good accuracy"
        assert result["helpfulness"]["score"] == 3
        assert result["safety"]["score"] == 5
        assert result["bias"]["score"] is None
        assert result["robustness"]["score"] == 2

    def test_unknown_metric_skipped(self, caplog):
        """Test that unknown metrics are skipped with warning."""
        user_scores = {
            "Truthfulness": {"score": 4, "reasoning": "Good"},
            "InvalidMetric": {"score": 3, "reasoning": "Should be skipped"}
        }

        result = convert_user_scores_to_slugs(user_scores)

        # Only valid metric should be in result
        assert "truthfulness" in result
        assert "invalid_metric" not in result
        assert len(result) == 1


# =====================================================
# Test 3: convert_judge_scores_to_slugs()
# =====================================================

class TestConvertJudgeScoresToSlugs:
    """Tests for judge score slug conversion."""

    def test_convert_all_8_metrics(self):
        """Test conversion with all 8 metrics."""
        judge_scores = {
            "Truthfulness": {"score": 5, "rationale": "Excellent catch"},
            "Helpfulness": {"score": 3, "rationale": "Adequate guidance"},
            "Safety": {"score": 5, "rationale": "No issues"},
            "Bias": {"score": 5, "rationale": "Fair"},
            "Clarity": {"score": 4, "rationale": "Mostly clear"},
            "Consistency": {"score": 3, "rationale": "Some inconsistency"},
            "Efficiency": {"score": 4, "rationale": "Good conciseness"},
            "Robustness": {"score": 3, "rationale": "Decent edge handling"}
        }

        result = convert_judge_scores_to_slugs(judge_scores)

        # Verify all keys converted to slugs
        assert set(result.keys()) == set(METRIC_SLUG_MAP.values())

        # Verify score and rationale preserved
        assert result["truthfulness"]["score"] == 5
        assert result["truthfulness"]["rationale"] == "Excellent catch"
        assert result["efficiency"]["score"] == 4

    def test_unknown_metric_skipped(self, caplog):
        """Test that unknown metrics are skipped."""
        judge_scores = {
            "Truthfulness": {"score": 5, "rationale": "Good"},
            "FakeMetric": {"score": 3, "rationale": "Skip me"}
        }

        result = convert_judge_scores_to_slugs(judge_scores)

        assert "truthfulness" in result
        assert "fake_metric" not in result


# =====================================================
# Test 4: convert_evidence_to_slugs()
# =====================================================

class TestConvertEvidenceToSlugs:
    """Tests for evidence slug conversion."""

    def test_convert_evidence_multiple_metrics(self):
        """Test evidence conversion for multiple metrics."""
        raw_evidence = {
            "Truthfulness": [
                {
                    "quote": "The capital of France is Paris.",
                    "start": 0,
                    "end": 30,
                    "why": "Correct fact",
                    "better": "N/A",
                    "verified": True,
                    "highlight_available": True
                }
            ],
            "Clarity": [
                {
                    "quote": "The answer is well-structured.",
                    "start": 50,
                    "end": 80,
                    "why": "Clear explanation",
                    "better": "N/A",
                    "verified": True,
                    "highlight_available": True
                }
            ]
        }

        result = convert_evidence_to_slugs(raw_evidence)

        # Verify keys converted
        assert "truthfulness" in result
        assert "clarity" in result
        assert "Truthfulness" not in result
        assert "Clarity" not in result

        # Verify evidence list structure preserved
        assert len(result["truthfulness"]) == 1
        assert result["truthfulness"][0]["quote"] == "The capital of France is Paris."
        assert result["clarity"][0]["verified"] is True

    def test_unknown_metric_skipped_in_evidence(self):
        """Test unknown metrics skipped in evidence."""
        raw_evidence = {
            "Truthfulness": [{"quote": "test", "start": 0, "end": 4, "why": "test", "better": "test"}],
            "InvalidMetric": [{"quote": "skip", "start": 0, "end": 4, "why": "skip", "better": "skip"}]
        }

        result = convert_evidence_to_slugs(raw_evidence)

        assert "truthfulness" in result
        assert "invalid_metric" not in result


# =====================================================
# Test 5: create_evaluation_snapshot() - Success Case
# =====================================================

class TestCreateEvaluationSnapshot:
    """Tests for snapshot creation."""

    def test_create_snapshot_success(
        self,
        db_session: Session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """Test successful snapshot creation with all fields."""
        # Create test data
        question = make_question(
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Helpfulness"]
        )
        model_response = make_model_response(question_id=question.id)
        user_eval = make_user_evaluation(response_id=model_response.id)

        # Mock stage results
        stage1_result = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 4,
                    "rationale": "Good evaluation",
                    "evidence": [
                        {
                            "quote": "Test evidence",
                            "start": 0,
                            "end": 12,
                            "why": "Test",
                            "better": "Better"
                        }
                    ]
                },
                "Clarity": {"score": 5, "rationale": "Clear"},
                "Helpfulness": {"score": 3, "rationale": "Moderate"},
                "Safety": {"score": 5, "rationale": "Safe"},
                "Bias": {"score": 5, "rationale": "Fair"},
                "Consistency": {"score": 4, "rationale": "Consistent"},
                "Efficiency": {"score": 4, "rationale": "Efficient"},
                "Robustness": {"score": 4, "rationale": "Robust"}
            }
        }

        stage2_result = {
            "judge_meta_score": 5,
            "weighted_gap": 0.3,
            "overall_feedback": "Excellent evaluation!",
            "judge_evaluation_id": "judge_test123"
        }

        # Create snapshot
        snapshot = create_evaluation_snapshot(
            db=db_session,
            stage1_result=stage1_result,
            stage2_result=stage2_result,
            user_eval=user_eval,
            question=question,
            model_response=model_response
        )

        # Verify snapshot created
        assert snapshot is not None
        assert snapshot.id.startswith("snap_")
        assert snapshot.question_id == question.id
        assert snapshot.question == question.question
        assert snapshot.model_answer == model_response.response_text
        assert snapshot.model_name == model_response.model_name

        # Verify slug conversion for primary_metric and bonus_metrics
        assert snapshot.primary_metric == "truthfulness"
        assert set(snapshot.bonus_metrics) == {"clarity", "helpfulness"}

        # Verify user scores converted to slugs
        assert "truthfulness" in snapshot.user_scores_json
        assert "clarity" in snapshot.user_scores_json
        assert "Truthfulness" not in snapshot.user_scores_json

        # Verify judge scores converted to slugs
        assert "truthfulness" in snapshot.judge_scores_json
        assert snapshot.judge_scores_json["truthfulness"]["score"] == 4

        # Verify evidence converted to slugs
        assert snapshot.evidence_json is not None
        assert "truthfulness" in snapshot.evidence_json
        assert "Truthfulness" not in snapshot.evidence_json

        # Verify judge summary
        assert snapshot.judge_meta_score == 5
        assert snapshot.weighted_gap == 0.3
        assert snapshot.overall_feedback == "Excellent evaluation!"
        assert snapshot.judge_evaluation_id == "judge_test123"

        # Verify chat metadata defaults
        assert snapshot.chat_turn_count == 0
        assert snapshot.status == "active"
        assert snapshot.deleted_at is None

        # Verify in database
        db_snapshot = db_session.query(EvaluationSnapshot).filter(
            EvaluationSnapshot.id == snapshot.id
        ).first()
        assert db_snapshot is not None

    def test_create_snapshot_with_empty_evidence(
        self,
        db_session: Session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """Test graceful degradation when evidence is empty."""
        question = make_question(primary_metric="Clarity")
        model_response = make_model_response(question_id=question.id)
        user_eval = make_user_evaluation(response_id=model_response.id)

        # Stage 1 without evidence
        stage1_result = {
            "independent_scores": {
                "Clarity": {"score": 4, "rationale": "Clear"},
                "Helpfulness": {"score": 3, "rationale": "OK"}
            }
        }

        stage2_result = {
            "judge_meta_score": 4,
            "weighted_gap": 0.5,
            "overall_feedback": "Good work"
        }

        snapshot = create_evaluation_snapshot(
            db=db_session,
            stage1_result=stage1_result,
            stage2_result=stage2_result,
            user_eval=user_eval,
            question=question,
            model_response=model_response
        )

        # Should still create snapshot with None evidence
        assert snapshot.evidence_json is None
        assert snapshot.judge_meta_score == 4


# =====================================================
# Test 6: create_evaluation_snapshot() - Rollback on Error
# =====================================================

class TestSnapshotRollback:
    """Tests for snapshot creation rollback."""

    def test_rollback_on_database_error(
        self,
        db_session: Session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """Test database rollback on exception."""
        question = make_question(primary_metric="Truthfulness")
        model_response = make_model_response(question_id=question.id)
        user_eval = make_user_evaluation(response_id=model_response.id)

        # Empty stage results (invalid for snapshot creation)
        stage1_result = {}  # Missing independent_scores key
        stage2_result = {}  # Missing judge_meta_score key

        # This should raise an error due to invalid data
        with pytest.raises((RuntimeError, ValueError, KeyError)):
            create_evaluation_snapshot(
                db=db_session,
                stage1_result=stage1_result,
                stage2_result=stage2_result,
                user_eval=user_eval,
                question=question,
                model_response=model_response
            )


# =====================================================
# Test 7: Slug Conversion Verification
# =====================================================

class TestSlugConversionInSnapshot:
    """Tests for comprehensive slug conversion in snapshots."""

    def test_all_metric_fields_use_slugs(
        self,
        db_session: Session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """Verify all metric-related fields use slug format."""
        question = make_question(
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Efficiency"]
        )
        model_response = make_model_response(question_id=question.id)
        user_eval = make_user_evaluation(response_id=model_response.id)

        stage1_result = {
            "independent_scores": {
                "Truthfulness": {"score": 3, "rationale": "OK"},
                "Clarity": {"score": 4, "rationale": "Clear"},
                "Efficiency": {"score": 5, "rationale": "Concise"},
                "Helpfulness": {"score": 4, "rationale": "Helpful"},
                "Safety": {"score": 5, "rationale": "Safe"},
                "Bias": {"score": 5, "rationale": "Fair"},
                "Consistency": {"score": 4, "rationale": "Consistent"},
                "Robustness": {"score": 4, "rationale": "Robust"}
            }
        }

        stage2_result = {
            "judge_meta_score": 4,
            "weighted_gap": 0.6,
            "overall_feedback": "Good"
        }

        snapshot = create_evaluation_snapshot(
            db=db_session,
            stage1_result=stage1_result,
            stage2_result=stage2_result,
            user_eval=user_eval,
            question=question,
            model_response=model_response
        )

        # Verify primary_metric is slug
        assert snapshot.primary_metric == "truthfulness"

        # Verify bonus_metrics are slugs
        assert set(snapshot.bonus_metrics) == {"clarity", "efficiency"}

        # Verify user_scores_json keys are slugs
        user_keys = set(snapshot.user_scores_json.keys())
        assert user_keys == {
            "truthfulness", "helpfulness", "safety", "bias",
            "clarity", "consistency", "efficiency", "robustness"
        }

        # Verify judge_scores_json keys are slugs
        judge_keys = set(snapshot.judge_scores_json.keys())
        assert judge_keys == {
            "truthfulness", "helpfulness", "safety", "bias",
            "clarity", "consistency", "efficiency", "robustness"
        }

        # Verify no display names in any JSON field
        all_json_keys = (
            set(snapshot.user_scores_json.keys()) |
            set(snapshot.judge_scores_json.keys()) |
            (set(snapshot.evidence_json.keys()) if snapshot.evidence_json else set())
        )
        for key in all_json_keys:
            assert key in METRIC_SLUG_MAP.values(), f"Found display name: {key}"


# =====================================================
# Test 8: get_snapshot() and list_snapshots()
# =====================================================

class TestGetAndListSnapshots:
    """Tests for snapshot retrieval functions."""

    def test_get_snapshot_by_id(
        self,
        db_session: Session,
        make_snapshot
    ):
        """Test retrieving snapshot by ID."""
        snapshot = make_snapshot()

        result = get_snapshot(db_session, snapshot.id)

        assert result is not None
        assert result.id == snapshot.id
        assert result.primary_metric == snapshot.primary_metric

    def test_get_snapshot_not_found(self, db_session: Session):
        """Test retrieving non-existent snapshot."""
        result = get_snapshot(db_session, "snap_nonexistent")
        assert result is None

    def test_get_snapshot_excludes_soft_deleted(
        self,
        db_session: Session,
        make_snapshot
    ):
        """Test that soft-deleted snapshots are not returned."""
        snapshot = make_snapshot()

        # Soft delete
        from datetime import datetime
        snapshot.deleted_at = datetime.now()
        db_session.commit()

        result = get_snapshot(db_session, snapshot.id)
        assert result is None

    def test_list_snapshots_default(
        self,
        db_session: Session,
        make_snapshot
    ):
        """Test listing snapshots without filters."""
        # Create multiple snapshots
        snap1 = make_snapshot(primary_metric="truthfulness")
        snap2 = make_snapshot(primary_metric="clarity")
        make_snapshot(primary_metric="helpfulness")

        snapshots, total = list_snapshots(db_session)

        assert total == 3
        assert len(snapshots) == 3
        assert any(s.id == snap1.id for s in snapshots)
        assert any(s.id == snap2.id for s in snapshots)

    def test_list_snapshots_with_status_filter(
        self,
        db_session: Session,
        make_snapshot
    ):
        """Test listing snapshots filtered by status."""
        make_snapshot(status="active")
        make_snapshot(status="completed")
        make_snapshot(status="archived")

        active_snapshots, active_total = list_snapshots(db_session, status="active")
        completed_snapshots, completed_total = list_snapshots(db_session, status="completed")

        assert active_total == 1
        assert len(active_snapshots) == 1
        assert active_snapshots[0].status == "active"

        assert completed_total == 1
        assert len(completed_snapshots) == 1
        assert completed_snapshots[0].status == "completed"

    def test_list_snapshots_pagination(
        self,
        db_session: Session,
        make_snapshot
    ):
        """Test pagination of snapshot list."""
        # Create 5 snapshots
        for i in range(5):
            make_snapshot(primary_metric=f"metric{i}")

        # First page
        snapshots1, total1 = list_snapshots(db_session, limit=2, offset=0)
        assert total1 == 5
        assert len(snapshots1) == 2

        # Second page
        snapshots2, total2 = list_snapshots(db_session, limit=2, offset=2)
        assert total2 == 5
        assert len(snapshots2) == 2

        # Third page (partial)
        snapshots3, total3 = list_snapshots(db_session, limit=2, offset=4)
        assert total3 == 5
        assert len(snapshots3) == 1
