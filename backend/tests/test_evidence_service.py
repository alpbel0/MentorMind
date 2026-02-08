"""
Unit Tests for Evidence Service (Task 12.2)

Tests:
- Display name preservation (NOT converted to slugs)
- Evidence list validation
- Evidence item validation
- Pydantic schema conversion (convert_to_evidence_by_metric does slug conversion)
- Error handling
"""

import pytest

from backend.services.evidence_service import (
    parse_evidence_from_stage1,
    _validate_evidence_list,
    _is_valid_evidence_item,
    convert_to_evidence_by_metric,
)


# =====================================================
# Test parse_evidence_from_stage1
# =====================================================

class TestParseEvidenceFromStage1:
    """Test parse_evidence_from_stage1 function."""

    def test_preserves_display_names(self):
        """Test that display name keys are preserved (NOT converted to slugs)."""
        input_data = {
            "independent_scores": {
                "Truthfulness": {"score": 3, "rationale": "test", "evidence": []},
                "Helpfulness": {"score": 5, "rationale": "test", "evidence": []}
            }
        }
        result = parse_evidence_from_stage1(input_data)

        # Display names should be preserved
        assert "Truthfulness" in result["independent_scores"]
        assert "Helpfulness" in result["independent_scores"]
        # Slugs should NOT be present
        assert "truthfulness" not in result["independent_scores"]
        assert "helpfulness" not in result["independent_scores"]

    def test_all_8_metrics_preserved(self):
        """Test all 8 metrics are preserved correctly."""
        input_data = {
            "independent_scores": {
                "Truthfulness": {"score": 3, "rationale": "test"},
                "Helpfulness": {"score": 3, "rationale": "test"},
                "Safety": {"score": 3, "rationale": "test"},
                "Bias": {"score": 3, "rationale": "test"},
                "Clarity": {"score": 3, "rationale": "test"},
                "Consistency": {"score": 3, "rationale": "test"},
                "Efficiency": {"score": 3, "rationale": "test"},
                "Robustness": {"score": 3, "rationale": "test"},
            }
        }
        result = parse_evidence_from_stage1(input_data)

        expected_names = [
            "Truthfulness", "Helpfulness", "Safety", "Bias",
            "Clarity", "Consistency", "Efficiency", "Robustness"
        ]
        for name in expected_names:
            assert name in result["independent_scores"]

    def test_unknown_metric_skipped_with_warning(self):
        """Test unknown metric names are skipped with warning."""
        input_data = {
            "independent_scores": {
                "Truthfulness": {"score": 3, "rationale": "test"},
                "InvalidMetric": {"score": 3, "rationale": "test"}
            }
        }
        result = parse_evidence_from_stage1(input_data)

        # Valid metric should be preserved
        assert "Truthfulness" in result["independent_scores"]
        # Invalid metric should NOT be present
        assert "InvalidMetric" not in result["independent_scores"]

    def test_raises_error_for_non_dict_input(self):
        """Test ValueError raised for non-dict input."""
        with pytest.raises(ValueError, match="must be a dict"):
            parse_evidence_from_stage1("not a dict")

        with pytest.raises(ValueError, match="must be a dict"):
            parse_evidence_from_stage1(["list", "input"])

    def test_raises_error_for_missing_independent_scores(self):
        """Test ValueError raised when independent_scores key missing."""
        with pytest.raises(ValueError, match="missing 'independent_scores'"):
            parse_evidence_from_stage1({"other_key": "value"})

    def test_preserves_evidence_field_when_present(self):
        """Test evidence field is preserved during parsing."""
        input_data = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 3,
                    "rationale": "test",
                    "evidence": [
                        {"quote": "test quote", "start": 0, "end": 10, "why": "test", "better": "better"}
                    ]
                }
            }
        }
        result = parse_evidence_from_stage1(input_data)

        # Display name should be preserved
        assert "Truthfulness" in result["independent_scores"]
        assert "evidence" in result["independent_scores"]["Truthfulness"]
        assert len(result["independent_scores"]["Truthfulness"]["evidence"]) == 1


# =====================================================
# Test _validate_evidence_list
# =====================================================

class TestValidateEvidenceList:
    """Test _validate_evidence_list function."""

    def test_valid_evidence_list_preserved(self):
        """Test valid evidence list is preserved."""
        evidence = [
            {"quote": "test", "start": 0, "end": 10, "why": "test", "better": "better"}
        ]
        result = _validate_evidence_list(evidence, "Truthfulness")

        assert len(result) == 1
        assert result[0]["quote"] == "test"

    def test_non_list_converts_to_empty_array(self):
        """Test non-list input converts to empty array."""
        result = _validate_evidence_list("not a list", "Truthfulness")

        assert result == []

    def test_non_dict_item_skipped(self):
        """Test non-dict items are skipped."""
        evidence = [
            "string item",
            {"quote": "test", "start": 0, "end": 10, "why": "test", "better": "better"}
        ]
        result = _validate_evidence_list(evidence, "Truthfulness")

        assert len(result) == 1
        assert result[0]["quote"] == "test"

    def test_item_missing_required_field_skipped(self):
        """Test items missing required fields are skipped."""
        evidence = [
            {"quote": "test", "start": 0, "end": 10},  # Missing 'why' and 'better'
            {"quote": "test", "start": 0, "end": 10, "why": "test", "better": "better"}
        ]
        result = _validate_evidence_list(evidence, "Truthfulness")

        assert len(result) == 1

    def test_start_greater_than_end_corrected(self):
        """Test start >= end is corrected to 0, 0."""
        evidence = [
            {"quote": "test", "start": 10, "end": 5, "why": "test", "better": "better"}
        ]
        result = _validate_evidence_list(evidence, "Truthfulness")

        assert result[0]["start"] == 0
        assert result[0]["end"] == 0

    def test_start_equal_to_end_corrected(self):
        """Test start == end is corrected to 0, 0."""
        evidence = [
            {"quote": "test", "start": 5, "end": 5, "why": "test", "better": "better"}
        ]
        result = _validate_evidence_list(evidence, "Truthfulness")

        assert result[0]["start"] == 0
        assert result[0]["end"] == 0


# =====================================================
# Test _is_valid_evidence_item
# =====================================================

class TestIsValidEvidenceItem:
    """Test _is_valid_evidence_item function."""

    def test_valid_item_returns_true(self):
        """Test valid evidence item returns True."""
        item = {
            "quote": "test quote",
            "start": 0,
            "end": 10,
            "why": "test reason",
            "better": "better alternative"
        }
        assert _is_valid_evidence_item(item) is True

    def test_non_dict_returns_false(self):
        """Test non-dict input returns False."""
        assert _is_valid_evidence_item("string") is False
        assert _is_valid_evidence_item(123) is False
        assert _is_valid_evidence_item(None) is False
        assert _is_valid_evidence_item([]) is False

    def test_missing_quote_returns_false(self):
        """Test missing 'quote' field returns False."""
        item = {
            "start": 0,
            "end": 10,
            "why": "test",
            "better": "better"
        }
        assert _is_valid_evidence_item(item) is False

    def test_empty_quote_returns_false(self):
        """Test empty 'quote' field returns False."""
        item = {
            "quote": "   ",
            "start": 0,
            "end": 10,
            "why": "test",
            "better": "better"
        }
        assert _is_valid_evidence_item(item) is False

    def test_invalid_quote_type_returns_false(self):
        """Test non-string 'quote' returns False."""
        item = {
            "quote": 123,
            "start": 0,
            "end": 10,
            "why": "test",
            "better": "better"
        }
        assert _is_valid_evidence_item(item) is False

    def test_invalid_start_end_types_return_false(self):
        """Test non-int start/end returns False."""
        item = {
            "quote": "test",
            "start": "0",
            "end": 10,
            "why": "test",
            "better": "better"
        }
        assert _is_valid_evidence_item(item) is False

    def test_invalid_why_type_returns_false(self):
        """Test non-string 'why' returns False."""
        item = {
            "quote": "test",
            "start": 0,
            "end": 10,
            "why": 123,
            "better": "better"
        }
        assert _is_valid_evidence_item(item) is False

    def test_invalid_better_type_returns_false(self):
        """Test non-string 'better' returns False."""
        item = {
            "quote": "test",
            "start": 0,
            "end": 10,
            "why": "test",
            "better": 123
        }
        assert _is_valid_evidence_item(item) is False


# =====================================================
# Test convert_to_evidence_by_metric
# =====================================================

class TestConvertToEvidenceByMetric:
    """Test convert_to_evidence_by_metric function."""

    def test_converts_to_pydantic_models(self):
        """Test conversion to EvidenceItem Pydantic models."""
        # Input uses display names (as returned by parse_evidence_from_stage1)
        input_data = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 3,
                    "rationale": "test",
                    "evidence": [
                        {"quote": "test", "start": 0, "end": 4, "why": "test", "better": "better"}
                    ]
                }
            }
        }
        model_answer = "This is a test answer"
        result = convert_to_evidence_by_metric(input_data, model_answer)

        # Output uses slugs (for Phase 3 Coach Chat schema)
        assert "truthfulness" in result
        assert len(result["truthfulness"]) == 1
        # Should be Pydantic model with all fields
        evidence_item = result["truthfulness"][0]
        assert evidence_item.quote == "test"
        assert evidence_item.why == "test"
        assert evidence_item.better == "better"
        # After verification (quote exists in model_answer)
        assert evidence_item.verified is True
        assert evidence_item.highlight_available is True

    def test_empty_evidence_list(self):
        """Test handling of empty evidence list."""
        input_data = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 3,
                    "rationale": "test",
                    "evidence": []
                }
            }
        }
        result = convert_to_evidence_by_metric(input_data, "any model answer")

        assert result["truthfulness"] == []

    def test_missing_evidence_field(self):
        """Test handling of missing evidence field."""
        input_data = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 3,
                    "rationale": "test"
                }
            }
        }
        result = convert_to_evidence_by_metric(input_data, "any model answer")

        assert result["truthfulness"] == []

    def test_invalid_evidence_items_skipped(self):
        """Test invalid evidence items are skipped."""
        input_data = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 3,
                    "rationale": "test",
                    "evidence": [
                        {"quote": "test", "start": 0, "end": 4, "why": "test", "better": "better"},
                        {"invalid": "item"}  # Missing required fields
                    ]
                }
            }
        }
        result = convert_to_evidence_by_metric(input_data, "This is a test")

        # Only valid item should be converted
        assert len(result["truthfulness"]) == 1

    def test_multiple_metrics(self):
        """Test conversion with multiple metrics (display names to slugs)."""
        input_data = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 3,
                    "evidence": [
                        {"quote": "t1", "start": 0, "end": 2, "why": "w1", "better": "b1"}
                    ]
                },
                "Clarity": {
                    "score": 4,
                    "evidence": [
                        {"quote": "c1", "start": 0, "end": 2, "why": "w2", "better": "b2"}
                    ]
                }
            }
        }
        result = convert_to_evidence_by_metric(input_data, "t1 and c1 are here")

        # Output should have slug keys
        assert len(result) == 2
        assert len(result["truthfulness"]) == 1
        assert len(result["clarity"]) == 1
