"""Unit tests for metric slug constants and helpers."""

import pytest

from backend.constants.metrics import (
    METRIC_SLUG_MAP,
    SLUG_DISPLAY_MAP,
    ALL_METRIC_SLUGS,
    ALL_METRIC_NAMES,
    display_name_to_slug,
    slug_to_display_name,
    is_valid_slug,
    is_valid_display_name,
)


class TestMetricMappings:
    """Test that all 8 metrics are mapped correctly."""

    def test_all_8_metrics_mapped(self):
        """All 8 evaluation metrics should have slug mappings."""
        assert len(METRIC_SLUG_MAP) == 8

    def test_specific_metric_mappings(self):
        """Verify specific metric display name to slug mappings."""
        expected_mappings = {
            "Truthfulness": "truthfulness",
            "Helpfulness": "helpfulness",
            "Safety": "safety",
            "Bias": "bias",
            "Clarity": "clarity",
            "Consistency": "consistency",
            "Efficiency": "efficiency",
            "Robustness": "robustness",
        }
        assert METRIC_SLUG_MAP == expected_mappings

    def test_reverse_mapping_consistency(self):
        """SLUG_DISPLAY_MAP should be the inverse of METRIC_SLUG_MAP."""
        for display_name, slug in METRIC_SLUG_MAP.items():
            assert SLUG_DISPLAY_MAP[slug] == display_name

    def test_all_slugs_are_lowercase(self):
        """All slugs should be lowercase."""
        for slug in METRIC_SLUG_MAP.values():
            assert slug.islower(), f"Slug '{slug}' is not lowercase"


class TestDisplayNameToSlug:
    """Test display_name_to_slug function."""

    def test_valid_display_names(self):
        """Should return correct slug for all valid display names."""
        assert display_name_to_slug("Truthfulness") == "truthfulness"
        assert display_name_to_slug("Helpfulness") == "helpfulness"
        assert display_name_to_slug("Safety") == "safety"
        assert display_name_to_slug("Bias") == "bias"
        assert display_name_to_slug("Clarity") == "clarity"
        assert display_name_to_slug("Consistency") == "consistency"
        assert display_name_to_slug("Efficiency") == "efficiency"
        assert display_name_to_slug("Robustness") == "robustness"

    def test_invalid_display_name_raises_error(self):
        """Should raise ValueError for unknown display names."""
        with pytest.raises(ValueError, match="Unknown metric display name"):
            display_name_to_slug("InvalidMetric")

        with pytest.raises(ValueError, match="Unknown metric display name"):
            display_name_to_slug("")

        with pytest.raises(ValueError, match="Unknown metric display name"):
            display_name_to_slug("truthfulness")  # Slug passed instead of name

    def test_case_sensitivity(self):
        """Display names are case-sensitive."""
        assert display_name_to_slug("Truthfulness") == "truthfulness"

        with pytest.raises(ValueError):
            display_name_to_slug("truthfulness")

        with pytest.raises(ValueError):
            display_name_to_slug("TRUTHFULNESS")

        with pytest.raises(ValueError):
            display_name_to_slug("tRuThFuLnEsS")


class TestSlugToDisplayName:
    """Test slug_to_display_name function."""

    def test_valid_slugs(self):
        """Should return correct display name for all valid slugs."""
        assert slug_to_display_name("truthfulness") == "Truthfulness"
        assert slug_to_display_name("helpfulness") == "Helpfulness"
        assert slug_to_display_name("safety") == "Safety"
        assert slug_to_display_name("bias") == "Bias"
        assert slug_to_display_name("clarity") == "Clarity"
        assert slug_to_display_name("consistency") == "Consistency"
        assert slug_to_display_name("efficiency") == "Efficiency"
        assert slug_to_display_name("robustness") == "Robustness"

    def test_invalid_slug_raises_error(self):
        """Should raise ValueError for unknown slugs."""
        with pytest.raises(ValueError, match="Unknown metric slug"):
            slug_to_display_name("invalid-slug")

        with pytest.raises(ValueError, match="Unknown metric slug"):
            slug_to_display_name("")

        with pytest.raises(ValueError, match="Unknown metric slug"):
            slug_to_display_name("Truthfulness")  # Name passed instead of slug


class TestIsValidSlug:
    """Test is_valid_slug function."""

    def test_valid_slugs_return_true(self):
        """All valid slugs should return True."""
        valid_slugs = [
            "truthfulness",
            "helpfulness",
            "safety",
            "bias",
            "clarity",
            "consistency",
            "efficiency",
            "robustness",
        ]
        for slug in valid_slugs:
            assert is_valid_slug(slug), f"Slug '{slug}' should be valid"

    def test_invalid_slugs_return_false(self):
        """Invalid slugs should return False."""
        assert not is_valid_slug("invalid")
        assert not is_valid_slug("")
        assert not is_valid_slug("Truthfulness")  # Display name
        assert not is_valid_slug("TRUTHFULNESS")
        assert not is_valid_slug("safety-policy")  # Future potential but not now


class TestIsValidDisplayName:
    """Test is_valid_display_name function."""

    def test_valid_display_names_return_true(self):
        """All valid display names should return True."""
        valid_names = [
            "Truthfulness",
            "Helpfulness",
            "Safety",
            "Bias",
            "Clarity",
            "Consistency",
            "Efficiency",
            "Robustness",
        ]
        for name in valid_names:
            assert is_valid_display_name(name), f"Display name '{name}' should be valid"

    def test_invalid_display_names_return_false(self):
        """Invalid display names should return False."""
        assert not is_valid_display_name("InvalidMetric")
        assert not is_valid_display_name("")
        assert not is_valid_display_name("truthfulness")  # Slug
        assert not is_valid_display_name("TRUTHFULNESS")
        assert not is_valid_display_name("Safety & Policy")  # Future potential


class TestBidirectionalConsistency:
    """Test round-trip conversions between slugs and display names."""

    def test_round_trip_slug_to_name_to_slug(self):
        """Slug -> Display Name -> Slug should return original slug."""
        original_slug = "truthfulness"
        display_name = slug_to_display_name(original_slug)
        result_slug = display_name_to_slug(display_name)
        assert result_slug == original_slug

    def test_round_trip_name_to_slug_to_name(self):
        """Display Name -> Slug -> Display Name should return original name."""
        original_name = "Safety"
        slug = display_name_to_slug(original_name)
        result_name = slug_to_display_name(slug)
        assert result_name == original_name

    def test_all_metrics_round_trip(self):
        """All 8 metrics should survive round-trip conversion."""
        for original_slug in ALL_METRIC_SLUGS:
            display_name = slug_to_display_name(original_slug)
            result_slug = display_name_to_slug(display_name)
            assert result_slug == original_slug

        for original_name in ALL_METRIC_NAMES:
            slug = display_name_to_slug(original_name)
            result_name = slug_to_display_name(slug)
            assert result_name == original_name


class TestConstants:
    """Test exported constants."""

    def test_all_metric_slugs_sorted(self):
        """ALL_METRIC_SLUGS should be sorted alphabetically."""
        assert ALL_METRIC_SLUGS == sorted(ALL_METRIC_SLUGS)

    def test_all_metric_names_sorted(self):
        """ALL_METRIC_NAMES should be sorted alphabetically."""
        assert ALL_METRIC_NAMES == sorted(ALL_METRIC_NAMES)

    def test_all_metric_slugs_complete(self):
        """ALL_METRIC_SLUGS should contain all 8 metric slugs."""
        expected_slugs = {
            "truthfulness",
            "helpfulness",
            "safety",
            "bias",
            "clarity",
            "consistency",
            "efficiency",
            "robustness",
        }
        assert set(ALL_METRIC_SLUGS) == expected_slugs

    def test_all_metric_names_complete(self):
        """ALL_METRIC_NAMES should contain all 8 metric display names."""
        expected_names = {
            "Truthfulness",
            "Helpfulness",
            "Safety",
            "Bias",
            "Clarity",
            "Consistency",
            "Efficiency",
            "Robustness",
        }
        assert set(ALL_METRIC_NAMES) == expected_names

    def test_constants_length_match(self):
        """Both constant lists should have 8 items."""
        assert len(ALL_METRIC_SLUGS) == 8
        assert len(ALL_METRIC_NAMES) == 8
