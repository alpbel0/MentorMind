"""MentorMind - Metric Slug Constants and Helpers

Reference: AD-6 (Slug-Based Metric Keys) from NEW_FEATURES.md
"""

from typing import Dict, List

# =====================================================
# Core Mappings
# =====================================================

METRIC_SLUG_MAP: Dict[str, str] = {
    "Truthfulness": "truthfulness",
    "Helpfulness": "helpfulness",
    "Safety": "safety",
    "Bias": "bias",
    "Clarity": "clarity",
    "Consistency": "consistency",
    "Efficiency": "efficiency",
    "Robustness": "robustness",
}

SLUG_DISPLAY_MAP: Dict[str, str] = {v: k for k, v in METRIC_SLUG_MAP.items()}

# =====================================================
# Constants
# =====================================================

ALL_METRIC_SLUGS: List[str] = sorted(METRIC_SLUG_MAP.values())
ALL_METRIC_NAMES: List[str] = sorted(METRIC_SLUG_MAP.keys())

# =====================================================
# Helper Functions
# =====================================================


def display_name_to_slug(name: str) -> str:
    """Convert display name to slug. Raises ValueError for unknown names."""
    if name not in METRIC_SLUG_MAP:
        raise ValueError(f"Unknown metric display name: '{name}'")
    return METRIC_SLUG_MAP[name]


def slug_to_display_name(slug: str) -> str:
    """Convert slug to display name. Raises ValueError for unknown slugs."""
    if slug not in SLUG_DISPLAY_MAP:
        raise ValueError(f"Unknown metric slug: '{slug}'")
    return SLUG_DISPLAY_MAP[slug]


def is_valid_slug(slug: str) -> bool:
    """Check if slug is valid."""
    return slug in METRIC_SLUG_MAP.values()


def is_valid_display_name(name: str) -> bool:
    """Check if display name is valid."""
    return name in METRIC_SLUG_MAP
