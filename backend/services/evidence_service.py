"""
Evidence Service - Parse and transform Stage 1 evidence output.

Converts display name keys to slug keys (AD-6) and validates
evidence structure against Phase 3 schemas.

Reference: Task 12.2 - Evidence JSON Parser
"""

import logging
from typing import Any

from backend.constants.metrics import display_name_to_slug, is_valid_display_name
from backend.models.schemas import EvidenceItem

logger = logging.getLogger(__name__)

# The 8 metric display names
THE_EIGHT_METRICS = [
    "Truthfulness", "Helpfulness", "Safety", "Bias",
    "Clarity", "Consistency", "Efficiency", "Robustness"
]


def parse_evidence_from_stage1(stage1_response: dict) -> dict:
    """
    Parse Stage 1 evidence response and convert to slug-keyed format.

    Args:
        stage1_response: Raw GPT-4o response with display name keys
            {"independent_scores": {"Truthfulness": {...}}}

    Returns:
        Response with slug keys
            {"independent_scores": {"truthfulness": {...}}}

    Raises:
        ValueError: If response structure is invalid
    """
    # Validate structure
    if not isinstance(stage1_response, dict):
        raise ValueError(f"Stage 1 response must be a dict, got {type(stage1_response)}")

    if "independent_scores" not in stage1_response:
        raise ValueError("Stage 1 response missing 'independent_scores' key")

    # Convert each metric key from display name to slug
    slug_scores = {}
    for display_name, metric_data in stage1_response["independent_scores"].items():
        try:
            slug = display_name_to_slug(display_name)
        except ValueError:
            logger.warning(f"Unknown metric display name: {display_name}, skipping")
            continue

        # Validate evidence items if present
        if "evidence" in metric_data:
            metric_data["evidence"] = _validate_evidence_list(
                metric_data["evidence"], display_name
            )

        slug_scores[slug] = metric_data

    return {"independent_scores": slug_scores}


def _validate_evidence_list(evidence_list: list, metric_name: str) -> list:
    """
    Validate and clean evidence items.

    Ensures each evidence item has required fields and valid values.

    Args:
        evidence_list: Raw evidence list from GPT-4o
        metric_name: Metric name for logging

    Returns:
        Cleaned evidence list with only valid items
    """
    if not isinstance(evidence_list, list):
        logger.warning(f"Evidence for {metric_name} is not a list, converting to empty array")
        return []

    validated = []
    for idx, item in enumerate(evidence_list):
        if not _is_valid_evidence_item(item):
            logger.warning(f"Evidence item {idx} for {metric_name} invalid, skipping")
            continue

        # Ensure start < end
        if item["start"] >= item["end"]:
            logger.warning(f"Evidence item {idx} for {metric_name} has start >= end, setting to 0,0")
            item["start"] = 0
            item["end"] = 0

        validated.append(item)

    return validated


def _is_valid_evidence_item(item: Any) -> bool:
    """Check if evidence item has all required fields with valid types."""
    if not isinstance(item, dict):
        return False

    required = ["quote", "start", "end", "why", "better"]
    if not all(k in item for k in required):
        return False

    # Type checks
    if not isinstance(item["quote"], str) or not item["quote"].strip():
        return False

    if not isinstance(item["start"], int) or not isinstance(item["end"], int):
        return False

    if not isinstance(item["why"], str):
        return False

    if not isinstance(item["better"], str):
        return False

    return True


def convert_to_evidence_by_metric(stage1_response: dict) -> dict[str, list[EvidenceItem]]:
    """
    Convert Stage 1 evidence to EvidenceByMetric format (Phase 3 schema).

    Args:
        stage1_response: Parsed Stage 1 response (slug-keyed)

    Returns:
        Dictionary mapping metric slugs to EvidenceItem lists
    """
    result = {}

    for slug, metric_data in stage1_response.get("independent_scores", {}).items():
        evidence_list = metric_data.get("evidence", [])

        # Convert to EvidenceItem Pydantic models
        evidence_items = []
        for item in evidence_list:
            try:
                evidence_item = EvidenceItem(
                    quote=item["quote"],
                    start=item["start"],
                    end=item["end"],
                    why=item["why"],
                    better=item["better"],
                    verified=False,        # Explicit: not yet verified by self-healing
                    highlight_available=True  # Explicit: available for highlighting in UI
                )
                evidence_items.append(evidence_item)
            except Exception as e:
                logger.warning(f"Failed to convert evidence item for {slug}: {e}")

        result[slug] = evidence_items

    return result
