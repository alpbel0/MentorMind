"""
Tests for ChromaDB Memory Operations (Tasks 4.2 & 4.3)

Tests add_to_memory() and query_past_mistakes() with inline test data.
No dependency on judge_task - creates test data directly in tests.
"""

import pytest
from datetime import datetime

from backend.models.database import SessionLocal
from backend.models.question import Question
from backend.models.model_response import ModelResponse
from backend.models.user_evaluation import UserEvaluation
from backend.models.judge_evaluation import JudgeEvaluation
from backend.services.chromadb_service import chromadb_service


class TestChromaDBTasks:
    """Test ChromaDB memory operations with real ChromaDB instance."""

    def setup_method(self):
        """Set up test database session."""
        self.db = SessionLocal()

    def teardown_method(self):
        """Clean up test data."""
        # Clean up ChromaDB test documents
        try:
            collection = chromadb_service.get_collection()
            test_ids = [
                "test_add_to_memory_eval",
                "test_query_eval_1",
                "test_query_eval_2",
                "test_query_eval_3"
            ]
            collection.delete(ids=test_ids)
        except Exception:
            pass

        self.db.close()

    # =====================================================
    # Task 4.2: add_to_memory() Tests
    # =====================================================

    def test_add_to_memory_creates_document(self):
        """Test add_to_memory creates a document in ChromaDB."""
        # First check if test data already exists (from previous failed run)
        existing = self.db.query(JudgeEvaluation).filter_by(id="test_judge_add_memory").first()
        if existing:
            self.db.query(JudgeEvaluation).filter_by(id="test_judge_add_memory").delete()
            self.db.query(UserEvaluation).filter_by(id="test_add_to_memory_eval").delete()
            self.db.query(ModelResponse).filter_by(id="test_resp_add_memory").delete()
            self.db.query(Question).filter_by(id="test_q_add_memory").delete()
            self.db.commit()

        # Create inline test data in correct order (respecting FKs)
        # 1. Question first (no dependencies)
        question = Question(
            id="test_q_add_memory",
            question="What is 2 + 2?",
            category="Math",
            difficulty="easy",
            reference_answer="4",
            expected_behavior="Model should answer correctly",
            rubric_breakdown={"1": "Wrong", "5": "Correct"},
            primary_metric="Truthfulness",
            bonus_metrics=["Clarity"]
        )
        self.db.add(question)
        self.db.flush()  # Flush to get the ID assigned

        # 2. ModelResponse (depends on question)
        model_response = ModelResponse(
            id="test_resp_add_memory",
            question_id="test_q_add_memory",
            model_name="openai/gpt-3.5-turbo",
            response_text="The answer is 5."
        )
        self.db.add(model_response)
        self.db.flush()

        # 3. UserEvaluation (depends on model_response)
        user_eval = UserEvaluation(
            id="test_add_to_memory_eval",
            response_id="test_resp_add_memory",
            evaluations={
                "Truthfulness": {"score": 2, "reasoning": "Wrong answer"},
                "Clarity": {"score": 5, "reasoning": "Clear but wrong"},
                "Helpfulness": {"score": None, "reasoning": "N/A"},
                "Safety": {"score": None, "reasoning": "N/A"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Consistency": {"score": None, "reasoning": "N/A"},
                "Efficiency": {"score": 5, "reasoning": "Concise"},
                "Robustness": {"score": None, "reasoning": "N/A"}
            },
            judged=False
        )
        self.db.add(user_eval)
        self.db.flush()

        # 4. JudgeEvaluation (depends on user_evaluation)
        judge_eval = JudgeEvaluation(
            id="test_judge_add_memory",
            user_evaluation_id="test_add_to_memory_eval",
            independent_scores={
                "Truthfulness": {"score": 1, "rationale": "Factually incorrect"},
                "Clarity": {"score": 5, "rationale": "Clear answer"},
                "Helpfulness": {"score": 2, "rationale": "Misleading"},
                "Safety": {"score": 5, "rationale": "Safe"},
                "Bias": {"score": 5, "rationale": "No bias"},
                "Consistency": {"score": 5, "rationale": "Consistent"},
                "Efficiency": {"score": 5, "rationale": "Efficient"},
                "Robustness": {"score": 3, "rationale": "Failed edge case"}
            },
            alignment_analysis={
                "Truthfulness": {
                    "user_score": 2,
                    "judge_score": 1,
                    "gap": 1,
                    "verdict": "under_estimated",
                    "feedback": "Answer is factually wrong"
                }
            },
            judge_meta_score=3,
            overall_feedback="You under-detected the factual error. The answer is clearly wrong.",
            improvement_areas=["Detect factual errors"],
            positive_feedback=["Good clarity assessment"],
            primary_metric="Truthfulness",
            primary_metric_gap=1.0,
            weighted_gap=1.0
        )
        self.db.add(judge_eval)
        self.db.commit()

        # Test add_to_memory
        try:
            chromadb_service.add_to_memory(
                self.db,
                "test_add_to_memory_eval",
                "test_judge_add_memory"
            )

            # Verify document was added
            collection = chromadb_service.get_collection()
            results = collection.get(ids=["test_add_to_memory_eval"])

            assert results is not None
            assert len(results['ids']) == 1
            assert results['ids'][0] == "test_add_to_memory_eval"
            assert len(results['documents']) == 1
            assert "Truthfulness" in results['documents'][0]
            assert "Math" in results['documents'][0]

            # Verify metadata
            metadata = results['metadatas'][0]
            assert metadata['category'] == "Math"
            assert metadata['primary_metric'] == "Truthfulness"
            assert metadata['judge_meta_score'] == 3
            assert metadata['primary_metric_gap'] == 1.0

        finally:
            # Clean up database
            self.db.rollback()
            self.db.query(JudgeEvaluation).filter_by(id="test_judge_add_memory").delete()
            self.db.query(UserEvaluation).filter_by(id="test_add_to_memory_eval").delete()
            self.db.query(ModelResponse).filter_by(id="test_resp_add_memory").delete()
            self.db.query(Question).filter_by(id="test_q_add_memory").delete()
            self.db.commit()

    def test_add_to_memory_missing_user_eval(self):
        """Test add_to_memory raises ValueError for missing user evaluation."""
        with pytest.raises(ValueError, match="User evaluation.*not found"):
            chromadb_service.add_to_memory(self.db, "nonexistent_eval", "judge_123")

    def test_add_to_memory_missing_judge_eval(self):
        """Test add_to_memory raises ValueError for missing judge evaluation."""
        # Clean up any existing test data first
        self.db.query(UserEvaluation).filter_by(id="test_eval_missing_judge").delete()
        self.db.query(ModelResponse).filter_by(id="test_resp_missing_judge").delete()
        self.db.query(Question).filter_by(id="test_q_missing_judge").delete()
        self.db.commit()

        # Create user eval only
        question = Question(
            id="test_q_missing_judge",
            question="Test?",
            category="General",
            difficulty="easy",
            rubric_breakdown={"1": "Bad", "5": "Good"},
            primary_metric="Clarity",
            bonus_metrics=[]
        )
        self.db.add(question)
        self.db.flush()

        model_response = ModelResponse(
            id="test_resp_missing_judge",
            question_id="test_q_missing_judge",
            model_name="openai/gpt-3.5-turbo",
            response_text="Test response"
        )
        self.db.add(model_response)
        self.db.flush()

        user_eval = UserEvaluation(
            id="test_eval_missing_judge",
            response_id="test_resp_missing_judge",
            evaluations={
                "Truthfulness": {"score": 5, "reasoning": "Good"},
                "Helpfulness": {"score": None, "reasoning": "N/A"},
                "Safety": {"score": None, "reasoning": "N/A"},
                "Bias": {"score": None, "reasoning": "N/A"},
                "Clarity": {"score": 5, "reasoning": "Clear"},
                "Consistency": {"score": None, "reasoning": "N/A"},
                "Efficiency": {"score": None, "reasoning": "N/A"},
                "Robustness": {"score": None, "reasoning": "N/A"}
            },
            judged=False
        )
        self.db.add(user_eval)
        self.db.commit()

        try:
            with pytest.raises(ValueError, match="Judge evaluation.*not found"):
                chromadb_service.add_to_memory(
                    self.db,
                    "test_eval_missing_judge",
                    "nonexistent_judge"
                )
        finally:
            # Clean up
            self.db.rollback()
            self.db.query(UserEvaluation).filter_by(id="test_eval_missing_judge").delete()
            self.db.query(ModelResponse).filter_by(id="test_resp_missing_judge").delete()
            self.db.query(Question).filter_by(id="test_q_missing_judge").delete()
            self.db.commit()

    # =====================================================
    # Task 4.3: query_past_mistakes() Tests
    # =====================================================

    def test_query_past_mistakes_empty_results(self):
        """Test query_past_mistakes returns empty list when no matches."""
        result = chromadb_service.query_past_mistakes(
            "NonExistentMetric",
            "NonExistentCategory",
            n=5
        )

        assert result is not None
        assert "evaluations" in result
        assert result["evaluations"] == []

    def test_query_past_mistakes_with_data(self):
        """Test query_past_mistakes returns matching evaluations."""
        # Add test data to ChromaDB directly (faster than full DB setup)
        collection = chromadb_service.get_collection()

        test_evaluations = [
            {
                "id": "test_query_eval_1",
                "metric": "Truthfulness",
                "category": "Math",
                "meta_score": 3,
                "gap": 1.2
            },
            {
                "id": "test_query_eval_2",
                "metric": "Truthfulness",
                "category": "Math",
                "meta_score": 4,
                "gap": 0.5
            },
            {
                "id": "test_query_eval_3",
                "metric": "Clarity",  # Different metric
                "category": "Math",
                "meta_score": 5,
                "gap": 0.0
            }
        ]

        for eval_data in test_evaluations:
            collection.add(
                ids=[eval_data["id"]],
                documents=[
                    f"User evaluating {eval_data['metric']} in {eval_data['category']} category. "
                    f"Meta score: {eval_data['meta_score']}/5. Primary gap: {eval_data['gap']}. "
                    f"Feedback: Test feedback for {eval_data['id']}."
                ],
                metadatas=[{
                    "evaluation_id": eval_data["id"],
                    "category": eval_data["category"],
                    "primary_metric": eval_data["metric"],
                    "judge_meta_score": eval_data["meta_score"],
                    "primary_metric_gap": eval_data["gap"],
                    "weighted_gap": eval_data["gap"],
                    "mistake_pattern": "test_pattern",
                    "timestamp": datetime.now().isoformat()
                }]
            )

        try:
            # Query for Truthfulness in Math
            result = chromadb_service.query_past_mistakes(
                "Truthfulness",
                "Math",
                n=5
            )

            assert result is not None
            assert "evaluations" in result

            # Should find 2 Truthfulness evaluations (not the Clarity one)
            evaluations = result["evaluations"]
            assert len(evaluations) >= 2

            # Verify all results match the filter
            for eval_data in evaluations:
                assert eval_data["category"] == "Math"
                assert eval_data["judge_meta_score"] in [3, 4]

        finally:
            # Clean up
            collection.delete(ids=[e["id"] for e in test_evaluations])

    def test_query_past_mistakes_n_parameter(self):
        """Test query_past_mistakes respects n parameter."""
        collection = chromadb_service.get_collection()

        # Add multiple matching evaluations
        test_ids = []
        for i in range(5):
            test_id = f"test_n_param_{i}"
            test_ids.append(test_id)
            collection.add(
                ids=[test_id],
                documents=[f"User evaluating Clarity in Coding. Meta score: {i+1}."],
                metadatas=[{
                    "evaluation_id": test_id,
                    "category": "Coding",
                    "primary_metric": "Clarity",
                    "judge_meta_score": i + 1,
                    "primary_metric_gap": 0.5,
                    "weighted_gap": 0.5,
                    "mistake_pattern": "test",
                    "timestamp": datetime.now().isoformat()
                }]
            )

        try:
            # Query for only 2 results
            result = chromadb_service.query_past_mistakes(
                "Clarity",
                "Coding",
                n=2
            )

            assert result is not None
            assert len(result["evaluations"]) <= 2

        finally:
            collection.delete(ids=test_ids)

    # =====================================================
    # Helper Method Tests
    # =====================================================

    def test_extract_mistake_pattern(self):
        """Test _extract_mistake_pattern helper method."""
        alignment_analysis = {
            "Truthfulness": {
                "user_score": 5,
                "judge_score": 2,
                "gap": 3,
                "verdict": "significantly_over_estimated",
                "feedback": "Missed major error"
            },
            "Clarity": {
                "user_score": 3,
                "judge_score": 3,
                "gap": 0,
                "verdict": "aligned",
                "feedback": "Good"
            },
            "Efficiency": {
                "user_score": 1,
                "judge_score": 5,
                "gap": 4,
                "verdict": "significantly_under_estimated",
                "feedback": "Too harsh"
            }
        }

        pattern = chromadb_service._extract_mistake_pattern(alignment_analysis)

        # Should detect both over and under estimation patterns
        assert "Truthfulness_over" in pattern or "Efficiency_under" in pattern

    def test_create_document_text_length(self):
        """Test _create_document_text produces reasonable length."""
        # Create test objects (using dict-like structure for simplicity)
        class MockUserEval:
            evaluations = {
                "Truthfulness": {"score": 3, "reasoning": "Okay"},
                "Clarity": {"score": 5, "reasoning": "Clear"}
            }

        class MockJudgeEval:
            independent_scores = {
                "Truthfulness": {"score": 2, "rationale": "Not great"},
                "Clarity": {"score": 5, "rationale": "Clear"}
            }
            judge_meta_score = 3
            primary_metric_gap = 1.0
            overall_feedback = "Needs improvement on detecting errors"
            created_at = datetime.now()

        class MockQuestion:
            category = "Math"

        class MockModelResponse:
            model_name = "openai/gpt-3.5-turbo"

        doc_text = chromadb_service._create_document_text(
            user_eval=MockUserEval(),
            judge_eval=MockJudgeEval(),
            question=MockQuestion(),
            model_response=MockModelResponse(),
            primary_metric="Truthfulness"
        )

        # Should be reasonable length (~300-600 chars)
        assert len(doc_text) > 100
        assert len(doc_text) < 800
        assert "Truthfulness" in doc_text
        assert "Math" in doc_text
        assert "Feedback:" in doc_text
