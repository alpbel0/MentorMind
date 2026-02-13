"""
Test Coach Prompts - Coach Prompt Design Validation

Tests for coach prompt templates, helper functions, and rendering.
Reference: Task 14.1 - Coach Prompt Design
"""

import pytest

from backend.prompts.coach_prompts import (
    COACH_PROMPTS,
    COACH_SYSTEM_PROMPT,
    COACH_INIT_GREETING_TEMPLATE,
    COACH_USER_PROMPT_TEMPLATE,
    COACH_MAX_HISTORY_WINDOW,
    COACH_MAX_SELECTED_METRICS,
    render_coach_init_greeting,
    render_coach_user_prompt,
    format_evidence_display,
    format_gaps_summary,
    format_scores_display,
    format_chat_history,
)


# =====================================================
# Test Constants
# =====================================================

class TestCoachPromptConstants:
    """Test coach prompt constants."""

    def test_coach_prompts_export_exists(self):
        """COACH_PROMPTS export dictionary should exist."""
        assert isinstance(COACH_PROMPTS, dict)
        assert "system_prompt" in COACH_PROMPTS
        assert "user_prompt_template" in COACH_PROMPTS
        assert "init_greeting_template" in COACH_PROMPTS
        assert "render_user_prompt" in COACH_PROMPTS
        assert "render_init_greeting" in COACH_PROMPTS

    def test_max_history_window(self):
        """History window should match AD-4 setting."""
        assert COACH_MAX_HISTORY_WINDOW == 6

    def test_max_selected_metrics(self):
        """Max selected metrics should be 3."""
        assert COACH_MAX_SELECTED_METRICS == 3

    def test_system_prompt_not_empty(self):
        """System prompt should not be empty."""
        assert len(COACH_SYSTEM_PROMPT) > 1000


# =====================================================
# Test Helper Functions
# =====================================================

class TestFormatEvidenceDisplay:
    """Test format_evidence_display helper."""

    def test_empty_evidence(self):
        """Empty evidence should return 'Kanıt yok.'"""
        result = format_evidence_display(None, ["truthfulness"])
        assert result == "Kanıt yok."

    def test_evidence_with_selected_metric(self):
        """Evidence for selected metric should be formatted."""
        evidence = {
            "truthfulness": [
                {
                    "quote": "Test quote text here",
                    "start": 0,
                    "end": 20,
                    "why": "Test why",
                    "better": "Test better"
                }
            ]
        }
        result = format_evidence_display(evidence, ["truthfulness"])
        assert "Truthfulness" in result
        assert "Test quote text here" in result

    def test_evidence_ignores_non_selected_metrics(self):
        """Evidence for non-selected metrics should be ignored."""
        evidence = {
            "truthfulness": [{"quote": "T", "start": 0, "end": 1, "why": "W", "better": "B"}],
            "clarity": [{"quote": "C", "start": 0, "end": 1, "why": "W", "better": "B"}]
        }
        result = format_evidence_display(evidence, ["truthfulness"])
        assert "Truthfulness" in result
        # Clarity should NOT be in result (not selected)
        lines = result.split("\n")
        clarity_lines = [l for l in lines if "Clarity" in l]
        assert len(clarity_lines) == 0


class TestFormatGapsSummary:
    """Test format_gaps_summary helper."""

    def test_gap_zero_perfect_alignment(self):
        """Gap of 0 should show 'mükemmel uyum'."""
        user_scores = {"truthfulness": {"score": 4}}
        judge_scores = {"truthfulness": {"score": 4}}
        result = format_gaps_summary(user_scores, judge_scores, ["truthfulness"])
        assert "mükemmel uyum" in result

    def test_gap_one_minor_difference(self):
        """Gap of 1 should show 'küçük fark'."""
        user_scores = {"truthfulness": {"score": 4}}
        judge_scores = {"truthfulness": {"score": 3}}
        result = format_gaps_summary(user_scores, judge_scores, ["truthfulness"])
        assert "küçük fark" in result
        assert "(1 puan)" in result

    def test_gap_two_moderate_difference(self):
        """Gap of 2 should show 'orta fark'."""
        user_scores = {"truthfulness": {"score": 5}}
        judge_scores = {"truthfulness": {"score": 3}}
        result = format_gaps_summary(user_scores, judge_scores, ["truthfulness"])
        assert "orta fark" in result
        assert "(2 puan)" in result

    def test_gap_three_major_difference(self):
        """Gap of 3+ should show 'büyük fark'."""
        user_scores = {"truthfulness": {"score": 5}}
        judge_scores = {"truthfulness": {"score": 1}}
        result = format_gaps_summary(user_scores, judge_scores, ["truthfulness"])
        assert "büyük fark" in result
        assert "(4 puan)" in result

    def test_null_score_no_comparison(self):
        """Null scores should show 'karşılaştırılamaz'."""
        user_scores = {"truthfulness": {"score": None}}
        judge_scores = {"truthfulness": {"score": 3}}
        result = format_gaps_summary(user_scores, judge_scores, ["truthfulness"])
        assert "karşılaştırılamaz" in result

    def test_ignores_non_selected_metrics(self):
        """Should only include selected metrics."""
        user_scores = {
            "truthfulness": {"score": 4},
            "clarity": {"score": 3}
        }
        judge_scores = {
            "truthfulness": {"score": 3},
            "clarity": {"score": 4}
        }
        result = format_gaps_summary(user_scores, judge_scores, ["truthfulness"])
        assert "Truthfulness" in result
        assert "Clarity" not in result


class TestFormatScoresDisplay:
    """Test format_scores_display helper."""

    def test_empty_scores(self):
        """Empty scores should return placeholder."""
        result = format_scores_display({}, ["truthfulness"])
        assert "Puan yok" in result or "Puan bilgisi yok" in result

    def test_score_with_reasoning(self):
        """Score with reasoning should be formatted."""
        scores = {
            "truthfulness": {
                "score": 4,
                "reasoning": "Bu bir test gerekçesi"
            }
        }
        result = format_scores_display(scores, ["truthfulness"])
        assert "Truthfulness" in result
        assert "4/5" in result
        assert "Bu bir test gerekçesi" in result

    def test_score_with_rationale(self):
        """Score with rationale (judge format) should be formatted."""
        scores = {
            "truthfulness": {
                "score": 3,
                "rationale": "Judge gerekçesi"
            }
        }
        result = format_scores_display(scores, ["truthfulness"])
        assert "Truthfulness" in result
        assert "3/5" in result
        assert "Judge gerekçesi" in result

    def test_long_reasoning_truncated(self):
        """Long reasoning should be truncated to 60 chars."""
        scores = {
            "truthfulness": {
                "score": 4,
                "reasoning": "a" * 100  # 100 chars
            }
        }
        result = format_scores_display(scores, ["truthfulness"])
        assert "..." in result  # Truncation marker
        # Check that result is shorter than original
        assert len(result.split(" - ")[-1]) < 70

    def test_null_score_shows_na(self):
        """Null score should show N/A."""
        scores = {
            "truthfulness": {
                "score": None,
                "reasoning": "Not applicable"
            }
        }
        result = format_scores_display(scores, ["truthfulness"])
        assert "N/A" in result


class TestFormatChatHistory:
    """Test format_chat_history helper."""

    def test_empty_history(self):
        """Empty history should return placeholder."""
        result = format_chat_history([])
        assert "yok" in result.lower()

    def test_user_message_formatted(self):
        """User messages should be formatted correctly."""
        history = [
            {"role": "user", "content": "Test user message"}
        ]
        result = format_chat_history(history)
        assert "Kullanıcı:" in result
        assert "Test user message" in result

    def test_assistant_message_formatted(self):
        """Assistant (Coach) messages should be formatted correctly."""
        history = [
            {"role": "assistant", "content": "Test coach response"}
        ]
        result = format_chat_history(history)
        assert "Coach:" in result
        assert "Test coach response" in result

    def test_long_message_truncated(self):
        """Long messages should be truncated to 200 chars."""
        history = [
            {"role": "user", "content": "a" * 300}
        ]
        result = format_chat_history(history)
        # Result should be shorter than original
        assert len(result) < 250

    def test_mixed_history(self):
        """Mixed user/assistant history should be formatted."""
        history = [
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Coach response"},
            {"role": "user", "content": "Follow-up"}
        ]
        result = format_chat_history(history)
        assert "Kullanıcı:" in result
        assert "Coach:" in result
        assert "User message" in result
        assert "Coach response" in result
        assert "Follow-up" in result


# =====================================================
# Test Render Functions
# =====================================================

class TestRenderCoachInitGreeting:
    """Test render_coach_init_greeting function."""

    def test_basic_render(self):
        """Should render greeting with all context."""
        user_scores = {"truthfulness": {"score": 4, "reasoning": "Test"}}
        judge_scores = {"truthfulness": {"score": 3, "rationale": "Test"}}
        evidence = {
            "truthfulness": [
                {"quote": "Test", "start": 0, "end": 4, "why": "Why", "better": "Better"}
            ]
        }

        result = render_coach_init_greeting(
            question="Test question?",
            model_answer="Test answer.",
            user_scores=user_scores,
            judge_scores=judge_scores,
            evidence_json=evidence,
            selected_metrics=["truthfulness"]
        )

        assert "değerlendirmeyi birlikte inceleyelim" in result
        assert "Truthfulness" in result
        assert len(result) > 50

    def test_no_evidence(self):
        """Should handle missing evidence gracefully."""
        user_scores = {"truthfulness": {"score": 4, "reasoning": "Test"}}
        judge_scores = {"truthfulness": {"score": 3, "rationale": "Test"}}

        result = render_coach_init_greeting(
            question="Test question?",
            model_answer="Test answer.",
            user_scores=user_scores,
            judge_scores=judge_scores,
            evidence_json=None,
            selected_metrics=["truthfulness"]
        )

        assert "kanıt yok" in result.lower()

    def test_multiple_selected_metrics(self):
        """Should include all selected metrics."""
        user_scores = {
            "truthfulness": {"score": 4, "reasoning": "Test"},
            "clarity": {"score": 3, "reasoning": "Test"}
        }
        judge_scores = {
            "truthfulness": {"score": 3, "rationale": "Test"},
            "clarity": {"score": 4, "rationale": "Test"}
        }

        result = render_coach_init_greeting(
            question="Test question?",
            model_answer="Test answer.",
            user_scores=user_scores,
            judge_scores=judge_scores,
            evidence_json=None,
            selected_metrics=["truthfulness", "clarity"]
        )

        assert "Truthfulness" in result
        assert "Clarity" in result


class TestRenderCoachUserPrompt:
    """Test render_coach_user_prompt function."""

    def test_basic_render(self):
        """Should render user prompt with all context."""
        user_scores = {"truthfulness": {"score": 4, "reasoning": "Test"}}
        judge_scores = {"truthfulness": {"score": 3, "rationale": "Test"}}
        evidence = {
            "truthfulness": [
                {"quote": "Test", "start": 0, "end": 4, "why": "Why", "better": "Better"}
            ]
        }

        result = render_coach_user_prompt(
            question="Test question?",
            model_answer="Test answer.",
            user_scores=user_scores,
            judge_scores=judge_scores,
            evidence_json=evidence,
            chat_history=[],
            user_message="Why is there a gap?",
            selected_metrics=["truthfulness"]
        )

        assert "Test question?" in result
        assert "Test answer." in result
        assert "Why is there a gap?" in result
        assert "Truthfulness" in result
        assert "SADECE" in result  # Constraint reminder

    def test_with_chat_history(self):
        """Should include chat history in prompt."""
        user_scores = {"truthfulness": {"score": 4, "reasoning": "Test"}}
        judge_scores = {"truthfulness": {"score": 3, "rationale": "Test"}}
        history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First response"}
        ]

        result = render_coach_user_prompt(
            question="Test question?",
            model_answer="Test answer.",
            user_scores=user_scores,
            judge_scores=judge_scores,
            evidence_json=None,
            chat_history=history,
            user_message="Follow-up",
            selected_metrics=["truthfulness"]
        )

        assert "First question" in result
        assert "First response" in result
        assert "Sohbet Geçmişi" in result

    def test_custom_history_window(self):
        """Should respect custom history window."""
        long_history = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(10)
        ]

        # Default window (6)
        result_default = render_coach_user_prompt(
            question="Test?",
            model_answer="Test.",
            user_scores={"truthfulness": {"score": 4, "reasoning": "T"}},
            judge_scores={"truthfulness": {"score": 3, "rationale": "T"}},
            evidence_json=None,
            chat_history=long_history,
            user_message="Latest",
            selected_metrics=["truthfulness"]
        )

        # Custom window (3)
        result_custom = render_coach_user_prompt(
            question="Test?",
            model_answer="Test.",
            user_scores={"truthfulness": {"score": 4, "reasoning": "T"}},
            judge_scores={"truthfulness": {"score": 3, "rationale": "T"}},
            evidence_json=None,
            chat_history=long_history,
            user_message="Latest",
            selected_metrics=["truthfulness"],
            history_window=3
        )

        # Custom should have fewer messages included
        assert len(result_custom) < len(result_default)

    def test_no_evidence(self):
        """Should handle missing evidence gracefully."""
        user_scores = {"truthfulness": {"score": 4, "reasoning": "Test"}}
        judge_scores = {"truthfulness": {"score": 3, "rationale": "Test"}}

        result = render_coach_user_prompt(
            question="Test question?",
            model_answer="Test answer.",
            user_scores=user_scores,
            judge_scores=judge_scores,
            evidence_json=None,
            chat_history=[],
            user_message="Why?",
            selected_metrics=["truthfulness"]
        )

        # Should still render successfully
        assert "Test question?" in result
        assert "Why?" in result
