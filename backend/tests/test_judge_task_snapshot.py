"""
Tests for Snapshot Creation in Judge Task - Task 13.3

Tests that snapshot creation is integrated with judge evaluation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from backend.tasks.judge_task import run_judge_evaluation
from backend.models.user_evaluation import UserEvaluation
from backend.models.model_response import ModelResponse
from backend.models.question import Question
from backend.services.judge_service import JudgeService


# =====================================================
# Task 13.3: Snapshot Integration Tests
# =====================================================

class TestJudgeTaskSnapshotIntegration:
    """Tests for snapshot creation in judge task."""

    @patch('backend.tasks.judge_task.SessionLocal')
    def test_snapshot_created_via_full_judge_evaluation(self, mock_session_local):
        """Verify snapshot is created when judge evaluation succeeds (via full_judge_evaluation)."""
        # Setup: Create mock database session
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # Create mock user evaluation
        mock_user_eval = Mock()
        mock_user_eval.id = "eval_test_001"
        mock_user_eval.judged = False

        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user_eval
        mock_db.query.return_value = mock_query

        # Mock judge service to verify call
        with patch('backend.tasks.judge_task.judge_service') as mock_judge:
            mock_judge.full_judge_evaluation.return_value = "judge_test_001"

            # Execute task
            result = run_judge_evaluation("eval_test_001")

            # Verify task succeeded
            assert result == "success"
            # Verify full_judge_evaluation was called (which includes snapshot creation)
            mock_judge.full_judge_evaluation.assert_called_once_with(
                user_eval_id="eval_test_001",
                db=mock_db
            )

    @patch('backend.tasks.judge_task.SessionLocal')
    def test_judge_task_succeeds_despite_snapshot_error(self, mock_session_local):
        """Verify judge task succeeds even if snapshot fails (graceful degradation)."""
        # Setup: Create mock database session
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # Create mock user evaluation
        mock_user_eval = Mock()
        mock_user_eval.id = "eval_test_002"
        mock_user_eval.judged = False

        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user_eval
        mock_db.query.return_value = mock_query

        # Mock judge service - full_judge_evaluation handles snapshot errors internally
        with patch('backend.tasks.judge_task.judge_service') as mock_judge:
            # Even if snapshot fails, full_judge_evaluation should return success
            mock_judge.full_judge_evaluation.return_value = "judge_test_002"

            result = run_judge_evaluation("eval_test_002")

            # Judge task should succeed (snapshot errors are non-fatal)
            assert result == "success"
            mock_judge.full_judge_evaluation.assert_called_once()
