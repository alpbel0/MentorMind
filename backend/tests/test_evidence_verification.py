"""
Unit tests for Evidence Verification Algorithm (Task 12.3 - AD-2).

Tests the 5-stage self-healing verification system for evidence items.
"""

import pytest

from backend.services.evidence_service import (
    _verify_exact_slice,
    _verify_substring_search,
    _verify_anchor_based,
    _verify_whitespace_safe,
    verify_evidence_item,
    verify_all_evidence,
)


# =====================================================
# Test Data Fixtures
# =====================================================

@pytest.fixture
def sample_model_answer():
    """Sample model response for testing."""
    return "The answer is 42, according to Douglas Adams. This is the meaning of life."


@pytest.fixture
def sample_evidence_item():
    """Sample evidence item with all required fields."""
    return {
        "quote": "The answer is 42",
        "start": 0,
        "end": 16,
        "why": "Direct answer to the question",
        "better": "None"
    }


# =====================================================
# Stage 1: Exact Slice Tests
# =====================================================

class TestExactSlice:
    """Tests for Stage 1: Exact slice verification."""

    def test_exact_slice_match(self, sample_model_answer):
        """Correct positions should match exactly."""
        quote = "The answer is 42"
        start, end = 0, 16

        verified, new_start, new_end = _verify_exact_slice(
            sample_model_answer, quote, start, end
        )

        assert verified is True
        assert new_start == 0
        assert new_end == 16

    def test_exact_slice_no_match(self, sample_model_answer):
        """Wrong positions should not match."""
        quote = "The answer is 42"
        start, end = 10, 26  # Wrong position

        verified, new_start, new_end = _verify_exact_slice(
            sample_model_answer, quote, start, end
        )

        assert verified is False
        assert new_start == 10
        assert new_end == 26  # Positions unchanged

    def test_exact_slice_out_of_bounds_negative_start(self, sample_model_answer):
        """Negative start position should fail."""
        quote = "The answer"
        verified, _, _ = _verify_exact_slice(sample_model_answer, quote, -1, 10)

        assert verified is False

    def test_exact_slice_out_of_bounds_end_beyond_text(self, sample_model_answer):
        """End beyond text length should fail."""
        quote = "The answer"
        verified, _, _ = _verify_exact_slice(
            sample_model_answer, quote, 0, 1000
        )

        assert verified is False

    def test_exact_slice_start_equals_end(self, sample_model_answer):
        """Start equal to end should fail."""
        quote = "The"
        verified, _, _ = _verify_exact_slice(sample_model_answer, quote, 0, 0)

        assert verified is False

    def test_exact_slice_start_greater_than_end(self, sample_model_answer):
        """Start greater than end should fail."""
        quote = "The"
        verified, _, _ = _verify_exact_slice(sample_model_answer, quote, 10, 5)

        assert verified is False


# =====================================================
# Stage 2: Substring Search Tests
# =====================================================

class TestSubstringSearch:
    """Tests for Stage 2: Substring search."""

    def test_substring_found(self, sample_model_answer):
        """Quote exists at different position."""
        quote = "Douglas Adams"

        verified, start, end = _verify_substring_search(sample_model_answer, quote)

        assert verified is True
        assert start == 31  # Position of "Douglas Adams"
        assert end == 44    # start + len(quote)

    def test_substring_not_found(self, sample_model_answer):
        """Quote doesn't exist in text."""
        quote = "Albert Einstein"

        verified, start, end = _verify_substring_search(sample_model_answer, quote)

        assert verified is False
        assert start == 0
        assert end == 0

    def test_substring_multiple_occurrences(self):
        """First occurrence should be used."""
        text = "the cat and the dog"
        quote = "the"

        verified, start, end = _verify_substring_search(text, quote)

        assert verified is True
        assert start == 0  # First occurrence
        assert end == 3

    def test_substring_empty_quote(self, sample_model_answer):
        """Empty quote should be found at position 0."""
        verified, start, end = _verify_substring_search(sample_model_answer, "")

        assert verified is True
        assert start == 0
        assert end == 0

    def test_substring_case_sensitive(self, sample_model_answer):
        """Search should be case-sensitive."""
        quote = "THE ANSWER"

        verified, _, _ = _verify_substring_search(sample_model_answer, quote)

        assert verified is False


# =====================================================
# Stage 3: Anchor-Based Tests
# =====================================================

class TestAnchorBased:
    """Tests for Stage 3: Anchor-based search."""

    def test_anchor_both_found(self, sample_model_answer):
        """Both head and tail anchors found."""
        quote = "meaning of life"
        anchor_len = 7

        verified, start, end = _verify_anchor_based(
            sample_model_answer, quote, anchor_len, search_window=2000
        )

        assert verified is True
        # Should find "meaning " at start and " life" at end
        assert start >= 0
        assert end > start

    def test_anchor_head_only(self, sample_model_answer):
        """Head found but tail missing."""
        quote = "meaning of death"  # "death" not in text
        anchor_len = 7

        verified, start, end = _verify_anchor_based(
            sample_model_answer, quote, anchor_len, search_window=2000
        )

        assert verified is False
        assert start == 0
        assert end == 0

    def test_anchor_search_window(self):
        """Tail should only be found within search window."""
        text = "START" + "x" * 3000 + "END"
        quote = "START" + "x" * 100 + "END"  # Actual gap is larger than quote
        anchor_len = 4

        # With small window, tail not found
        verified, _, _ = _verify_anchor_based(
            text, quote, anchor_len, search_window=100
        )

        assert verified is False

    def test_anchor_quote_too_short(self, sample_model_answer):
        """Quote shorter than 2*anchor_len should skip Stage 3."""
        quote = "hi"  # Only 2 chars
        anchor_len = 25

        verified, start, end = _verify_anchor_based(
            sample_model_answer, quote, anchor_len, search_window=2000
        )

        assert verified is False
        assert start == 0
        assert end == 0

    def test_anchor_exactly_double_length(self):
        """Quote exactly 2*anchor_len should work.

        Note: When text is repetitive, anchor search finds first occurrence
        of each anchor. For "ABABAB..." repeated, head anchor at position 0,
        tail anchor also found at position 0 (first match).
        """
        text = "AB" * 25  # 50 chars
        quote = "AB" * 25
        anchor_len = 25

        verified, start, end = _verify_anchor_based(
            text, quote, anchor_len, search_window=2000
        )

        # Should verify successfully
        assert verified is True
        # Found at position where head anchor appears first
        assert start >= 0
        # End position is head_idx + len(tail_anchor)
        assert end > start


# =====================================================
# Stage 4: Whitespace Safe Tests
# =====================================================

class TestWhitespaceSafe:
    """Tests for Stage 4: Whitespace-insensitive match."""

    def test_whitespace_safe_found(self):
        """Match with different whitespace."""
        text = "The  answer\tis\n42"
        quote = "The answer is 42"

        verified = _verify_whitespace_safe(text, quote)

        assert verified is True

    def test_whitespace_safe_not_found(self, sample_model_answer):
        """No match even after normalization."""
        quote = "The answer is 43"  # Different number

        verified = _verify_whitespace_safe(sample_model_answer, quote)

        assert verified is False

    def test_whitespace_safe_newlines(self):
        """Match with newlines normalized to spaces."""
        text = "Line1\nLine2\nLine3"
        quote = "Line1 Line2 Line3"

        verified = _verify_whitespace_safe(text, quote)

        assert verified is True

    def test_whitespace_safe_tabs(self):
        """Match with tabs normalized to spaces."""
        text = "Word1\t\t\tWord2"
        quote = "Word1 Word2"

        verified = _verify_whitespace_safe(text, quote)

        assert verified is True

    def test_whitespace_safe_leading_trailing(self):
        """Match with leading/trailing whitespace."""
        text = "  hello world  "
        quote = "hello world"

        verified = _verify_whitespace_safe(text, quote)

        assert verified is True

    def test_whitespace_safe_empty_both(self):
        """Empty strings should match."""
        verified = _verify_whitespace_safe("", "")

        assert verified is True

    def test_whitespace_safe_empty_text(self):
        """Empty text with non-empty quote should not match."""
        verified = _verify_whitespace_safe("", "hello")

        assert verified is False


# =====================================================
# Orchestrator Tests
# =====================================================

class TestVerifyEvidenceItem:
    """Tests for the 5-stage orchestrator."""

    def test_verify_stage1_pass(self, sample_model_answer):
        """Exact slice should succeed at Stage 1."""
        item = {
            "quote": "The answer is 42",
            "start": 0,
            "end": 16,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(sample_model_answer, item)

        assert result["verified"] is True
        assert result["highlight_available"] is True
        assert result["start"] == 0
        assert result["end"] == 16

    def test_verify_stage2_pass(self, sample_model_answer):
        """Substring search should succeed at Stage 2."""
        item = {
            "quote": "Douglas Adams",
            "start": 0,  # Wrong position
            "end": 13,   # Wrong position
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(sample_model_answer, item)

        assert result["verified"] is True
        assert result["highlight_available"] is True
        assert result["start"] == 31  # Corrected position
        assert result["end"] == 44

    def test_verify_stage3_pass(self, sample_model_answer):
        """Anchor-based should succeed at Stage 3."""
        item = {
            "quote": "meaning of life",
            "start": 0,  # Wrong
            "end": 10,   # Wrong
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(
            sample_model_answer, item,
            anchor_len=7,
            search_window=2000
        )

        assert result["verified"] is True
        assert result["highlight_available"] is True
        assert result["start"] >= 0

    def test_verify_stage4_pass(self):
        """Whitespace-safe should succeed at Stage 4."""
        text = "The  answer\tis\n42"
        item = {
            "quote": "The answer is 42",
            "start": 0,
            "end": 16,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(text, item)

        assert result["verified"] is True
        assert result["highlight_available"] is False  # Safe mode
        assert result["start"] == 0  # Original preserved
        assert result["end"] == 16

    def test_verify_stage5_fail(self, sample_model_answer):
        """All stages fail - verification should fail."""
        item = {
            "quote": "nonexistent text xyz123",
            "start": 0,
            "end": 20,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(sample_model_answer, item)

        assert result["verified"] is False
        assert result["highlight_available"] is False

    def test_verify_preserves_other_fields(self, sample_model_answer):
        """why and better fields should be preserved."""
        item = {
            "quote": "The answer is 42",
            "start": 0,
            "end": 16,
            "why": "This is why",
            "better": "This is better"
        }

        result = verify_evidence_item(sample_model_answer, item)

        assert result["why"] == "This is why"
        assert result["better"] == "This is better"

    def test_verify_empty_model_answer(self, sample_evidence_item):
        """Empty model_answer should return fallback."""
        result = verify_evidence_item("", sample_evidence_item)

        assert result["verified"] is False
        assert result["highlight_available"] is False

    def test_verify_empty_quote(self, sample_model_answer):
        """Empty quote should return fallback."""
        item = {
            "quote": "",
            "start": 0,
            "end": 0,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(sample_model_answer, item)

        assert result["verified"] is False
        assert result["highlight_available"] is False

    def test_verify_custom_anchor_len(self, sample_model_answer):
        """Custom anchor_len should be used."""
        item = {
            "quote": "The answer is 42",
            "start": 0,
            "end": 16,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(sample_model_answer, item, anchor_len=5)

        assert result["verified"] is True

    def test_verify_custom_search_window(self, sample_model_answer):
        """Custom search_window should be used."""
        item = {
            "quote": "Douglas",
            "start": 0,
            "end": 7,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(
            sample_model_answer, item, search_window=100
        )

        assert result["verified"] is True


# =====================================================
# Batch Verification Tests
# =====================================================

class TestVerifyAllEvidence:
    """Tests for batch verification."""

    def test_verify_all_evidence_empty_list(self, sample_model_answer):
        """Empty list should return empty list."""
        result = verify_all_evidence(sample_model_answer, [])

        assert result == []

    def test_verify_all_evidence_multiple_items(self, sample_model_answer):
        """Multiple items should all be verified."""
        items = [
            {
                "quote": "The answer is 42",
                "start": 0,
                "end": 16,
                "why": "Test1",
                "better": "None"
            },
            {
                "quote": "Douglas Adams",
                "start": 0,
                "end": 13,
                "why": "Test2",
                "better": "None"
            }
        ]

        result = verify_all_evidence(sample_model_answer, items)

        assert len(result) == 2
        assert result[0]["verified"] is True
        assert result[1]["verified"] is True

    def test_verify_all_evidence_partial_failure(self, sample_model_answer):
        """Some items fail, some succeed."""
        items = [
            {
                "quote": "The answer is 42",
                "start": 0,
                "end": 16,
                "why": "Test1",
                "better": "None"
            },
            {
                "quote": "nonexistent xyz",
                "start": 0,
                "end": 14,
                "why": "Test2",
                "better": "None"
            }
        ]

        result = verify_all_evidence(sample_model_answer, items)

        assert len(result) == 2
        assert result[0]["verified"] is True
        assert result[1]["verified"] is False

    def test_verify_all_preserves_order(self, sample_model_answer):
        """Order of items should be preserved."""
        items = [
            {"quote": "42", "start": 0, "end": 2, "why": "1", "better": "N"},
            {"quote": "Douglas", "start": 0, "end": 7, "why": "2", "better": "N"},
            {"quote": "Adams", "start": 0, "end": 5, "why": "3", "better": "N"},
        ]

        result = verify_all_evidence(sample_model_answer, items)

        assert len(result) == 3
        assert result[0]["why"] == "1"
        assert result[1]["why"] == "2"
        assert result[2]["why"] == "3"


# =====================================================
# Edge Cases Tests
# =====================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_unicode_characters(self):
        """Unicode characters should be handled correctly."""
        text = "Hello 世界 🌍"
        item = {
            "quote": "世界",
            "start": 6,
            "end": 8,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(text, item)

        assert result["verified"] is True

    def test_very_long_quote(self):
        """Long quote should still work."""
        text = "A" * 1000 + "TARGET" + "B" * 1000
        item = {
            "quote": "TARGET",
            "start": 1000,
            "end": 1006,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(text, item)

        assert result["verified"] is True

    def test_quote_at_text_boundary(self):
        """Quote at the very end of text."""
        text = "This is the end"
        item = {
            "quote": "end",
            "start": 12,
            "end": 15,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(text, item)

        assert result["verified"] is True

    def test_quote_at_text_start(self):
        """Quote at the very start of text."""
        text = "Start here"
        item = {
            "quote": "Start",
            "start": 0,
            "end": 5,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(text, item)

        assert result["verified"] is True

    def test_single_character_quote(self):
        """Single character quote should work."""
        text = "ABC"
        item = {
            "quote": "B",
            "start": 1,
            "end": 2,
            "why": "Test",
            "better": "None"
        }

        result = verify_evidence_item(text, item)

        assert result["verified"] is True

    def test_special_regex_chars(self):
        """Special regex characters should be handled."""
        text = "Price is $100.00"
        item = {
            "quote": "$100.00",
            "start": 9,
            "end": 16,
            "why": "Test",
            "better": "None"
        }

        # Stage 1 should work (exact match)
        result = verify_evidence_item(text, item)

        assert result["verified"] is True
