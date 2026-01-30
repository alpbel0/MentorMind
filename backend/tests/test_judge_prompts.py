"""
Tests for Judge Prompts

Tests the hardcoded judge prompt templates for GPT-4o's two-stage evaluation workflow.
"""

import pytest

from backend.prompts.judge_prompts import (
    JUDGE_PROMPTS,
    JUDGE_STAGE1_VERDICTS,
    META_SCORE_THRESHOLDS,
    WEIGHTED_GAP_WEIGHTS,
    render_stage1_prompt,
    render_stage2_prompt,
)


class TestJudgePromptsStructure:
    """Test that prompts have correct structure."""

    def test_prompts_has_both_stages(self):
        """Test that JUDGE_PROMPTS has both stage1 and stage2."""
        assert "stage1" in JUDGE_PROMPTS
        assert "stage2" in JUDGE_PROMPTS

    def test_stage1_has_required_keys(self):
        """Test that Stage 1 has all required keys."""
        stage1 = JUDGE_PROMPTS["stage1"]
        assert "system_prompt" in stage1
        assert "user_prompt_template" in stage1
        assert "render_function" in stage1

    def test_stage2_has_required_keys(self):
        """Test that Stage 2 has all required keys."""
        stage2 = JUDGE_PROMPTS["stage2"]
        assert "system_prompt" in stage2
        assert "user_prompt_template" in stage2
        assert "render_function" in stage2


class TestStage1Prompts:
    """Test Stage 1 (Independent Evaluation) prompts."""

    def test_stage1_system_prompt_exists(self):
        """Test that Stage 1 system prompt exists and is non-empty."""
        prompt = JUDGE_PROMPTS["stage1"]["system_prompt"]
        assert prompt
        assert len(prompt) > 0

    def test_stage1_system_prompt_length(self):
        """Test that Stage 1 system prompt is detailed enough (6+ paragraphs equivalent)."""
        prompt = JUDGE_PROMPTS["stage1"]["system_prompt"]
        # 6 paragraphs ~ 2000+ characters
        assert len(prompt) > 2000, f"Stage 1 system prompt too short: {len(prompt)} chars"

    def test_stage1_system_prompt_contains_key_sections(self):
        """Test that Stage 1 system prompt contains all required sections."""
        prompt = JUDGE_PROMPTS["stage1"]["system_prompt"]
        required_sections = [
            "Blind Evaluation Protocol",
            "8 Evaluation Metrics",
            "Truthfulness",
            "Helpfulness",
            "Safety",
            "Scoring Guidelines",
            "Output Format",
        ]
        for section in required_sections:
            assert section in prompt, f"Missing section: {section}"

    def test_stage1_template_has_all_placeholders(self):
        """Test that Stage 1 user template has all required placeholders."""
        template = JUDGE_PROMPTS["stage1"]["user_prompt_template"]
        required_placeholders = [
            "{question}",
            "{model_name}",
            "{model_response}",
            "{reference_answer}",
            "{expected_behavior}",
            "{primary_metric}",
            "{rubric_breakdown}",
        ]
        for placeholder in required_placeholders:
            assert placeholder in template, f"Missing placeholder: {placeholder}"

    def test_stage1_specifies_turkish_output(self):
        """Test that Stage 1 prompts specify Turkish language output."""
        sys_prompt = JUDGE_PROMPTS["stage1"]["system_prompt"]
        user_template = JUDGE_PROMPTS["stage1"]["user_prompt_template"]
        assert "Turkish" in sys_prompt or "Türkçe" in sys_prompt
        assert "Turkish" in user_template or "Türkçe" in user_template

    def test_stage1_specifies_json_output(self):
        """Test that Stage 1 prompts specify JSON output format."""
        sys_prompt = JUDGE_PROMPTS["stage1"]["system_prompt"]
        user_template = JUDGE_PROMPTS["stage1"]["user_prompt_template"]
        assert "JSON" in sys_prompt
        assert "JSON" in user_template

    def test_stage1_has_all_8_metrics_in_instructions(self):
        """Test that Stage 1 system prompt mentions all 8 metrics."""
        prompt = JUDGE_PROMPTS["stage1"]["system_prompt"]
        metrics = [
            "Truthfulness",
            "Helpfulness",
            "Safety",
            "Bias",
            "Clarity",
            "Consistency",
            "Efficiency",
            "Robustness",
        ]
        for metric in metrics:
            assert metric in prompt, f"Missing metric in instructions: {metric}"

    def test_stage1_has_few_shot_example(self):
        """Test that Stage 1 includes few-shot example."""
        template = JUDGE_PROMPTS["stage1"]["user_prompt_template"]
        assert "Example" in template or "example" in template
        assert "```json" in template or "```JSON" in template


class TestStage2Prompts:
    """Test Stage 2 (Mentoring Comparison) prompts."""

    def test_stage2_system_prompt_exists(self):
        """Test that Stage 2 system prompt exists and is non-empty."""
        prompt = JUDGE_PROMPTS["stage2"]["system_prompt"]
        assert prompt
        assert len(prompt) > 0

    def test_stage2_system_prompt_length(self):
        """Test that Stage 2 system prompt is detailed enough (6+ paragraphs equivalent)."""
        prompt = JUDGE_PROMPTS["stage2"]["system_prompt"]
        # 6 paragraphs ~ 2000+ characters
        assert len(prompt) > 2000, f"Stage 2 system prompt too short: {len(prompt)} chars"

    def test_stage2_system_prompt_contains_key_sections(self):
        """Test that Stage 2 system prompt contains all required sections."""
        prompt = JUDGE_PROMPTS["stage2"]["system_prompt"]
        required_sections = [
            "Comparison Methodology",
            "Verdict Categories",
            "Meta Score Calculation",
            "Feedback Construction",
            "Output Format",
        ]
        for section in required_sections:
            assert section in prompt, f"Missing section: {section}"

    def test_stage2_template_has_all_placeholders(self):
        """Test that Stage 2 user template has all required placeholders."""
        template = JUDGE_PROMPTS["stage2"]["user_prompt_template"]
        required_placeholders = [
            "{user_scores}",
            "{judge_scores}",
            "{comparison_table}",
            "{primary_metric}",
            "{bonus_metrics}",
            "{past_mistakes}",
        ]
        for placeholder in required_placeholders:
            assert placeholder in template, f"Missing placeholder: {placeholder}"

    def test_stage2_specifies_turkish_output(self):
        """Test that Stage 2 prompts specify Turkish language output."""
        sys_prompt = JUDGE_PROMPTS["stage2"]["system_prompt"]
        user_template = JUDGE_PROMPTS["stage2"]["user_prompt_template"]
        assert "Turkish" in sys_prompt or "Türkçe" in sys_prompt
        assert "Turkish" in user_template or "Türkçe" in user_template

    def test_stage2_specifies_json_output(self):
        """Test that Stage 2 prompts specify JSON output format."""
        sys_prompt = JUDGE_PROMPTS["stage2"]["system_prompt"]
        user_template = JUDGE_PROMPTS["stage2"]["user_prompt_template"]
        assert "JSON" in sys_prompt
        assert "JSON" in user_template

    def test_stage2_has_verdict_categories(self):
        """Test that Stage 2 defines verdict categories."""
        prompt = JUDGE_PROMPTS["stage2"]["system_prompt"]
        verdicts = [
            "aligned",
            "slightly_over_estimated",
            "slightly_under_estimated",
            "moderately_over_estimated",
            "moderately_under_estimated",
            "significantly_over_estimated",
            "significantly_under_estimated",
            "not_applicable",
        ]
        for verdict in verdicts:
            assert verdict in prompt, f"Missing verdict: {verdict}"

    def test_stage2_has_meta_score_calculation(self):
        """Test that Stage 2 explains meta score calculation."""
        prompt = JUDGE_PROMPTS["stage2"]["system_prompt"]
        assert "meta_score" in prompt or "meta score" in prompt
        assert "weighted_gap" in prompt or "weighted gap" in prompt
        assert "primary" in prompt.lower()
        assert "bonus" in prompt.lower()

    def test_stage2_has_few_shot_example(self):
        """Test that Stage 2 includes few-shot example."""
        template = JUDGE_PROMPTS["stage2"]["user_prompt_template"]
        assert "Example" in template or "example" in template
        assert "```json" in template or "```JSON" in template


class TestRenderFunctions:
    """Test prompt rendering functions."""

    def test_render_stage1_prompt_basic(self):
        """Test basic Stage 1 prompt rendering."""
        rendered = render_stage1_prompt(
            question="What is 2+2?",
            model_name="gpt-3.5-turbo",
            model_response="The answer is 4.",
            reference_answer="4",
            expected_behavior="Answer correctly",
            primary_metric="Truthfulness",
            rubric_breakdown={"1": "Wrong", "5": "Correct"},
        )
        assert "What is 2+2?" in rendered
        assert "gpt-3.5-turbo" in rendered
        assert "The answer is 4." in rendered
        assert "Truthfulness" in rendered

    def test_render_stage1_prompt_with_list_rubric(self):
        """Test Stage 1 rendering with list rubric."""
        rendered = render_stage1_prompt(
            question="Test question",
            model_name="gpt-4o-mini",
            model_response="Test response",
            reference_answer="Test reference",
            expected_behavior="Test behavior",
            primary_metric="Clarity",
            rubric_breakdown=["Wrong", "Poor", "Okay", "Good", "Excellent"],
        )
        assert "Wrong" in rendered
        assert "Excellent" in rendered

    def test_render_stage1_prompt_with_nullable_fields(self):
        """Test Stage 1 rendering with nullable reference/expected."""
        rendered = render_stage1_prompt(
            question="Test question",
            model_name="gpt-3.5-turbo",
            model_response="Test response",
            reference_answer="",
            expected_behavior="",
            primary_metric="Safety",
            rubric_breakdown={"1": "Harmful", "5": "Safe"},
        )
        assert "N/A" in rendered

    def test_render_stage2_prompt_basic(self):
        """Test basic Stage 2 prompt rendering."""
        user_scores = {
            "Truthfulness": {"score": 4, "reasoning": "Looks correct to me"},
            "Helpfulness": {"score": 5, "reasoning": "Very helpful"},
        }
        judge_scores = {
            "Truthfulness": {"score": 3, "rationale": "Has a small error"},
            "Helpfulness": {"score": 5, "rationale": "Excellent guidance"},
        }
        comparison_table = """
| Metric | User | Judge | Gap | Verdict |
|--------|------|-------|-----|---------|
| Truthfulness | 4 | 3 | 1 | slightly_over_estimated |
| Helpfulness | 5 | 5 | 0 | aligned |
""".strip()

        rendered = render_stage2_prompt(
            user_scores=user_scores,
            judge_scores=judge_scores,
            comparison_table=comparison_table,
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity", "Safety"],
            past_mistakes="User often overestimates Truthfulness",
        )

        assert "Truthfulness" in rendered
        assert "Clarity, Safety" in rendered
        assert "slightly_over_estimated" in rendered
        assert "User often overestimates" in rendered

    def test_render_stage2_prompt_empty_bonus_metrics(self):
        """Test Stage 2 rendering with empty bonus metrics."""
        rendered = render_stage2_prompt(
            user_scores={},
            judge_scores={},
            comparison_table="",
            primary_metric="Safety",
            bonus_metrics=[],
            past_mistakes="",
        )
        assert "None" in rendered

    def test_render_stage2_prompt_empty_past_mistakes(self):
        """Test Stage 2 rendering with empty past mistakes."""
        rendered = render_stage2_prompt(
            user_scores={},
            judge_scores={},
            comparison_table="",
            primary_metric="Bias",
            bonus_metrics=["Truthfulness"],
            past_mistakes="",
        )
        assert "No similar past evaluations found" in rendered


class TestConstants:
    """Test exported constants."""

    def test_judge_stage1_verdicts(self):
        """Test JUDGE_STAGE1_VERDICTS constant."""
        assert isinstance(JUDGE_STAGE1_VERDICTS, list)
        assert len(JUDGE_STAGE1_VERDICTS) == 8
        assert "aligned" in JUDGE_STAGE1_VERDICTS
        assert "not_applicable" in JUDGE_STAGE1_VERDICTS

    def test_meta_score_thresholds(self):
        """Test META_SCORE_THRESHOLDS constant."""
        assert isinstance(META_SCORE_THRESHOLDS, dict)
        assert 5 in META_SCORE_THRESHOLDS
        assert 4 in META_SCORE_THRESHOLDS
        assert 3 in META_SCORE_THRESHOLDS
        assert 2 in META_SCORE_THRESHOLDS
        assert META_SCORE_THRESHOLDS[5] == 0.5
        assert META_SCORE_THRESHOLDS[4] == 1.0
        assert META_SCORE_THRESHOLDS[3] == 1.5
        assert META_SCORE_THRESHOLDS[2] == 2.0

    def test_weighted_gap_weights(self):
        """Test WEIGHTED_GAP_WEIGHTS constant."""
        assert isinstance(WEIGHTED_GAP_WEIGHTS, dict)
        assert "primary" in WEIGHTED_GAP_WEIGHTS
        assert "bonus" in WEIGHTED_GAP_WEIGHTS
        assert "other" in WEIGHTED_GAP_WEIGHTS
        assert WEIGHTED_GAP_WEIGHTS["primary"] == 0.7
        assert WEIGHTED_GAP_WEIGHTS["bonus"] == 0.2
        assert WEIGHTED_GAP_WEIGHTS["other"] == 0.1
        # Sum should be 1.0
        assert sum(WEIGHTED_GAP_WEIGHTS.values()) == pytest.approx(1.0)
