"""
Unit tests for Phase 3 schemas (Coach Chat & Evidence).

Tests validation logic for:
- EvidenceItem (start/end position validation)
- ChatMessageCreate (UUID v4 validation)
- ChatRequest (UUID v4 validation)
- SnapshotResponse (ORM configuration)
"""

import pytest
from pydantic import ValidationError

from backend.models.schemas import (
    EvidenceItem,
    MetricEvidence,
    ChatMessageCreate,
    ChatRequest,
    SnapshotResponse,
)


# =====================================================
# EvidenceItem Tests
# =====================================================

class TestEvidenceItem:
    """Test EvidenceItem validation."""

    def test_valid_evidence_item(self):
        """Valid evidence item should pass validation."""
        evidence = EvidenceItem(
            start=10,
            end=25,
            quote="example text",
            why="This shows the issue"
        )
        assert evidence.start == 10
        assert evidence.end == 25
        assert evidence.quote == "example text"
        assert evidence.why == "This shows the issue"
        assert evidence.verified is False
        assert evidence.highlight_available is True

    def test_evidence_item_with_all_fields(self):
        """Evidence item with all optional fields set."""
        evidence = EvidenceItem(
            start=0,
            end=50,
            quote="Full excerpt from the response",
            why="This demonstrates the problem clearly",
            better="A better alternative suggestion",
            verified=True,
            highlight_available=False
        )
        assert evidence.start == 0
        assert evidence.end == 50
        assert evidence.better == "A better alternative suggestion"
        assert evidence.verified is True
        assert evidence.highlight_available is False

    def test_end_equal_to_start_raises_error(self):
        """end == start should raise ValidationError."""
        with pytest.raises(ValidationError, match="end.*must be greater than start"):
            EvidenceItem(
                start=10,
                end=10,
                quote="invalid",
                why="test"
            )

    def test_end_before_start_raises_error(self):
        """end < start should raise ValidationError."""
        with pytest.raises(ValidationError, match="end.*must be greater than start"):
            EvidenceItem(
                start=25,
                end=10,
                quote="invalid",
                why="test"
            )

    def test_negative_start_raises_error(self):
        """start < 0 should raise ValidationError."""
        with pytest.raises(ValidationError):
            EvidenceItem(
                start=-1,
                end=10,
                quote="test",
                why="test"
            )

    def test_zero_end_raises_error(self):
        """end <= 0 should raise ValidationError (gt=0 constraint)."""
        with pytest.raises(ValidationError):
            EvidenceItem(
                start=0,
                end=0,
                quote="test",
                why="test"
            )

    def test_negative_end_raises_error(self):
        """end < 0 should raise ValidationError."""
        with pytest.raises(ValidationError):
            EvidenceItem(
                start=0,
                end=-5,
                quote="test",
                why="test"
            )

    def test_zero_start_valid(self):
        """start=0 is valid when end > 0."""
        evidence = EvidenceItem(
            start=0,
            end=5,
            quote="valid",
            why="test"
        )
        assert evidence.start == 0
        assert evidence.end == 5


# =====================================================
# ChatMessageCreate Tests
# =====================================================

class TestChatMessageCreate:
    """Test ChatMessageCreate UUID validation."""

    def test_valid_uuid_v4(self):
        """Valid UUID v4 should pass."""
        msg = ChatMessageCreate(
            snapshot_id="snap_001",
            client_message_id="550e8400-e29b-41d4-a716-446655440000",
            role="user",
            content="Hello"
        )
        assert msg.client_message_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_valid_uuid_v4_uppercase(self):
        """Valid UUID v4 with uppercase letters should pass."""
        msg = ChatMessageCreate(
            snapshot_id="snap_001",
            client_message_id="550E8400-E29B-41D4-A716-446655440000",
            role="user",
            content="Hello"
        )
        assert msg.client_message_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_valid_uuid_v4_mixed_case(self):
        """Valid UUID v4 with mixed case should pass."""
        msg = ChatMessageCreate(
            snapshot_id="snap_001",
            client_message_id="550e8400-E29b-41d4-A716-446655440000",
            role="user",
            content="Hello"
        )
        assert msg.client_message_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_invalid_uuid_format_raises_error(self):
        """Invalid UUID format should raise ValidationError."""
        with pytest.raises(ValidationError, match="must be a valid UUID"):
            ChatMessageCreate(
                snapshot_id="snap_001",
                client_message_id="not-a-uuid",
                role="user",
                content="Hello"
            )

    def test_invalid_uuid_format_partial_raises_error(self):
        """Partial UUID format should raise ValidationError."""
        with pytest.raises(ValidationError, match="must be a valid UUID"):
            ChatMessageCreate(
                snapshot_id="snap_001",
                client_message_id="550e8400-e29b",
                role="user",
                content="Hello"
            )

    def test_xss_script_tag_raises_error(self):
        """XSS script tag payload should fail UUID validation."""
        with pytest.raises(ValidationError, match="must be a valid UUID"):
            ChatMessageCreate(
                snapshot_id="snap_001",
                client_message_id="<script>alert('xss')</script>",
                role="user",
                content="Hello"
            )

    def test_sql_injection_attempt_raises_error(self):
        """SQL injection payload should fail UUID validation."""
        with pytest.raises(ValidationError, match="must be a valid UUID"):
            ChatMessageCreate(
                snapshot_id="snap_001",
                client_message_id="'; DROP TABLE users; --",
                role="user",
                content="Hello"
            )

    def test_xss_img_tag_raises_error(self):
        """XSS img tag payload should fail UUID validation."""
        with pytest.raises(ValidationError, match="must be a valid UUID"):
            ChatMessageCreate(
                snapshot_id="snap_001",
                client_message_id='"><script>alert(String.fromCharCode(88,83,83))</script>',
                role="user",
                content="Hello"
            )

    def test_empty_uuid_raises_error(self):
        """Empty string should raise ValidationError."""
        with pytest.raises(ValidationError, match="must be a valid UUID|cannot be empty"):
            ChatMessageCreate(
                snapshot_id="snap_001",
                client_message_id="",
                role="user",
                content="Hello"
            )

    def test_whitespace_only_raises_error(self):
        """Whitespace-only string should raise ValidationError."""
        with pytest.raises(ValidationError, match="must be a valid UUID|cannot be empty"):
            ChatMessageCreate(
                snapshot_id="snap_001",
                client_message_id="   ",
                role="user",
                content="Hello"
            )

    def test_uuid_v1_raises_error(self):
        """UUID v1 should be rejected (only v4 allowed)."""
        # UUID v1: time-based, version 1 (valid UUID format but wrong version)
        uuid_v1 = "00000000-0000-1000-8000-00805f9b34fb"
        with pytest.raises(ValidationError, match="must be UUID v4"):
            ChatMessageCreate(
                snapshot_id="snap_001",
                client_message_id=uuid_v1,
                role="user",
                content="Hello"
            )

    def test_uuid_with_selected_metrics(self):
        """Valid chat message with selected metrics."""
        msg = ChatMessageCreate(
            snapshot_id="snap_001",
            client_message_id="6ba7b810-9dad-41d1-80b4-00c04fd430c8",
            role="user",
            content="Explain truthfulness",
            selected_metrics=["truthfulness", "clarity"]
        )
        assert msg.selected_metrics == ["truthfulness", "clarity"]

    def test_invalid_role_raises_error(self):
        """Invalid role should raise ValidationError."""
        with pytest.raises(ValidationError, match="Invalid role"):
            ChatMessageCreate(
                snapshot_id="snap_001",
                client_message_id="550e8400-e29b-41d4-a716-446655440000",
                role="system",
                content="Hello"
            )


# =====================================================
# ChatRequest Tests
# =====================================================

class TestChatRequest:
    """Test ChatRequest UUID validation."""

    def test_valid_uuid_v4(self):
        """Valid UUID v4 should pass."""
        request = ChatRequest(
            message="Test message",
            client_message_id="6ba7b810-9dad-41d1-80b4-00c04fd430c8"
        )
        assert request.client_message_id == "6ba7b810-9dad-41d1-80b4-00c04fd430c8"

    def test_invalid_uuid_raises_error(self):
        """Invalid UUID should raise ValidationError."""
        with pytest.raises(ValidationError, match="must be a valid UUID"):
            ChatRequest(
                message="Test",
                client_message_id="invalid-uuid-format"
            )

    def test_xss_payload_raises_error(self):
        """XSS payload should fail UUID validation."""
        with pytest.raises(ValidationError, match="must be a valid UUID"):
            ChatRequest(
                message="Test",
                client_message_id="<img src=x onerror=alert('XSS')>"
            )

    def test_chat_request_with_selected_metrics(self):
        """Chat request with selected metrics."""
        request = ChatRequest(
            message="Help me understand",
            client_message_id="550e8400-e29b-41d4-a716-446655440000",
            selected_metrics=["truthfulness", "helpfulness", "safety"]
        )
        assert request.selected_metrics == ["truthfulness", "helpfulness", "safety"]

    def test_too_many_selected_metrics_raises_error(self):
        """More than 3 selected metrics should raise ValidationError."""
        with pytest.raises(ValidationError, match="at most 3 items"):
            ChatRequest(
                message="Test",
                client_message_id="550e8400-e29b-41d4-a716-446655440000",
                selected_metrics=["truthfulness", "helpfulness", "safety", "bias"]
            )

    def test_invalid_metric_slug_raises_error(self):
        """Invalid metric slug should raise ValidationError."""
        with pytest.raises(ValidationError, match="Invalid metric slug"):
            ChatRequest(
                message="Test",
                client_message_id="550e8400-e29b-41d4-a716-446655440000",
                selected_metrics=["invalid_metric"]
            )

    def test_empty_message_raises_error(self):
        """Empty message should raise ValidationError."""
        with pytest.raises(ValidationError):
            ChatRequest(
                message="",
                client_message_id="550e8400-e29b-41d4-a716-446655440000"
            )

    def test_is_init_flag(self):
        """is_init flag should be settable."""
        request = ChatRequest(
            message="First message",
            client_message_id="550e8400-e29b-41d4-a716-446655440000",
            is_init=True
        )
        assert request.is_init is True


# =====================================================
# SnapshotResponse Tests
# =====================================================

class TestSnapshotResponse:
    """Test SnapshotResponse ORM conversion."""

    def test_from_attributes_config(self):
        """SnapshotResponse should have from_attributes enabled."""
        assert SnapshotResponse.model_config.get("from_attributes", False) is True


# =====================================================
# MetricEvidence Tests
# =====================================================

class TestMetricEvidence:
    """Test MetricEvidence validation."""

    def test_valid_metric_evidence(self):
        """Valid metric evidence should pass."""
        evidence = MetricEvidence(
            metric_slug="truthfulness",
            user_score=3,
            judge_score=4,
            metric_gap=1.0,
            user_reason="User's reasoning",
            judge_reason="Judge's rationale",
            evidence=[
                EvidenceItem(
                    start=10,
                    end=25,
                    quote="example",
                    why="evidence"
                )
            ]
        )
        assert evidence.metric_slug == "truthfulness"
        assert evidence.user_score == 3
        assert evidence.judge_score == 4
        assert evidence.metric_gap == 1.0
        assert len(evidence.evidence) == 1

    def test_metric_evidence_with_null_scores(self):
        """Metric evidence with null scores should be valid."""
        evidence = MetricEvidence(
            metric_slug="truthfulness",
            user_score=None,
            judge_score=None,
            metric_gap=0.0,
            user_reason="N/A",
            judge_reason="N/A",
            evidence=[]
        )
        assert evidence.user_score is None
        assert evidence.judge_score is None
        assert evidence.evidence == []
