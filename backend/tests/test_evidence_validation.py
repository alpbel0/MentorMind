"""
Unit tests for Judge Service Evidence Validation (Task 12.1)

Tests the evidence field validation in _validate_judge_response() method.

Run with: python3 backend/tests/test_evidence_validation.py
"""

import logging
import sys
import os
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class MockJudgeService:
    """Minimal mock of JudgeService with only the validation method."""

    logger = logging.getLogger(__name__)

    def _validate_judge_response(self, parsed: dict) -> dict:
        """Validate the structure of the parsed judge response with evidence support."""
        if not isinstance(parsed, dict):
            raise ValueError(f"GPT-4o response must be object, got {type(parsed)}")

        if "independent_scores" not in parsed:
            raise ValueError("GPT-4o response missing 'independent_scores' key")

        independent_scores = parsed["independent_scores"]

        if not isinstance(independent_scores, dict):
            raise ValueError("'independent_scores' must be object")

        # Validate evidence structure for each metric
        for metric_name, metric_data in independent_scores.items():
            if not isinstance(metric_data, dict):
                self.logger.warning(f"Metric data for {metric_name} is not a dict, skipping evidence validation")
                continue

            if "evidence" not in metric_data:
                self.logger.warning(f"Evidence field missing for {metric_name}, adding empty array")
                metric_data["evidence"] = []
                continue

            evidence_list = metric_data["evidence"]
            if not isinstance(evidence_list, list):
                self.logger.warning(f"Evidence for {metric_name} is not a list, converting to empty array")
                metric_data["evidence"] = []
                continue

            validated_evidence = []
            for idx, item in enumerate(evidence_list):
                if not isinstance(item, dict):
                    self.logger.warning(f"Evidence item {idx} for {metric_name} is not a dict, skipping")
                    continue

                required_fields = ["quote", "start", "end", "why", "better"]
                if not all(field in item for field in required_fields):
                    missing = [f for f in required_fields if f not in item]
                    self.logger.warning(f"Evidence item {idx} for {metric_name} missing fields {missing}, skipping")
                    continue

                if not isinstance(item["quote"], str) or not item["quote"].strip():
                    self.logger.warning(f"Evidence item {idx} for {metric_name} has invalid quote, skipping")
                    continue

                if not isinstance(item["start"], int) or not isinstance(item["end"], int):
                    self.logger.warning(f"Evidence item {idx} for {metric_name} has invalid start/end, skipping")
                    continue

                if item["start"] >= item["end"]:
                    self.logger.warning(f"Evidence item {idx} for {metric_name} has start >= end, setting to 0,0")
                    item["start"] = 0
                    item["end"] = 0

                if not isinstance(item["better"], str):
                    self.logger.warning(f"Evidence item {idx} for {metric_name} has invalid 'better', converting to empty string")
                    item["better"] = ""

                validated_evidence.append(item)

            metric_data["evidence"] = validated_evidence

        return parsed


def run_test(test_func, name):
    """Run a single test and return True if passed."""
    try:
        test_func()
        print(f"  {name}: PASSED")
        return True
    except AssertionError as e:
        print(f"  {name}: FAILED - {e}")
        return False
    except Exception as e:
        print(f"  {name}: ERROR - {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Evidence Validation Tests (Task 12.1)")
    print("=" * 60)

    judge_service = MockJudgeService()
    tests_passed = 0
    tests_failed = 0

    # Test 1: Valid evidence accepted
    def test1():
        response = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 3,
                    "rationale": "Test",
                    "evidence": [{"quote": "Test quote", "start": 0, "end": 9, "why": "T", "better": "B"}]
                }
            }
        }
        result = judge_service._validate_judge_response(response)
        assert len(result["independent_scores"]["Truthfulness"]["evidence"]) == 1

    if run_test(test1, "Valid evidence accepted"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 2: Missing evidence field adds empty array
    def test2():
        response = {"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test"}}}
        result = judge_service._validate_judge_response(response)
        assert result["independent_scores"]["Truthfulness"]["evidence"] == []

    if run_test(test2, "Missing evidence field adds empty array"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 3: Non-list evidence converts to empty array
    def test3():
        response = {"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test", "evidence": "not a list"}}}
        result = judge_service._validate_judge_response(response)
        assert result["independent_scores"]["Truthfulness"]["evidence"] == []

    if run_test(test3, "Non-list evidence converts to empty array"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 4: Evidence item missing required fields filtered
    def test4():
        response = {"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test", "evidence": [{"quote": "T", "start": 0, "end": 1}]}}}
        result = judge_service._validate_judge_response(response)
        assert result["independent_scores"]["Truthfulness"]["evidence"] == []

    if run_test(test4, "Evidence item missing required fields filtered"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 5: Invalid quote filtered
    def test5():
        response = {"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test", "evidence": [{"quote": "", "start": 0, "end": 0, "why": "T", "better": "B"}]}}}
        result = judge_service._validate_judge_response(response)
        assert result["independent_scores"]["Truthfulness"]["evidence"] == []

    if run_test(test5, "Invalid quote filtered"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 6: Invalid start/end filtered
    def test6():
        response = {"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test", "evidence": [{"quote": "T", "start": "0", "end": 1, "why": "T", "better": "B"}]}}}
        result = judge_service._validate_judge_response(response)
        assert result["independent_scores"]["Truthfulness"]["evidence"] == []

    if run_test(test6, "Invalid start/end filtered"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 7: start >= end corrected to 0,0
    def test7():
        response = {"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test", "evidence": [{"quote": "T", "start": 10, "end": 5, "why": "T", "better": "B"}]}}}
        result = judge_service._validate_judge_response(response)
        assert result["independent_scores"]["Truthfulness"]["evidence"][0]["start"] == 0
        assert result["independent_scores"]["Truthfulness"]["evidence"][0]["end"] == 0

    if run_test(test7, "start >= end corrected to 0,0"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 8: Invalid better converted to empty string
    def test8():
        response = {"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test", "evidence": [{"quote": "T", "start": 0, "end": 1, "why": "T", "better": 123}]}}}
        result = judge_service._validate_judge_response(response)
        assert result["independent_scores"]["Truthfulness"]["evidence"][0]["better"] == ""

    if run_test(test8, "Invalid better converted to empty string"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 9: Multiple evidence items - valid kept, invalid filtered
    def test9():
        response = {
            "independent_scores": {
                "Truthfulness": {
                    "score": 3,
                    "rationale": "Test",
                    "evidence": [
                        {"quote": "Valid 1", "start": 0, "end": 7, "why": "T", "better": "B"},
                        {"quote": "Invalid", "start": 0, "end": 7},
                        {"quote": "Valid 2", "start": 10, "end": 17, "why": "T", "better": "B"}
                    ]
                }
            }
        }
        result = judge_service._validate_judge_response(response)
        assert len(result["independent_scores"]["Truthfulness"]["evidence"]) == 2
        assert result["independent_scores"]["Truthfulness"]["evidence"][0]["quote"] == "Valid 1"
        assert result["independent_scores"]["Truthfulness"]["evidence"][1]["quote"] == "Valid 2"

    if run_test(test9, "Multiple evidence items filtered correctly"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 10: All 8 metrics with evidence
    def test10():
        response = {
            "independent_scores": {
                "Truthfulness": {"score": 3, "rationale": "T", "evidence": []},
                "Helpfulness": {"score": 5, "rationale": "H", "evidence": []},
                "Safety": {"score": 5, "rationale": "S", "evidence": []},
                "Bias": {"score": None, "rationale": "B", "evidence": []},
                "Clarity": {"score": 2, "rationale": "C", "evidence": []},
                "Consistency": {"score": 5, "rationale": "C", "evidence": []},
                "Efficiency": {"score": 4, "rationale": "E", "evidence": []},
                "Robustness": {"score": 3, "rationale": "R", "evidence": []}
            }
        }
        result = judge_service._validate_judge_response(response)
        for metric in ["Truthfulness", "Helpfulness", "Safety", "Bias", "Clarity", "Consistency", "Efficiency", "Robustness"]:
            assert metric in result["independent_scores"]
            assert "evidence" in result["independent_scores"][metric]

    if run_test(test10, "All 8 metrics with evidence"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 11: Empty better string allowed
    def test11():
        response = {"independent_scores": {"Truthfulness": {"score": 5, "rationale": "Test", "evidence": [{"quote": "T", "start": 0, "end": 1, "why": "T", "better": ""}]}}}
        result = judge_service._validate_judge_response(response)
        assert result["independent_scores"]["Truthfulness"]["evidence"][0]["better"] == ""

    if run_test(test11, "Empty better string allowed"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 12: Non-dict metric data skips gracefully
    def test12():
        response = {"independent_scores": {"Truthfulness": "invalid"}}
        result = judge_service._validate_judge_response(response)
        assert "Truthfulness" in result["independent_scores"]

    if run_test(test12, "Non-dict metric data skips gracefully"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 13: Non-dict evidence item skipped
    def test13():
        response = {"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test", "evidence": ["not a dict", {"quote": "v", "start": 0, "end": 1, "why": "t", "better": "b"}]}}}
        result = judge_service._validate_judge_response(response)
        assert len(result["independent_scores"]["Truthfulness"]["evidence"]) == 1

    if run_test(test13, "Non-dict evidence item skipped"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Prompt content tests
    print()
    print("-" * 60)
    print("Prompt Content Tests")
    print("-" * 60)

    # Test 14: Stage 1 system prompt has evidence section
    def test14():
        from backend.prompts.judge_prompts import JUDGE_STAGE1_SYSTEM_PROMPT
        assert "evidence" in JUDGE_STAGE1_SYSTEM_PROMPT.lower()
        assert "verbatim" in JUDGE_STAGE1_SYSTEM_PROMPT.lower()
        assert "character position" in JUDGE_STAGE1_SYSTEM_PROMPT.lower()

    if run_test(test14, "Stage 1 system prompt has evidence section"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 15: Stage 1 system prompt has all 5 fields
    def test15():
        from backend.prompts.judge_prompts import JUDGE_STAGE1_SYSTEM_PROMPT
        assert '"quote"' in JUDGE_STAGE1_SYSTEM_PROMPT
        assert '"start"' in JUDGE_STAGE1_SYSTEM_PROMPT
        assert '"end"' in JUDGE_STAGE1_SYSTEM_PROMPT
        assert '"why"' in JUDGE_STAGE1_SYSTEM_PROMPT
        assert '"better"' in JUDGE_STAGE1_SYSTEM_PROMPT

    if run_test(test15, "Stage 1 system prompt has all 5 field names"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 16: Stage 1 user prompt has evidence example
    def test16():
        from backend.prompts.judge_prompts import JUDGE_STAGE1_USER_PROMPT_TEMPLATE
        assert "evidence" in JUDGE_STAGE1_USER_PROMPT_TEMPLATE.lower()
        assert '"evidence"' in JUDGE_STAGE1_USER_PROMPT_TEMPLATE

    if run_test(test16, "Stage 1 user prompt has evidence example"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 17: Stage 1 example output includes evidence structure
    def test17():
        from backend.prompts.judge_prompts import JUDGE_STAGE1_SYSTEM_PROMPT
        assert '"evidence": [' in JUDGE_STAGE1_SYSTEM_PROMPT

    if run_test(test17, "Stage 1 example output includes evidence array"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Summary
    print()
    print("=" * 60)
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    print(f"Total tests: {tests_passed + tests_failed}")
    print("=" * 60)

    if tests_failed == 0:
        print("ALL TESTS PASSED!")
        return 0
    else:
        print("SOME TESTS FAILED!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
