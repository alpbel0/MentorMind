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
    Parse Stage 1 evidence response and validate evidence structure.

    NOTE: As of the fix for missing metrics bug, this function NO LONGER
    converts display names to slugs. The display names (e.g., "Truthfulness")
    are preserved for backward compatibility with existing tests and code.

    For Phase 3 (Coach Chat), use convert_to_evidence_by_metric() which
    handles the slug conversion as part of creating EvidenceByMetric format.

    Args:
        stage1_response: Raw GPT-4o response with display name keys
            {"independent_scores": {"Truthfulness": {...}}}

    Returns:
        Response with display name keys preserved
            {"independent_scores": {"Truthfulness": {...}}}

    Raises:
        ValueError: If response structure is invalid
    """
    # Validate structure
    if not isinstance(stage1_response, dict):
        raise ValueError(f"Stage 1 response must be a dict, got {type(stage1_response)}")

    if "independent_scores" not in stage1_response:
        raise ValueError("Stage 1 response missing 'independent_scores' key")

    # Validate evidence items for each metric (keep display name keys)
    # Build a new dict to filter out invalid metrics
    validated_scores = {}
    for display_name, metric_data in stage1_response["independent_scores"].items():
        # Validate display name
        if not is_valid_display_name(display_name):
            logger.warning(f"Unknown metric display name: {display_name}, skipping")
            continue

        # Validate evidence items if present
        if "evidence" in metric_data:
            metric_data["evidence"] = _validate_evidence_list(
                metric_data["evidence"], display_name
            )

        validated_scores[display_name] = metric_data

    return {"independent_scores": validated_scores}


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


def convert_to_evidence_by_metric(
    stage1_response: dict,
    model_answer: str,
    anchor_len: int = 25,
    search_window: int = 2000
) -> dict[str, list[EvidenceItem]]:
    """
    Convert Stage 1 evidence to EvidenceByMetric format (Phase 3 schema).

    Validates evidence items, then verifies using the 5-stage self-healing
    algorithm before converting to Pydantic models.

    NOTE: This function accepts display name keys and converts them to slugs
    in the output, as required by Phase 3 Coach Chat schema.

    Args:
        stage1_response: Parsed Stage 1 response (display name keys)
        model_answer: Original model response text for verification
        anchor_len: From settings.evidence_anchor_len (default: 25)
        search_window: From settings.evidence_search_window (default: 2000)

    Returns:
        Dictionary mapping metric slugs to EvidenceItem lists
    """
    result = {}

    for display_name, metric_data in stage1_response.get("independent_scores", {}).items():
        # Convert display name to slug for Phase 3 output
        try:
            slug = display_name_to_slug(display_name)
        except ValueError:
            logger.warning(f"Unknown metric display name: {display_name}, skipping")
            continue

        evidence_list = metric_data.get("evidence", [])

        # First validate evidence structure (filters out invalid items)
        validated_list = _validate_evidence_list(evidence_list, display_name)

        # Then verify all valid evidence items using self-healing algorithm
        verified_list = verify_all_evidence(
            model_answer=model_answer,
            evidence_list=validated_list,
            anchor_len=anchor_len,
            search_window=search_window
        )

        # Convert to EvidenceItem Pydantic models
        evidence_items = []
        for item in verified_list:
            try:
                evidence_item = EvidenceItem(
                    quote=item["quote"],
                    start=item["start"],
                    end=item["end"],
                    why=item["why"],
                    better=item["better"],
                    verified=item["verified"],
                    highlight_available=item["highlight_available"]
                )
                evidence_items.append(evidence_item)
            except Exception as e:
                logger.warning(f"Failed to convert evidence item for {slug}: {e}")

        result[slug] = evidence_items

    return result


# =====================================================
# Evidence Verification (5-Stage Self-Healing Algorithm)
# Reference: Task 12.3 - AD-2
# =====================================================

def _verify_exact_slice(
    model_answer: str,
    quote: str,
    start: int,
    end: int
) -> tuple[bool, int, int]:
    """
    Stage 1: Exact slice verification (highest confidence).

    Checks if model_answer[start:end] exactly matches the quote.

    Args:
        model_answer: Original model response text
        quote: Evidence quote to verify
        start: Original start position
        end: Original end position

    Returns:
        (verified, start, end) - If verified=True, positions unchanged
    """
    # Bounds check
    if start < 0 or end > len(model_answer) or start >= end:
        return False, start, end

    actual = model_answer[start:end]
    if actual == quote:
        return True, start, end
    return False, start, end


def _verify_substring_search(
    model_answer: str,
    quote: str
) -> tuple[bool, int, int]:
    """
    Stage 2: Substring search (high confidence).

    Searches for exact quote in model_answer using str.find().

    Args:
        model_answer: Original model response text
        quote: Evidence quote to verify

    Returns:
        (verified, new_start, new_end) - New positions if found
    """
    idx = model_answer.find(quote)
    if idx >= 0:
        return True, idx, idx + len(quote)
    return False, 0, 0


def _verify_anchor_based(
    model_answer: str,
    quote: str,
    anchor_len: int,
    search_window: int
) -> tuple[bool, int, int]:
    """
    Stage 3: Anchor-based search (medium-high confidence).

    Searches for head and tail anchors in model_answer.
    Uses search window to prevent false positives in long texts.

    Args:
        model_answer: Original model response text
        quote: Evidence quote to verify
        anchor_len: Length of anchors (from settings.evidence_anchor_len)
        search_window: Search tolerance window (from settings.evidence_search_window)

    Returns:
        (verified, new_start, new_end) if both anchors found
    """
    # Quote too short for anchors
    if len(quote) < anchor_len * 2:
        return False, 0, 0

    head_anchor = quote[:anchor_len]
    tail_anchor = quote[-anchor_len:]

    head_idx = model_answer.find(head_anchor)
    if head_idx < 0:
        return False, 0, 0

    # Search for tail within window
    search_end = min(head_idx + len(quote) + search_window, len(model_answer))
    tail_idx = model_answer.find(tail_anchor, head_idx, search_end)

    if tail_idx >= 0:
        return True, head_idx, tail_idx + len(tail_anchor)

    return False, 0, 0


def _verify_whitespace_safe(
    model_answer: str,
    quote: str
) -> bool:
    """
    Stage 4: Whitespace-insensitive match (low confidence, safe mode).

    Normalizes both texts (removes excess whitespace/newlines) and searches.
    Returns verified=True BUT does NOT update positions (safe mode).

    Safe Mode: Don't update start/end because reverse mapping is error-prone.
    UI will show quote but disable highlight.

    Args:
        model_answer: Original model response text
        quote: Evidence quote to verify

    Returns:
        verified (bool) - True if found in normalized text
    """
    import re

    def normalize(text: str) -> str:
        """Remove excess whitespace, newlines."""
        return re.sub(r'\s+', ' ', text).strip()

    normalized_answer = normalize(model_answer)
    normalized_quote = normalize(quote)

    return normalized_quote in normalized_answer


def verify_evidence_item(
    model_answer: str,
    evidence_item: dict,
    anchor_len: int = 25,
    search_window: int = 2000
) -> dict:
    """
    Run 5-stage verification on a single evidence item.

    Stages run in order, stop at first success.

    Args:
        model_answer: Original model response text
        evidence_item: Dict with quote, start, end, why, better
        anchor_len: From settings.evidence_anchor_len
        search_window: From settings.evidence_search_window

    Returns:
        Updated evidence_item dict with verified and highlight_available set
    """
    quote = evidence_item["quote"]
    original_start = evidence_item["start"]
    original_end = evidence_item["end"]

    # Edge case: empty model_answer or quote
    if not model_answer or not quote:
        return {
            **evidence_item,
            "verified": False,
            "highlight_available": False,
            "start": original_start,
            "end": original_end
        }

    # Stage 1: Exact Slice
    verified, start, end = _verify_exact_slice(
        model_answer, quote, original_start, original_end
    )
    if verified:
        return {
            **evidence_item,
            "verified": True,
            "highlight_available": True,
            "start": start,
            "end": end
        }

    # Stage 2: Substring Search
    verified, start, end = _verify_substring_search(model_answer, quote)
    if verified:
        return {
            **evidence_item,
            "verified": True,
            "highlight_available": True,
            "start": start,
            "end": end
        }

    # Stage 3: Anchor-Based Search
    verified, start, end = _verify_anchor_based(
        model_answer, quote, anchor_len, search_window
    )
    if verified:
        return {
            **evidence_item,
            "verified": True,
            "highlight_available": True,
            "start": start,
            "end": end
        }

    # Stage 4: Whitespace-Insensitive Match (Safe Mode)
    verified = _verify_whitespace_safe(model_answer, quote)
    if verified:
        return {
            **evidence_item,
            "verified": True,
            "highlight_available": False,  # Safe mode: no highlight
            "start": original_start,       # Keep original for reference
            "end": original_end
        }

    # Stage 5: Fallback - Verification failed
    return {
        **evidence_item,
        "verified": False,
        "highlight_available": False,
        "start": original_start,
        "end": original_end
    }


def verify_all_evidence(
    model_answer: str,
    evidence_list: list[dict],
    anchor_len: int = 25,
    search_window: int = 2000
) -> list[dict]:
    """
    Verify all evidence items in a list.

    Args:
        model_answer: Original model response text
        evidence_list: List of evidence item dicts
        anchor_len: From settings.evidence_anchor_len
        search_window: From settings.evidence_search_window

    Returns:
        List of verified evidence items
    """
    return [
        verify_evidence_item(model_answer, item, anchor_len, search_window)
        for item in evidence_list
    ]


# =====================================================
# Evidence Processing Orchestration (Task 12.4)
# =====================================================

def process_evidence(
    model_answer: str,
    raw_evidence: dict[str, list],
    anchor_len: int = 25,
    search_window: int = 2000
) -> dict[str, list]:
    """
    Orchestrate evidence processing with graceful degradation.

    This is the single entry point for evidence processing that:
    1. Validates input structure
    2. Runs self-healing verification on all evidence items
    3. Returns processed evidence with verified/highlight_available flags
    4. Logs statistics per evaluation
    5. Handles graceful degradation on errors

    Args:
        model_answer: Original model response text for verification
        raw_evidence: Dict mapping metric display names to evidence lists
            {"Truthfulness": [{"quote": "...", "start": 0, "end": 10, ...}], ...}
        anchor_len: From settings.evidence_anchor_len (default: 25)
        search_window: From settings.evidence_search_window (default: 2000)

    Returns:
        Dict with same structure as input, containing verified evidence items:
        {
            "Truthfulness": [
                {
                    "quote": "...",
                    "start": 0,
                    "end": 10,
                    "why": "...",
                    "better": "...",
                    "verified": True,
                    "highlight_available": True
                },
                ...
            ],
            ...
        }

    Graceful Degradation:
    - Empty model_answer → skips verification, returns raw evidence with warnings
    - Invalid evidence list → treats as empty list, logs warning
    - Individual item failures don't stop processing of other items
    """
    # Initialize statistics
    total_items = 0
    total_verified = 0
    total_failed = 0
    total_items_with_highlight = 0

    # Validate input structure
    if not isinstance(raw_evidence, dict):
        logger.error(f"raw_evidence must be a dict, got {type(raw_evidence)}")
        return {}

    # Graceful degradation: empty model_answer
    if not model_answer:
        logger.warning(
            "Empty model_answer provided - skipping evidence verification. "
            "Returning raw evidence with verified=False, highlight_available=False"
        )
        # Add flags to all items without verification
        result = {}
        for metric_name, evidence_list in raw_evidence.items():
            if not isinstance(evidence_list, list):
                logger.warning(f"Evidence for {metric_name} is not a list, using empty array")
                result[metric_name] = []
                continue

            processed_list = []
            for item in evidence_list:
                if isinstance(item, dict):
                    processed_list.append({
                        **item,
                        "verified": False,
                        "highlight_available": False
                    })
            result[metric_name] = processed_list
        return result

    # Process each metric's evidence
    result = {}
    for metric_name, evidence_list in raw_evidence.items():
        # Handle missing or invalid evidence lists
        if not isinstance(evidence_list, list):
            logger.warning(
                f"Evidence for {metric_name} is not a list (got {type(evidence_list)}), "
                f"treating as empty array"
            )
            result[metric_name] = []
            continue

        # Skip empty lists
        if not evidence_list:
            result[metric_name] = []
            continue

        # Verify all evidence items for this metric
        try:
            verified_list = verify_all_evidence(
                model_answer=model_answer,
                evidence_list=evidence_list,
                anchor_len=anchor_len,
                search_window=search_window
            )

            # Update statistics
            for item in verified_list:
                total_items += 1
                if item.get("verified", False):
                    total_verified += 1
                else:
                    total_failed += 1
                if item.get("highlight_available", False):
                    total_items_with_highlight += 1

            result[metric_name] = verified_list

        except Exception as e:
            logger.error(
                f"Error verifying evidence for {metric_name}: {e}. "
                f"Returning unverified evidence."
            )
            # Graceful degradation: return items with verified=False
            fallback_list = []
            for item in evidence_list:
                if isinstance(item, dict):
                    total_items += 1
                    total_failed += 1
                    fallback_list.append({
                        **item,
                        "verified": False,
                        "highlight_available": False
                    })
            result[metric_name] = fallback_list

    # Log statistics
    logger.info(
        f"Evidence processing complete: "
        f"{total_verified}/{total_items} verified, "
        f"{total_failed} failed, "
        f"{total_items_with_highlight} with highlight_available=true"
    )

    return result
