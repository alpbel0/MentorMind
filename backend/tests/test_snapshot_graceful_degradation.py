"""
Tests for Snapshot Service Evidence Graceful Degradation (Task 13.4)

Tests for AD-8: Evidence parse failure should not crash snapshot creation.
Snapshot should be created with evidence_json=None when evidence processing fails.

The evidence_service already handles many error cases gracefully (returns empty lists).
This test suite focuses on the try/except wrapper in snapshot_service that
catches unexpected exceptions during evidence processing.
"""

import pytest
from unittest.mock import patch
from sqlalchemy.orm import Session

from backend.models.evaluation_snapshot import EvaluationSnapshot
from backend.services.snapshot_service import create_evaluation_snapshot


# =====================================================
# Test: Evidence Graceful Degradation (AD-8)
# =====================================================

class TestEvidenceGracefulDegradation:
    """Tests for AD-8: Evidence graceful degradation."""

    def test_missing_evidence_field_in_stage1(
        self,
        db_session: Session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """Test snapshot creation when Stage 1 has no evidence field."""
        question = make_question(primary_metric="Truthfulness")
        model_response = make_model_response(question_id=question.id)
        user_eval = make_user_evaluation(response_id=model_response.id)

        # Stage 1 WITHOUT evidence field at all
        stage1_result = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 4,
                    "rationale": "Good"
                    # NO evidence field
                }
            }
        }

        stage2_result = {
            "judge_meta_score": 4,
            "weighted_gap": 0.5,
            "overall_feedback": "OK"
        }

        snapshot = create_evaluation_snapshot(
            db=db_session,
            stage1_result=stage1_result,
            stage2_result=stage2_result,
            user_eval=user_eval,
            question=question,
            model_response=model_response
        )

        # No evidence field → raw_evidence is empty → evidence_json is None
        assert snapshot.evidence_json is None
        assert snapshot.judge_meta_score == 4  # Other data preserved

    def test_empty_evidence_list_converts_to_none(
        self,
        db_session: Session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """Test that empty evidence lists result in evidence_json=None."""
        question = make_question(primary_metric="Clarity")
        model_response = make_model_response(question_id=question.id)
        user_eval = make_user_evaluation(response_id=model_response.id)

        # Evidence is explicitly an empty list
        stage1_result = {
            "independent_scores": {
                "Clarity": {
                    "score": 3,
                    "rationale": "OK",
                    "evidence": []  # Empty list
                }
            }
        }

        stage2_result = {
            "judge_meta_score": 3,
            "weighted_gap": 0.8,
            "overall_feedback": "Decent"
        }

        snapshot = create_evaluation_snapshot(
            db=db_session,
            stage1_result=stage1_result,
            stage2_result=stage2_result,
            user_eval=user_eval,
            question=question,
            model_response=model_response
        )

        # Empty evidence dict → evidence_json is None
        assert snapshot.evidence_json is None
        assert snapshot.judge_meta_score == 3

    def test_invalid_evidence_items_get_fallback_flags(
        self,
        db_session: Session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """Test that invalid evidence items get fallback flags (graceful degradation)."""
        question = make_question(primary_metric="Safety")
        model_response = make_model_response(question_id=question.id)
        user_eval = make_user_evaluation(response_id=model_response.id)

        # Evidence items missing required fields - verification will fail
        # but evidence_service provides fallback with verified=False
        stage1_result = {
            "independent_scores": {
                "Safety": {
                    "score": 5,
                    "rationale": "Safe",
                    "evidence": [
                        {
                            "quote": "test quote",
                            "start": 0,
                            "end": 10,
                            "why": "test reason",
                            "better": "test better"
                        }
                    ]
                }
            }
        }

        stage2_result = {
            "judge_meta_score": 5,
            "weighted_gap": 0.0,
            "overall_feedback": "Perfect"
        }

        # Use a response text that doesn't match the quote (forces verification failure)
        snapshot = create_evaluation_snapshot(
            db=db_session,
            stage1_result=stage1_result,
            stage2_result=stage2_result,
            user_eval=user_eval,
            question=question,
            model_response=model_response
        )

        # Evidence is stored (even if unverified) - graceful degradation means
        # we preserve as much data as possible
        assert snapshot.evidence_json is not None
        assert snapshot.judge_meta_score == 5

    def test_malformed_metric_data_continues_gracefully(
        self,
        db_session: Session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """Test graceful degradation when metric_data is not a dict."""
        question = make_question(primary_metric="Efficiency")
        model_response = make_model_response(question_id=question.id)
        user_eval = make_user_evaluation(response_id=model_response.id)

        # Stage 1 with corrupted structure (metric_data is string)
        stage1_result = {
            "independent_scores": {
                "Efficiency": "corrupted data instead of dict"
            }
        }

        stage2_result = {
            "judge_meta_score": 4,
            "weighted_gap": 0.3,
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

        # String can't be iterated → caught by try/except → evidence_json=None
        assert snapshot.judge_meta_score == 4
        assert snapshot.evidence_json is None

    def test_unexpected_exception_during_processing(
        self,
        db_session: Session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """Test that unexpected exceptions during evidence processing are caught."""
        question = make_question(primary_metric="Truthfulness")
        model_response = make_model_response(question_id=question.id)
        user_eval = make_user_evaluation(response_id=model_response.id)

        stage1_result = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 5,
                    "rationale": "Perfect",
                    "evidence": [{"quote": "test", "start": 0, "end": 4, "why": "test", "better": "test"}]
                }
            }
        }

        stage2_result = {
            "judge_meta_score": 5,
            "weighted_gap": 0.0,
            "overall_feedback": "Excellent"
        }

        # Mock process_evidence to raise an unexpected exception
        with patch('backend.services.snapshot_service.process_evidence', side_effect=RuntimeError("Unexpected error!")):
            snapshot = create_evaluation_snapshot(
                db=db_session,
                stage1_result=stage1_result,
                stage2_result=stage2_result,
                user_eval=user_eval,
                question=question,
                model_response=model_response
            )

        # Exception caught → evidence_json=None → snapshot still created
        assert snapshot.evidence_json is None
        assert snapshot.judge_meta_score == 5
        assert snapshot.status == "active"

    def test_valid_evidence_still_works(
        self,
        db_session: Session,
        make_question,
        make_model_response,
        make_user_evaluation
    ):
        """Test that valid evidence still processes correctly (no regression)."""
        question = make_question(primary_metric="Truthfulness")
        model_response = make_model_response(
            question_id=question.id,
            response_text="The capital of France is Paris and it's a beautiful city."
        )
        user_eval = make_user_evaluation(response_id=model_response.id)

        # Valid evidence with all required fields
        stage1_result = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 5,
                    "rationale": "Perfect",
                    "evidence": [
                        {
                            "quote": "The capital of France is Paris",
                            "start": 0,
                            "end": 30,
                            "why": "Correct fact stated",
                            "better": "N/A"
                        }
                    ]
                }
            }
        }

        stage2_result = {
            "judge_meta_score": 5,
            "weighted_gap": 0.0,
            "overall_feedback": "Excellent"
        }

        snapshot = create_evaluation_snapshot(
            db=db_session,
            stage1_result=stage1_result,
            stage2_result=stage2_result,
            user_eval=user_eval,
            question=question,
            model_response=model_response
        )

        # Evidence should be processed and converted to slugs
        assert snapshot.evidence_json is not None
        assert "truthfulness" in snapshot.evidence_json
        assert snapshot.judge_meta_score == 5
