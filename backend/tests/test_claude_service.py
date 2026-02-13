"""
Unit tests for Claude Service - CANLI API TESTS

This module tests the Claude service with actual API calls (no mocks).
Tests are organized by:
- Category selection (unit, no API required)
- JSON parsing (unit, no API required)
- Service initialization (unit)
- Live API tests (integration, requires API key)
"""

import pytest
from backend.services.claude_service import (
    ClaudeService,
    select_category,
    DEFAULT_CATEGORY_POOL
)

# =====================================================
# Category Selection Tests (Unit, API gerektirmez)
# =====================================================


def test_select_category_any():
    """Test category selection with ['any'] hint"""
    result = select_category(["any"])
    assert result in DEFAULT_CATEGORY_POOL


def test_select_category_empty_list():
    """Test empty list falls back to pool"""
    result = select_category([])
    assert result in DEFAULT_CATEGORY_POOL


def test_select_category_specific():
    """Test category selection with specific hints"""
    hints = ["React", "Vue", "Angular"]
    result = select_category(hints)
    assert result in hints


def test_select_category_legacy_mapping():
    """Test legacy category mapping"""
    assert select_category(["Math"]) == "Mathematics"
    assert select_category(["Coding"]) == "Programming"
    assert select_category(["Medical"]) == "Medicine"


# =====================================================
# Service Initialization Tests
# =====================================================


def test_claude_service_initialization():
    """Test ClaudeService initializes with correct model"""
    service = ClaudeService()
    assert service.model == "claude-haiku-4-5-20251001"
    assert service.timeout == 30
    assert service.api_key is not None


def test_claude_service_api_client():
    """Test Anthropic client is initialized"""
    service = ClaudeService()
    assert service.client is not None
    assert hasattr(service.client, 'messages')


def test_claude_service_custom_timeout():
    """Test ClaudeService with custom timeout"""
    service = ClaudeService(timeout=60)
    assert service.timeout == 60


# =====================================================
# JSON Parsing Tests (Unit, API gerektirmez)
# =====================================================


def test_parse_claude_response_valid_json():
    """Test JSON parsing with valid JSON"""
    service = ClaudeService()
    content = '{"question": "test", "reference_answer": "ans", "expected_behavior": "exp", "rubric_breakdown": {"1": "bad", "2": "ok", "3": "good", "4": "great", "5": "excellent"}}'
    result = service._parse_claude_response(content)
    assert result["question"] == "test"
    assert "rubric_breakdown" in result


def test_parse_claude_response_markdown_json():
    """Test JSON extraction from markdown code block"""
    service = ClaudeService()
    content = '''```json
{
    "question": "test question",
    "reference_answer": "test answer",
    "expected_behavior": "test behavior",
    "rubric_breakdown": {
        "1": "bad",
        "2": "ok",
        "3": "good",
        "4": "great",
        "5": "excellent"
    }
}
```'''
    result = service._parse_claude_response(content)
    assert result["question"] == "test question"


def test_parse_claude_response_markdown_no_language():
    """Test JSON extraction from markdown code block without language"""
    service = ClaudeService()
    content = '''```
{
    "question": "test question",
    "reference_answer": "test answer",
    "expected_behavior": "test behavior",
    "rubric_breakdown": {
        "1": "bad",
        "2": "ok",
        "3": "good",
        "4": "great",
        "5": "excellent"
    }
}
```'''
    result = service._parse_claude_response(content)
    assert result["question"] == "test question"


def test_parse_claude_response_invalid_json():
    """Test parsing invalid JSON raises error"""
    service = ClaudeService()
    with pytest.raises(ValueError, match="Failed to parse"):
        service._parse_claude_response("not valid json")


def test_parse_json_static():
    """Test static _parse_json method"""
    result = ClaudeService._parse_json('{"key": "value"}')
    assert result == {"key": "value"}


def test_parse_json_static_invalid():
    """Test static _parse_json method with invalid JSON"""
    with pytest.raises(ValueError, match="Invalid JSON"):
        ClaudeService._parse_json("invalid json")


# =====================================================
# Pool Selection Tests (Database gerektirir)
# =====================================================


@pytest.mark.integration
def test_select_from_pool_empty_database(db_session):
    """Test that pool selection raises ValueError when database is empty"""
    service = ClaudeService()

    with pytest.raises(ValueError, match="No questions found"):
        service._select_from_pool("Truthfulness", db_session)


@pytest.mark.integration
def test_select_from_pool_with_existing_question(db_session):
    """Test pool selection with existing question in database"""
    from backend.models.question import Question

    # Create a test question using the fixture's session
    question = Question(
        id="q_test_pool_selection",
        question="Test question for pool selection",
        category="Mathematics",
        difficulty="medium",  # Added difficulty
        reference_answer="Test reference",
        expected_behavior="Test behavior",
        rubric_breakdown={"1": "bad", "2": "ok", "3": "good", "4": "great", "5": "excellent"},
        primary_metric="Truthfulness",
        bonus_metrics=["Clarity", "Safety"],
        question_prompt_id=None,
        times_used=0
    )
    db_session.add(question)
    db_session.commit()

    try:
        # Now test pool selection
        service = ClaudeService()
        selected = service._select_from_pool("Truthfulness", db_session)

        assert selected is not None
        assert selected.primary_metric == "Truthfulness"
        assert selected.times_used == 1  # Should be incremented
    finally:
        # Cleanup is handled by transaction rollback usually, 
        # but we explicitly delete to be safe if commit was used
        db_session.query(Question).filter(Question.id == "q_test_pool_selection").delete()
        db_session.commit()


# =====================================================
# CANLI API TEST - Gerçek Claude çağrısı
# =====================================================


@pytest.mark.integration
def test_generate_question_live_api():
    """
    CANLI API TEST: Gerçek Claude Haiku 4.5 ile soru üretir

    Not: Bu test gerçek API çağrısı yapar ve API key gerektirir.
    """
    service = ClaudeService()

    # Basit bir metric ile test
    question = service.generate_question(
        primary_metric="Truthfulness",
        use_pool=False  # Yeni soru üret (havuzdan değil)
    )

    # Doğrulamalar
    assert question.id is not None
    assert question.id.startswith("q_")
    assert question.question is not None
    assert len(question.question) > 0
    assert question.category is not None
    assert question.primary_metric == "Truthfulness"
    assert question.rubric_breakdown is not None

    # Rubric breakdown kontrolü (1-5 arası skorlar olmalı)
    rubric = question.rubric_breakdown
    for score in ["1", "2", "3", "4", "5"]:
        assert score in rubric, f"Rubric missing score {score}"

    print(f"\n Generated Question ID: {question.id}")
    print(f"   Category: {question.category}")
    print(f"   Question: {question.question[:100]}...")


@pytest.mark.integration
def test_generate_question_clarity_live_api():
    """
    CANLI API TEST: Clarity metric ile soru üretir
    """
    service = ClaudeService()

    question = service.generate_question(
        primary_metric="Clarity",
        use_pool=False
    )

    assert question.primary_metric == "Clarity"
    assert question.question is not None
    assert len(question.question) > 10
    assert "1" in question.rubric_breakdown
    assert "5" in question.rubric_breakdown

    print(f"\n Generated Clarity Question: {question.id}")


@pytest.mark.integration
def test_generate_question_safety_live_api():
    """
    CANLI API TEST: Safety metric ile soru üretir
    """
    service = ClaudeService()

    question = service.generate_question(
        primary_metric="Safety",
        use_pool=False
    )

    assert question.primary_metric == "Safety"
    assert question.question is not None
    assert question.reference_answer is not None

    print(f"\n Generated Safety Question: {question.id}")


# =====================================================
# Error Handling Tests
# =====================================================


@pytest.mark.integration
def test_generate_question_invalid_metric():
    """Test that invalid metric raises ValueError"""
    service = ClaudeService()

    with pytest.raises(ValueError, match="Invalid metric"):
        service.generate_question(
            primary_metric="InvalidMetric",
            use_pool=False
        )


def test_parse_claude_response_malformed_json():
    """Test parsing malformed JSON response"""
    service = ClaudeService()
    malformed = '{"question": "test", "reference_answer": "ans"'  # Missing closing brace

    with pytest.raises(ValueError):
        service._parse_claude_response(malformed)


def test_parse_claude_response_missing_fields():
    """Test parsing response with missing required fields"""
    service = ClaudeService()
    incomplete = '{"question": "test"}'  # Missing reference_answer, expected_behavior, rubric_breakdown

    # This should parse successfully but will fail validation in _generate_new_question
    result = service._parse_claude_response(incomplete)
    assert result["question"] == "test"


# =====================================================
# Category Pool Distribution Test
# =====================================================


def test_category_pool_diversity():
    """Test that DEFAULT_CATEGORY_POOL has expected diversity"""
    # Check that pool has at least 15 categories
    assert len(DEFAULT_CATEGORY_POOL) >= 15

    # Check for category domains
    academic_cats = ["Mathematics", "Physics", "Chemistry", "Biology", "History"]
    tech_cats = ["Programming", "Data Science", "Artificial Intelligence"]
    professional_cats = ["Business", "Finance", "Medicine", "Law"]
    arts_cats = ["Art", "Music", "Film", "Design"]

    for cat in academic_cats:
        assert cat in DEFAULT_CATEGORY_POOL
    for cat in tech_cats:
        assert cat in DEFAULT_CATEGORY_POOL
    for cat in professional_cats:
        assert cat in DEFAULT_CATEGORY_POOL
    for cat in arts_cats:
        assert cat in DEFAULT_CATEGORY_POOL


@pytest.mark.integration
def test_select_category_distribution():
    """
    Test that category selection follows expected distribution patterns
    over multiple selections (probabilistic test).
    """
    import collections

    n_selections = 100
    selections = []

    for _ in range(n_selections):
        result = select_category(["any"])
        selections.append(result)

    # Count selections
    counter = collections.Counter(selections)

    # Check that no single category dominates (>50%)
    max_count = max(counter.values())
    assert max_count < n_selections * 0.5, f"Category {max(counter, key=counter.get)} has {max_count}/{n_selections} selections"
