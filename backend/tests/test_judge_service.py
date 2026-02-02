"""
Tests for Judge Service - Live GPT-4o API

These tests use live GPT-4o API calls (no mocks).
Ensure OPENAI_API_KEY is set in environment.
"""

import pytest
from sqlalchemy.orm import Session

from backend.services.judge_service import JudgeService, THE_EIGHT_METRICS
from backend.models.user_evaluation import UserEvaluation
from backend.models.model_response import ModelResponse
from backend.models.question import Question


class TestJudgeServiceInit:
    """Test JudgeService initialization."""

    def test_service_initialization(self):
        """Test JudgeService initializes correctly."""
        service = JudgeService()
        assert service.model == "gpt-4o"
        assert service.client is not None
        assert service.timeout == 60


class TestFetchEvaluationData:
    """Test data fetching logic."""

    def test_fetch_evaluation_data_success(self, db_session):
        """Test successful data fetching with inline data creation."""
        # Setup: Create test data inline (no external fixture)
        from datetime import datetime
        question = Question(
            id="q_fetch_test_001",
            question="Test question?",
            category="Testing",
            difficulty="medium",
            reference_answer="Test answer",
            expected_behavior="Test behavior",
            rubric_breakdown={"1": "Bad", "5": "Good"},
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()  # Flush to get the question in the DB before creating model_response

        model_response = ModelResponse(
            id="resp_fetch_test_001",
            question_id="q_fetch_test_001",
            model_name="openai/gpt-3.5-turbo",
            response_text="Test response",
            evaluated=False
        )
        db_session.add(model_response)

        user_eval = UserEvaluation(
            id="eval_fetch_test_001",
            response_id="resp_fetch_test_001",
            evaluations={
                "Truthfulness": {"score": 3, "reasoning": "Test"},
                "Helpfulness": {"score": 3, "reasoning": "Test"},
                "Safety": {"score": None, "reasoning": "N/A"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Clarity": {"score": 3, "reasoning": "Test"},
                "Consistency": {"score": None, "reasoning": "N/A"},
                "Efficiency": {"score": None, "reasoning": "N/A"},
                "Robustness": {"score": None, "reasoning": "N/A"}
            },
            judged=False
        )
        db_session.add(user_eval)
        db_session.commit()

        # Execute
        service = JudgeService()
        result = service.fetch_evaluation_data("eval_fetch_test_001", db_session)

        # Verify
        assert "user_eval" in result
        assert "model_response" in result
        assert "question" in result
        assert "user_scores" in result
        assert len(result["user_scores"]) == 8

    def test_fetch_evaluation_data_not_found(self, db_session):
        """Test error when evaluation not found."""
        service = JudgeService()
        with pytest.raises(ValueError, match="not found"):
            service.fetch_evaluation_data("eval_nonexistent", db_session)

    def test_fetch_evaluation_data_missing_metrics(self, db_session):
        """Test error when user evaluation missing metrics."""
        # Create evaluation with only 1 metric (inline, no fixture)
        from datetime import datetime
        question = Question(
            id="q_fetch_test_002",
            question="Test?",
            category="Test",
            difficulty="medium",
            reference_answer="Answer",
            expected_behavior="Behavior",
            rubric_breakdown={"1": "Bad", "5": "Good"},
            primary_metric="Truthfulness",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()  # Flush before creating model_response

        model_response = ModelResponse(
            id="resp_fetch_test_002",
            question_id="q_fetch_test_002",
            model_name="openai/gpt-3.5-turbo",
            response_text="Response",
            evaluated=False
        )
        db_session.add(model_response)

        user_eval = UserEvaluation(
            id="eval_fetch_test_002",
            response_id="resp_fetch_test_002",
            evaluations={"Truthfulness": {"score": 3, "reasoning": "..."}}
        )
        db_session.add(user_eval)
        db_session.commit()

        service = JudgeService()
        with pytest.raises(ValueError, match="missing metrics"):
            service.fetch_evaluation_data("eval_fetch_test_002", db_session)


class TestParseJudgeResponse:
    """Test response parsing."""

    def test_parse_direct_json(self):
        """Test parsing direct JSON."""
        service = JudgeService()
        response = '{"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test"}}}'
        result = service.parse_judge_response(response)
        assert "independent_scores" in result
        assert result["independent_scores"]["Truthfulness"]["score"] == 3

    def test_parse_markdown_json(self):
        """Test parsing JSON in markdown code block."""
        service = JudgeService()
        response = '''```json
{
  "independent_scores": {
    "Truthfulness": {"score": 4, "rationale": "Test"}
  }
}
```'''
        result = service.parse_judge_response(response)
        assert "independent_scores" in result

    def test_parse_with_extra_text(self):
        """Test parsing JSON with extra text before/after."""
        service = JudgeService()
        response = '''Here is the evaluation:

```json
{"independent_scores": {"Truthfulness": {"score": 3, "rationale": "Test"}}}
```

That's my assessment.'''
        result = service.parse_judge_response(response)
        assert "independent_scores" in result

    def test_parse_invalid_json(self):
        """Test error on invalid JSON."""
        service = JudgeService()
        with pytest.raises(ValueError, match="Invalid JSON"):
            service.parse_judge_response("not json at all")

    def test_parse_missing_key(self):
        """Test error when independent_scores missing."""
        service = JudgeService()
        with pytest.raises(ValueError, match="missing 'independent_scores'"):
            service.parse_judge_response('{"other_key": "value"}')


class TestStage1LiveAPI:
    """Test Stage 1 evaluation with live GPT-4o API."""

    @pytest.mark.live_api
    def test_stage1_wrong_answer(self, db_session):
        """Test Stage 1 with a wrong model response."""
        # Setup: Create test evaluation with wrong answer (inline data)
        from datetime import datetime
        question = Question(
            id="q_test_001",
            question="What is 2+2?",
            category="Mathematics",
            difficulty="easy",
            reference_answer="4",
            expected_behavior="Model should answer correctly",
            rubric_breakdown={
                "1": "Completely wrong",
                "5": "Correct answer"
            },
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Helpfulness"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()  # Flush before creating model_response

        model_response = ModelResponse(
            id="resp_test_001",
            question_id="q_test_001",
            model_name="openai/gpt-3.5-turbo",
            response_text="The answer is 5.",
            evaluated=False
        )
        db_session.add(model_response)
        db_session.flush()  # Flush before creating user_evaluation

        user_eval = UserEvaluation(
            id="eval_test_001",
            response_id="resp_test_001",
            evaluations={
                "Truthfulness": {"score": 2, "reasoning": "Wrong answer"},
                "Helpfulness": {"score": 3, "reasoning": "Brief but incorrect"},
                "Safety": {"score": None, "reasoning": "Not applicable"},
                "Bias": {"score": None, "reasoning": "Not applicable"},
                "Clarity": {"score": 5, "reasoning": "Clear"},
                "Consistency": {"score": None, "reasoning": "Not applicable"},
                "Efficiency": {"score": 4, "reasoning": "Concise"},
                "Robustness": {"score": None, "reasoning": "Not applicable"}
            },
            judged=False
        )
        db_session.add(user_eval)
        db_session.commit()

        # Execute: Call Stage 1
        service = JudgeService()
        result = service.stage1_independent_evaluation("eval_test_001", db_session)

        # Verify
        assert "independent_scores" in result
        scores = result["independent_scores"]

        # All 8 metrics present
        assert len(scores) == 8
        for metric in THE_EIGHT_METRICS:
            assert metric in scores
            assert "score" in scores[metric]
            assert "rationale" in scores[metric]

            # Score validation
            score = scores[metric]["score"]
            assert score is None or isinstance(score, int)
            if score is not None:
                assert 1 <= score <= 5

            # Rationale is string (Turkish expected)
            assert isinstance(scores[metric]["rationale"], str)
            assert len(scores[metric]["rationale"]) > 0

        # Log for manual verification
        print(f"\n=== GPT-4o Stage 1 Evaluation ===")
        for metric, data in scores.items():
            if data["score"] is not None:
                print(f"{metric}: {data['score']}/5 - {data['rationale']}")

    @pytest.mark.live_api
    def test_stage1_correct_response(self, db_session):
        """Test Stage 1 with a correct model response."""
        # Create question where model answers correctly (inline data)
        from datetime import datetime
        question = Question(
            id="q_test_002",
            question="What is the capital of France?",
            category="Geography",
            difficulty="easy",
            reference_answer="Paris",
            expected_behavior="Model should identify Paris",
            rubric_breakdown={"1": "Wrong", "5": "Correct"},
            primary_metric="Truthfulness",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()  # Flush before creating model_response

        model_response = ModelResponse(
            id="resp_test_002",
            question_id="q_test_002",
            model_name="openai/gpt-4o-mini",
            response_text="The capital of France is Paris.",
            evaluated=False
        )
        db_session.add(model_response)
        db_session.flush()  # Flush before creating user_evaluation

        user_eval = UserEvaluation(
            id="eval_test_002",
            response_id="resp_test_002",
            evaluations={metric: {"score": None, "reasoning": "N/A"} for metric in [
                "Truthfulness", "Helpfulness", "Safety", "Bias",
                "Clarity", "Consistency", "Efficiency", "Robustness"
            ]},
            judged=False
        )
        db_session.add(user_eval)
        db_session.commit()

        service = JudgeService()
        result = service.stage1_independent_evaluation("eval_test_002", db_session)

        # Truthfulness should be 5 (correct answer)
        truthfulness = result["independent_scores"]["Truthfulness"]
        assert truthfulness["score"] >= 4  # Should be high for correct answer


class TestComparisonTableGenerator:
    """Test generate_comparison_table helper function (Task 4.4)."""

    def test_generate_comparison_table_full_alignment(self):
        """Test table when user and judge scores match perfectly."""
        user_scores = {metric: {"score": 3, "reasoning": "..."} for metric in THE_EIGHT_METRICS}
        judge_scores = {metric: {"score": 3, "rationale": "..."} for metric in THE_EIGHT_METRICS}

        service = JudgeService()
        table = service.generate_comparison_table(user_scores, judge_scores)

        # Verify table structure: header + separator + 8 data rows = 10 rows
        rows = table.strip().split("\n")
        assert len(rows) == 10

        # Verify header row
        assert rows[0] == "| Metric | User Score | Judge Score | Gap | Verdict |"
        # Verify separator row
        assert rows[1] == "|--------|------------|-------------|-----|---------|"

        # Verify all data rows show "aligned" verdict
        for metric in THE_EIGHT_METRICS:
            assert f"{metric} | 3 | 3 | 0 | aligned" in table

    def test_generate_comparison_table_header_format(self):
        """Test that table has proper Markdown header and separator."""
        user_scores = {metric: {"score": 3, "reasoning": "..."} for metric in THE_EIGHT_METRICS}
        judge_scores = {metric: {"score": 3, "rationale": "..."} for metric in THE_EIGHT_METRICS}

        service = JudgeService()
        table = service.generate_comparison_table(user_scores, judge_scores)

        lines = table.strip().split("\n")

        # Header must be first
        assert "| Metric |" in lines[0]
        assert "| User Score |" in lines[0]
        assert "| Judge Score |" in lines[0]
        assert "| Gap |" in lines[0]
        assert "| Verdict |" in lines[0]

        # Separator must be second with dashes
        assert "|--------|" in lines[1]
        assert lines[1].count("---") >= 5  # At least 5 column separators

    def test_generate_comparison_table_with_nulls(self):
        """Test table with null scores."""
        user_scores = {
            "Truthfulness": {"score": 4, "reasoning": "..."},
            "Helpfulness": {"score": None, "reasoning": "N/A"},
            "Safety": {"score": None, "reasoning": "N/A"},
            "Bias": {"score": None, "reasoning": "N/A"},
            "Clarity": {"score": 5, "reasoning": "..."},
            "Consistency": {"score": None, "reasoning": "N/A"},
            "Efficiency": {"score": None, "reasoning": "N/A"},
            "Robustness": {"score": None, "reasoning": "N/A"},
        }
        judge_scores = {
            "Truthfulness": {"score": 3, "rationale": "..."},
            "Helpfulness": {"score": 5, "rationale": "..."},
            "Safety": {"score": 4, "rationale": "..."},
            "Bias": {"score": 5, "rationale": "..."},
            "Clarity": {"score": 4, "rationale": "..."},
            "Consistency": {"score": 5, "rationale": "..."},
            "Efficiency": {"score": 5, "rationale": "..."},
            "Robustness": {"score": 5, "rationale": "..."},
        }

        service = JudgeService()
        table = service.generate_comparison_table(user_scores, judge_scores)

        # Truthfulness: gap=1, slightly_over
        assert "Truthfulness | 4 | 3 | 1 | slightly_over_estimated" in table
        # Clarity: gap=1, slightly_over
        assert "Clarity | 5 | 4 | 1 | slightly_over_estimated" in table
        # Helpfulness: N/A verdict (user null)
        assert "Helpfulness | N/A | 5 | 0 | not_applicable" in table

    def test_generate_comparison_table_over_under(self):
        """Test verdict direction based on gap."""
        user_scores = {
            "Truthfulness": {"score": 5, "reasoning": "..."},  # Over by 2
            "Helpfulness": {"score": 3, "reasoning": "..."},   # Aligned
            "Safety": {"score": 2, "reasoning": "..."},        # Under by 2
            "Bias": {"score": 3, "reasoning": "..."},         # Aligned
            "Clarity": {"score": 5, "reasoning": "..."},      # Over by 3+
            "Consistency": {"score": 3, "reasoning": "..."},  # Aligned
            "Efficiency": {"score": 3, "reasoning": "..."},   # Aligned
            "Robustness": {"score": 3, "reasoning": "..."},   # Aligned
        }
        judge_scores = {
            "Truthfulness": {"score": 3, "rationale": "..."},
            "Helpfulness": {"score": 3, "rationale": "..."},
            "Safety": {"score": 4, "rationale": "..."},
            "Bias": {"score": 3, "rationale": "..."},
            "Clarity": {"score": 1, "rationale": "..."},
            "Consistency": {"score": 3, "rationale": "..."},
            "Efficiency": {"score": 3, "rationale": "..."},
            "Robustness": {"score": 3, "rationale": "..."},
        }

        service = JudgeService()
        table = service.generate_comparison_table(user_scores, judge_scores)

        assert "Truthfulness | 5 | 3 | 2 | moderately_over_estimated" in table
        assert "Safety | 2 | 4 | 2 | moderately_under_estimated" in table
        assert "Clarity | 5 | 1 | 4 | significantly_over_estimated" in table
        assert "Helpfulness | 3 | 3 | 0 | aligned" in table


class TestWeightedGapCalculator:
    """Test calculate_weighted_gap helper function (Task 4.5)."""

    def test_calculate_weighted_gap_perfect_alignment(self):
        """Test weighted gap when all scores match."""
        user_scores = {metric: {"score": 3} for metric in THE_EIGHT_METRICS}
        judge_scores = {metric: {"score": 3} for metric in THE_EIGHT_METRICS}

        service = JudgeService()
        gap = service.calculate_weighted_gap(
            user_scores, judge_scores,
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Safety"]
        )

        assert gap == 0.0

    def test_calculate_weighted_gap_primary_mismatch(self):
        """Test weighted gap when only primary metric differs."""
        # Primary: Truthfulness (gap=2)
        # Bonus: Clarity (gap=0), Safety (gap=0)
        # Other: all gap=0
        user_scores = {
            "Truthfulness": {"score": 5},  # Gap=2
            "Clarity": {"score": 3},       # Gap=0
            "Safety": {"score": 3},        # Gap=0
            **{m: {"score": 3} for m in THE_EIGHT_METRICS if m not in ["Truthfulness", "Clarity", "Safety"]}
        }
        judge_scores = {
            "Truthfulness": {"score": 3},
            "Clarity": {"score": 3},
            "Safety": {"score": 3},
            **{m: {"score": 3} for m in THE_EIGHT_METRICS if m not in ["Truthfulness", "Clarity", "Safety"]}
        }

        service = JudgeService()
        gap = service.calculate_weighted_gap(
            user_scores, judge_scores,
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Safety"]
        )

        # weighted_gap = 2 * 0.7 + 0 * 0.2 + 0 * 0.1 = 1.4
        assert gap == 1.4

    def test_calculate_weighted_gap_bonus_mismatch(self):
        """Test weighted gap when bonus metrics differ."""
        # Primary: Truthfulness (gap=0)
        # Bonus: Clarity (gap=2), Safety (gap=2) -> avg=2
        # Other: all gap=0
        user_scores = {
            "Truthfulness": {"score": 3},  # Gap=0
            "Clarity": {"score": 5},       # Gap=2
            "Safety": {"score": 5},        # Gap=2
            **{m: {"score": 3} for m in THE_EIGHT_METRICS if m not in ["Truthfulness", "Clarity", "Safety"]}
        }
        judge_scores = {
            "Truthfulness": {"score": 3},
            "Clarity": {"score": 3},
            "Safety": {"score": 3},
            **{m: {"score": 3} for m in THE_EIGHT_METRICS if m not in ["Truthfulness", "Clarity", "Safety"]}
        }

        service = JudgeService()
        gap = service.calculate_weighted_gap(
            user_scores, judge_scores,
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Safety"]
        )

        # weighted_gap = 0 * 0.7 + 2 * 0.2 + 0 * 0.1 = 0.4
        assert gap == 0.4

    def test_calculate_weighted_gap_with_nulls(self):
        """Test weighted gap with null scores (should be excluded)."""
        user_scores = {
            "Truthfulness": {"score": 4},  # Gap=1
            "Clarity": {"score": None},    # Excluded
            "Safety": {"score": None},     # Excluded
            **{m: {"score": 3} for m in THE_EIGHT_METRICS if m not in ["Truthfulness", "Clarity", "Safety"]}
        }
        judge_scores = {
            "Truthfulness": {"score": 3},
            "Clarity": {"score": 5},       # Excluded (user null)
            "Safety": {"score": 2},        # Excluded (user null)
            **{m: {"score": 3} for m in THE_EIGHT_METRICS if m not in ["Truthfulness", "Clarity", "Safety"]}
        }

        service = JudgeService()
        gap = service.calculate_weighted_gap(
            user_scores, judge_scores,
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Safety"]
        )

        # Primary gap=1, bonus excluded (treated as 0), other=0
        # weighted_gap = 1 * 0.7 + 0 * 0.2 + 0 * 0.1 = 0.7
        assert gap == 0.7

    def test_calculate_weighted_gap_complex(self):
        """Test weighted gap with mixed gaps across all categories."""
        # Primary: Truthfulness (gap=1)
        # Bonus: Clarity (gap=1), Safety (gap=3) -> avg=2
        # Other: 5 metrics with avg gap=1.6
        user_scores = {
            "Truthfulness": {"score": 4},  # Gap=1
            "Clarity": {"score": 4},       # Gap=1
            "Safety": {"score": 5},        # Gap=3
            "Bias": {"score": 5},          # Gap=2
            "Helpfulness": {"score": 4},   # Gap=1
            "Consistency": {"score": 5},   # Gap=2
            "Efficiency": {"score": 4},    # Gap=1
            "Robustness": {"score": 4},    # Gap=2
        }
        judge_scores = {
            "Truthfulness": {"score": 3},
            "Clarity": {"score": 3},
            "Safety": {"score": 2},
            "Bias": {"score": 3},
            "Helpfulness": {"score": 3},
            "Consistency": {"score": 3},
            "Efficiency": {"score": 3},
            "Robustness": {"score": 2},
        }

        service = JudgeService()
        gap = service.calculate_weighted_gap(
            user_scores, judge_scores,
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Safety"]
        )

        # Primary gap=1, bonus avg=2, other avg=(2+1+2+1+2)/5=1.6
        # weighted_gap = 1 * 0.7 + 2 * 0.2 + 1.6 * 0.1 = 0.7 + 0.4 + 0.16 = 1.26
        assert gap == 1.26


class TestMetaScoreMapper:
    """Test weighted_gap_to_meta_score helper function (Task 4.6)."""

    def test_meta_score_excellent_alignment(self):
        """Test meta score 5 (excellent alignment)."""
        service = JudgeService()

        # All gaps <= 0.5 should map to 5
        assert service.weighted_gap_to_meta_score(0.0) == 5
        assert service.weighted_gap_to_meta_score(0.3) == 5
        assert service.weighted_gap_to_meta_score(0.5) == 5  # Boundary

    def test_meta_score_good_alignment(self):
        """Test meta score 4 (good alignment)."""
        service = JudgeService()

        # Gaps > 0.5 and <= 1.0 should map to 4
        assert service.weighted_gap_to_meta_score(0.6) == 4
        assert service.weighted_gap_to_meta_score(0.7) == 4
        assert service.weighted_gap_to_meta_score(1.0) == 4  # Boundary

    def test_meta_score_moderate_alignment(self):
        """Test meta score 3 (moderate alignment)."""
        service = JudgeService()

        # Gaps > 1.0 and <= 1.5 should map to 3
        assert service.weighted_gap_to_meta_score(1.1) == 3
        assert service.weighted_gap_to_meta_score(1.2) == 3
        assert service.weighted_gap_to_meta_score(1.5) == 3  # Boundary

    def test_meta_score_poor_alignment(self):
        """Test meta score 2 (poor alignment)."""
        service = JudgeService()

        # Gaps > 1.5 and <= 2.0 should map to 2
        assert service.weighted_gap_to_meta_score(1.6) == 2
        assert service.weighted_gap_to_meta_score(1.8) == 2
        assert service.weighted_gap_to_meta_score(2.0) == 2  # Boundary

    def test_meta_score_very_poor_alignment(self):
        """Test meta score 1 (very poor alignment)."""
        service = JudgeService()

        # Gaps > 2.0 should map to 1
        assert service.weighted_gap_to_meta_score(2.1) == 1
        assert service.weighted_gap_to_meta_score(2.5) == 1
        assert service.weighted_gap_to_meta_score(3.0) == 1
        assert service.weighted_gap_to_meta_score(5.0) == 1  # Max gap

    def test_meta_score_rounded_values(self):
        """Test meta score with typical weighted gap values."""
        service = JudgeService()

        # Test common rounded values
        assert service.weighted_gap_to_meta_score(0.7) == 4   # Primary gap=1, all others aligned
        assert service.weighted_gap_to_meta_score(1.4) == 3   # Primary gap=2, all others aligned
        assert service.weighted_gap_to_meta_score(0.4) == 5   # Excellent alignment


class TestFormatPastMistakes:
    """Test _format_past_mistakes helper function (Task 4.7)."""

    def test_format_past_mistakes_empty(self):
        """Test formatting with empty ChromaDB results."""
        service = JudgeService()
        result = service._format_past_mistakes({"evaluations": []})
        assert result == ""

    def test_format_past_mistakes_with_data(self):
        """Test formatting with actual ChromaDB results."""
        service = JudgeService()
        vector_context = {
            "evaluations": [
                {
                    "evaluation_id": "eval_001",
                    "judge_meta_score": 3,
                    "primary_gap": 1.2,
                    "feedback": "Overestimated minor errors in Truthfulness"
                },
                {
                    "evaluation_id": "eval_002",
                    "judge_meta_score": 4,
                    "primary_gap": 0.5,
                    "feedback": "Good alignment overall"
                }
            ]
        }

        result = service._format_past_mistakes(vector_context)

        assert "Önceki benzer değerlendirmelerinizden dikkate değer kalıplar:" in result
        assert "Meta Skor: 3/5" in result
        assert "Birincil Metrik Farkı: 1.2" in result
        assert "Overestimated minor errors" in result

    def test_format_past_mistakes_truncates_long_feedback(self):
        """Test that long feedback is truncated."""
        service = JudgeService()
        long_feedback = "A" * 200
        vector_context = {
            "evaluations": [
                {
                    "evaluation_id": "eval_001",
                    "judge_meta_score": 3,
                    "primary_gap": 1.0,
                    "feedback": long_feedback
                }
            ]
        }

        result = service._format_past_mistakes(vector_context)

        # Should be truncated with ellipsis (check feedback line specifically)
        assert "..." in result
        # The feedback itself should be truncated to 100 chars + "..."
        assert "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA..." in result


class TestParseStage2Response:
    """Test parse_stage2_response method (Task 4.7)."""

    def test_parse_stage2_response_valid(self):
        """Test parsing valid Stage 2 JSON response."""
        service = JudgeService()
        response = '''{
  "alignment_analysis": {
    "Truthfulness": {"user_score": 4, "judge_score": 3, "gap": 1, "verdict": "slightly_over_estimated", "feedback": "Test"},
    "Helpfulness": {"user_score": 5, "judge_score": 5, "gap": 0, "verdict": "aligned", "feedback": "Test"},
    "Safety": {"user_score": null, "judge_score": 5, "gap": 0, "verdict": "not_applicable", "feedback": "Test"},
    "Bias": {"user_score": null, "judge_score": 5, "gap": 0, "verdict": "not_applicable", "feedback": "Test"},
    "Clarity": {"user_score": 3, "judge_score": 4, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"},
    "Consistency": {"user_score": 4, "judge_score": 4, "gap": 0, "verdict": "aligned", "feedback": "Test"},
    "Efficiency": {"user_score": 4, "judge_score": 5, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"},
    "Robustness": {"user_score": 2, "judge_score": 3, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"}
  },
  "judge_meta_score": 4,
  "overall_feedback": "Genel olarak başarılı",
  "improvement_areas": ["Daha eleştirel olun"],
  "positive_feedback": ["Doğru değerlendirme"]
}'''
        result = service.parse_stage2_response(response)

        assert "alignment_analysis" in result
        assert result["judge_meta_score"] == 4
        assert result["overall_feedback"] == "Genel olarak başarılı"
        assert len(result["improvement_areas"]) == 1
        assert len(result["positive_feedback"]) == 1

    def test_parse_stage2_response_markdown(self):
        """Test parsing Stage 2 response in markdown code block."""
        service = JudgeService()
        response = '''```json
{
  "alignment_analysis": {
    "Truthfulness": {"user_score": 4, "judge_score": 3, "gap": 1, "verdict": "slightly_over_estimated", "feedback": "Test"},
    "Helpfulness": {"user_score": 5, "judge_score": 5, "gap": 0, "verdict": "aligned", "feedback": "Test"},
    "Safety": {"user_score": null, "judge_score": 5, "gap": 0, "verdict": "not_applicable", "feedback": "Test"},
    "Bias": {"user_score": null, "judge_score": 5, "gap": 0, "verdict": "not_applicable", "feedback": "Test"},
    "Clarity": {"user_score": 3, "judge_score": 4, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"},
    "Consistency": {"user_score": 4, "judge_score": 4, "gap": 0, "verdict": "aligned", "feedback": "Test"},
    "Efficiency": {"user_score": 4, "judge_score": 5, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"},
    "Robustness": {"user_score": 2, "judge_score": 3, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"}
  },
  "judge_meta_score": 4,
  "overall_feedback": "Test feedback",
  "improvement_areas": [],
  "positive_feedback": []
}
```'''
        result = service.parse_stage2_response(response)

        assert result["judge_meta_score"] == 4
        assert "Truthfulness" in result["alignment_analysis"]

    def test_validate_stage2_response_missing_field(self):
        """Test validation catches missing required fields."""
        service = JudgeService()
        invalid_response = '{"alignment_analysis": {}, "judge_meta_score": 4}'

        with pytest.raises(ValueError, match="missing 'overall_feedback'"):
            service.parse_stage2_response(invalid_response)

    def test_validate_stage2_response_invalid_meta_score(self):
        """Test validation catches invalid meta score."""
        service = JudgeService()
        response = '''{
  "alignment_analysis": {
    "Truthfulness": {"user_score": 4, "judge_score": 3, "gap": 1, "verdict": "slightly_over_estimated", "feedback": "Test"},
    "Helpfulness": {"user_score": 5, "judge_score": 5, "gap": 0, "verdict": "aligned", "feedback": "Test"},
    "Safety": {"user_score": null, "judge_score": 5, "gap": 0, "verdict": "not_applicable", "feedback": "Test"},
    "Bias": {"user_score": null, "judge_score": 5, "gap": 0, "verdict": "not_applicable", "feedback": "Test"},
    "Clarity": {"user_score": 3, "judge_score": 4, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"},
    "Consistency": {"user_score": 4, "judge_score": 4, "gap": 0, "verdict": "aligned", "feedback": "Test"},
    "Efficiency": {"user_score": 4, "judge_score": 5, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"},
    "Robustness": {"user_score": 2, "judge_score": 3, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"}
  },
  "judge_meta_score": 6,
  "overall_feedback": "Test",
  "improvement_areas": [],
  "positive_feedback": []
}'''

        with pytest.raises(ValueError, match="judge_meta_score must be 1-5"):
            service.parse_stage2_response(response)

    def test_validate_stage2_response_invalid_verdict(self):
        """Test validation catches invalid verdict."""
        service = JudgeService()
        response = '''{
  "alignment_analysis": {
    "Truthfulness": {"user_score": 4, "judge_score": 3, "gap": 1, "verdict": "invalid_verdict", "feedback": "Test"},
    "Helpfulness": {"user_score": 5, "judge_score": 5, "gap": 0, "verdict": "aligned", "feedback": "Test"},
    "Safety": {"user_score": null, "judge_score": 5, "gap": 0, "verdict": "not_applicable", "feedback": "Test"},
    "Bias": {"user_score": null, "judge_score": 5, "gap": 0, "verdict": "not_applicable", "feedback": "Test"},
    "Clarity": {"user_score": 3, "judge_score": 4, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"},
    "Consistency": {"user_score": 4, "judge_score": 4, "gap": 0, "verdict": "aligned", "feedback": "Test"},
    "Efficiency": {"user_score": 4, "judge_score": 5, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"},
    "Robustness": {"user_score": 2, "judge_score": 3, "gap": 1, "verdict": "slightly_under_estimated", "feedback": "Test"}
  },
  "judge_meta_score": 4,
  "overall_feedback": "Test",
  "improvement_areas": [],
  "positive_feedback": []
}'''

        with pytest.raises(ValueError, match="invalid verdict"):
            service.parse_stage2_response(response)


class TestStage2MentoringComparison:
    """Test stage2_mentoring_comparison method (Task 4.7)."""

    @pytest.mark.live_api
    def test_stage2_full_flow(self, db_session):
        """Test complete Stage 2 flow with live GPT-4o API."""
        from datetime import datetime
        # Setup: Create test evaluation
        question = Question(
            id="q_stage2_test_001",
            question="What is the capital of Turkey?",
            category="Geography",
            difficulty="easy",
            reference_answer="Ankara",
            expected_behavior="Model should identify Ankara",
            rubric_breakdown={"1": "Wrong", "5": "Correct"},
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Helpfulness"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()

        model_response = ModelResponse(
            id="resp_stage2_test_001",
            question_id="q_stage2_test_001",
            model_name="openai/gpt-3.5-turbo",
            response_text="The capital of Turkey is Istanbul.",
            evaluated=False
        )
        db_session.add(model_response)
        db_session.flush()

        user_eval = UserEvaluation(
            id="eval_stage2_test_001",
            response_id="resp_stage2_test_001",
            evaluations={
                "Truthfulness": {"score": 3, "reasoning": "Wrong answer, should be Ankara"},
                "Helpfulness": {"score": 4, "reasoning": "Helpful but wrong"},
                "Safety": {"score": None, "reasoning": "N/A"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Clarity": {"score": 5, "reasoning": "Clear answer"},
                "Consistency": {"score": None, "reasoning": "N/A"},
                "Efficiency": {"score": 4, "reasoning": "Concise"},
                "Robustness": {"score": None, "reasoning": "N/A"}
            },
            judged=False
        )
        db_session.add(user_eval)
        db_session.commit()

        # First run Stage 1 to get independent scores
        service = JudgeService()
        stage1_result = service.stage1_independent_evaluation(
            "eval_stage2_test_001",
            db_session
        )

        # Now run Stage 2 with empty ChromaDB context
        stage2_result = service.stage2_mentoring_comparison(
            user_eval_id="eval_stage2_test_001",
            stage1_result=stage1_result,
            vector_context={"evaluations": []},
            db=db_session
        )

        # Verify Stage 2 result structure
        assert "alignment_analysis" in stage2_result
        assert "judge_meta_score" in stage2_result
        assert "overall_feedback" in stage2_result
        assert "improvement_areas" in stage2_result
        assert "positive_feedback" in stage2_result
        assert "primary_metric_gap" in stage2_result
        assert "weighted_gap" in stage2_result

        # Verify alignment_analysis has all 8 metrics
        for metric in THE_EIGHT_METRICS:
            assert metric in stage2_result["alignment_analysis"]
            metric_data = stage2_result["alignment_analysis"][metric]
            assert "user_score" in metric_data
            assert "judge_score" in metric_data
            assert "gap" in metric_data
            assert "verdict" in metric_data
            assert "feedback" in metric_data

        # Verify meta score is valid
        assert 1 <= stage2_result["judge_meta_score"] <= 5

        # Verify feedback arrays
        assert isinstance(stage2_result["improvement_areas"], list)
        assert isinstance(stage2_result["positive_feedback"], list)

        # Print for manual verification
        print(f"\n=== GPT-4o Stage 2 Evaluation ===")
        print(f"Meta Score: {stage2_result['judge_meta_score']}/5")
        print(f"Primary Gap: {stage2_result['primary_metric_gap']}")
        print(f"Weighted Gap: {stage2_result['weighted_gap']}")
        print(f"\nOverall Feedback:\n{stage2_result['overall_feedback']}")
        print(f"\nImprovement Areas:")
        for area in stage2_result['improvement_areas']:
            print(f"  - {area}")
        print(f"\nPositive Feedback:")
        for positive in stage2_result['positive_feedback']:
            print(f"  - {positive}")


class TestFullJudgeEvaluation:
    """Test full_judge_evaluation method (Task 4.8)."""

    @pytest.mark.live_api
    def test_full_judge_evaluation_end_to_end(self, db_session):
        """Test complete judge evaluation flow (Stage 1 → ChromaDB → Stage 2 → DB)."""
        from datetime import datetime
        from backend.models.judge_evaluation import JudgeEvaluation

        # Setup: Create test evaluation
        question = Question(
            id="q_full_test_001",
            question="What is 2+2?",
            category="Mathematics",
            difficulty="easy",
            reference_answer="4",
            expected_behavior="Model should answer correctly",
            rubric_breakdown={"1": "Wrong", "5": "Correct"},
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Helpfulness"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()

        model_response = ModelResponse(
            id="resp_full_test_001",
            question_id="q_full_test_001",
            model_name="openai/gpt-3.5-turbo",
            response_text="The answer is 5.",
            evaluated=False
        )
        db_session.add(model_response)
        db_session.flush()

        user_eval = UserEvaluation(
            id="eval_full_test_001",
            response_id="resp_full_test_001",
            evaluations={
                "Truthfulness": {"score": 2, "reasoning": "Wrong answer"},
                "Helpfulness": {"score": 3, "reasoning": "Brief but incorrect"},
                "Safety": {"score": None, "reasoning": "N/A"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Clarity": {"score": 5, "reasoning": "Clear"},
                "Consistency": {"score": None, "reasoning": "N/A"},
                "Efficiency": {"score": 4, "reasoning": "Concise"},
                "Robustness": {"score": None, "reasoning": "N/A"}
            },
            judged=False
        )
        db_session.add(user_eval)
        db_session.commit()

        # Execute full flow
        service = JudgeService()
        judge_eval_id = service.full_judge_evaluation(
            user_eval_id="eval_full_test_001",
            db=db_session
        )

        # Verify judge_eval_id format
        assert judge_eval_id.startswith("judge_")

        # Verify JudgeEvaluation record created
        judge_eval = db_session.query(JudgeEvaluation).filter_by(
            id=judge_eval_id
        ).first()
        assert judge_eval is not None
        assert judge_eval.user_evaluation_id == "eval_full_test_001"
        assert judge_eval.primary_metric == "Truthfulness"
        assert 1 <= judge_eval.judge_meta_score <= 5

        # Verify independent_scores present
        assert judge_eval.independent_scores is not None
        assert "Truthfulness" in judge_eval.independent_scores

        # Verify alignment_analysis present
        assert judge_eval.alignment_analysis is not None
        assert "Truthfulness" in judge_eval.alignment_analysis

        # Verify UserEvaluation.judged updated
        updated_user_eval = db_session.query(UserEvaluation).filter_by(
            id="eval_full_test_001"
        ).first()
        assert updated_user_eval.judged is True

        print(f"\n=== Full Judge Evaluation Test ===")
        print(f"Judge Evaluation ID: {judge_eval_id}")
        print(f"Meta Score: {judge_eval.judge_meta_score}/5")
        print(f"Primary Gap: {judge_eval.primary_metric_gap}")
        print(f"Weighted Gap: {judge_eval.weighted_gap}")
        print(f"Overall Feedback: {judge_eval.overall_feedback[:100]}...")

    def test_full_judge_evaluation_database_save(self, db_session):
        """Test that JudgeEvaluation record is saved correctly."""
        from datetime import datetime
        from backend.models.judge_evaluation import JudgeEvaluation
        from unittest.mock import Mock, patch

        # Setup: Create minimal test data
        question = Question(
            id="q_db_save_test_001",
            question="Test question?",
            category="Testing",
            difficulty="medium",
            reference_answer="Test answer",
            expected_behavior="Test behavior",
            rubric_breakdown={"1": "Bad", "5": "Good"},
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()

        model_response = ModelResponse(
            id="resp_db_save_test_001",
            question_id="q_db_save_test_001",
            model_name="openai/gpt-3.5-turbo",
            response_text="Test response",
            evaluated=False
        )
        db_session.add(model_response)
        db_session.flush()

        user_eval = UserEvaluation(
            id="eval_db_save_test_001",
            response_id="resp_db_save_test_001",
            evaluations={metric: {"score": 3, "reasoning": "Test"} for metric in THE_EIGHT_METRICS},
            judged=False
        )
        db_session.add(user_eval)
        db_session.commit()

        # Mock the Stage 1 and Stage 2 API calls to avoid live API
        service = JudgeService()

        mock_stage1_result = {
            "independent_scores": {
                metric: {"score": 3, "rationale": "Mock rationale"}
                for metric in THE_EIGHT_METRICS
            }
        }

        mock_stage2_result = {
            "alignment_analysis": {
                metric: {
                    "user_score": 3,
                    "judge_score": 3,
                    "gap": 0,
                    "verdict": "aligned",
                    "feedback": "Mock feedback"
                }
                for metric in THE_EIGHT_METRICS
            },
            "judge_meta_score": 5,
            "overall_feedback": "Mock overall feedback",
            "improvement_areas": ["Mock improvement"],
            "positive_feedback": ["Mock positive"],
            "primary_metric_gap": 0.0,
            "weighted_gap": 0.0
        }

        with patch.object(service, 'stage1_independent_evaluation', return_value=mock_stage1_result):
            with patch.object(service, 'stage2_mentoring_comparison', return_value=mock_stage2_result):
                with patch('backend.services.chromadb_service.chromadb_service') as mock_chroma:
                    # Mock ChromaDB query to return empty
                    mock_chroma.query_past_mistakes.return_value = {"evaluations": []}
                    # Mock ChromaDB add to succeed
                    mock_chroma.add_to_memory.return_value = None

                    judge_eval_id = service.full_judge_evaluation(
                        user_eval_id="eval_db_save_test_001",
                        db=db_session
                    )

        # Verify record created in database
        judge_eval = db_session.query(JudgeEvaluation).filter_by(id=judge_eval_id).first()
        assert judge_eval is not None
        assert judge_eval.judge_meta_score == 5
        assert judge_eval.primary_metric == "Truthfulness"

    def test_full_judge_evaluation_user_eval_update(self, db_session):
        """Test that UserEvaluation.judged is updated to TRUE."""
        from datetime import datetime
        from unittest.mock import patch

        # Setup: Create test data
        question = Question(
            id="q_user_update_test_001",
            question="Test?",
            category="Test",
            difficulty="medium",
            reference_answer="Answer",
            expected_behavior="Behavior",
            rubric_breakdown={"1": "Bad", "5": "Good"},
            primary_metric="Truthfulness",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(question)
        db_session.flush()

        model_response = ModelResponse(
            id="resp_user_update_test_001",
            question_id="q_user_update_test_001",
            model_name="openai/gpt-3.5-turbo",
            response_text="Response",
            evaluated=False
        )
        db_session.add(model_response)
        db_session.flush()

        user_eval = UserEvaluation(
            id="eval_user_update_test_001",
            response_id="resp_user_update_test_001",
            evaluations={metric: {"score": 3, "reasoning": "Test"} for metric in THE_EIGHT_METRICS},
            judged=False
        )
        db_session.add(user_eval)
        db_session.commit()

        # Mock API calls
        service = JudgeService()

        mock_stage1_result = {
            "independent_scores": {
                metric: {"score": 3, "rationale": "Mock"}
                for metric in THE_EIGHT_METRICS
            }
        }

        mock_stage2_result = {
            "alignment_analysis": {
                metric: {
                    "user_score": 3, "judge_score": 3, "gap": 0,
                    "verdict": "aligned", "feedback": "Mock"
                }
                for metric in THE_EIGHT_METRICS
            },
            "judge_meta_score": 5,
            "overall_feedback": "Mock",
            "improvement_areas": [],
            "positive_feedback": [],
            "primary_metric_gap": 0.0,
            "weighted_gap": 0.0
        }

        with patch.object(service, 'stage1_independent_evaluation', return_value=mock_stage1_result):
            with patch.object(service, 'stage2_mentoring_comparison', return_value=mock_stage2_result):
                with patch('backend.services.chromadb_service.chromadb_service') as mock_chroma:
                    mock_chroma.query_past_mistakes.return_value = {"evaluations": []}
                    mock_chroma.add_to_memory.return_value = None

                    service.full_judge_evaluation(
                        user_eval_id="eval_user_update_test_001",
                        db=db_session
                    )

        # Verify UserEvaluation.judged updated
        updated = db_session.query(UserEvaluation).filter_by(
            id="eval_user_update_test_001"
        ).first()
        assert updated.judged is True
