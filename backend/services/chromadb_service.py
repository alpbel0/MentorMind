"""
MentorMind - ChromaDB Vector Memory Service

This module handles ChromaDB integration for storing and retrieving
evaluation patterns as embeddings. Used by judge Stage 2 for
pattern recognition and feedback.

Usage:
    from backend.services.chromadb_service import chromadb_service

    # Test connection
    if chromadb_service.test_connection():
        collection = chromadb_service.get_collection()

    # Add evaluation to memory (Task 4.2)
    from backend.models.database import SessionLocal
    db = SessionLocal()
    chromadb_service.add_to_memory(db, "eval_123", "judge_456")

    # Query past mistakes (Task 4.3)
    results = chromadb_service.query_past_mistakes("Truthfulness", "Math", n=5)
"""

import json
import logging
from typing import Optional, Any

import chromadb
from chromadb.config import Settings
import chromadb.utils.embedding_functions as embedding_functions

from backend.config.settings import settings

logger = logging.getLogger(__name__)


# =====================================================
# ChromaDB Service Class
# =====================================================

class ChromaDBService:
    """
    Service for ChromaDB vector memory operations.

    Handles:
    - ChromaDB HTTP client initialization
    - Collection management (get/create)
    - Embedding function configuration (OpenAI)
    - Connection health testing

    Future (Tasks 4.2, 4.3):
    - add_to_memory() - Store evaluations as embeddings
    - query_past_mistakes() - Retrieve similar past evaluations
    """

    def __init__(self):
        """Initialize ChromaDB service with settings from config."""
        self.host: str = settings.chroma_host
        self.port: int = settings.chroma_port
        self.collection_name: str = settings.chroma_collection_name
        self.api_key: Optional[str] = settings.openai_api_key  # For embeddings

        # ChromaDB client (initialized lazily)
        self._client: Optional[chromadb.Client] = None

        # Embedding function (OpenAI text-embedding-3-small)
        self._embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self.api_key,
            model_name=settings.embedding_model
        )

        logger.info(
            f"ChromaDBService initialized: host={self.host}, "
            f"port={self.port}, collection={self.collection_name}"
        )

    # =====================================================
    # Connection Management
    # =====================================================

    def _get_client(self) -> chromadb.Client:
        """
        Get or create ChromaDB HTTP client.

        Uses lazy initialization pattern - client is created
        only when first requested.

        Returns:
            ChromaDB HTTP client instance

        Raises:
            RuntimeError: If connection to ChromaDB fails
        """
        if self._client is None:
            try:
                # Create HTTP client for server mode (ChromaDB 1.x compatible)
                self._client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                logger.info(f"Connected to ChromaDB at {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"Failed to connect to ChromaDB: {e}")
                raise RuntimeError(
                    f"ChromaDB connection failed: {e}"
                )

        return self._client

    def test_connection(self) -> bool:
        """
        Test connection to ChromaDB server.

        Attempts to connect and retrieve heartbeat.
        Used by health check endpoints.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            client = self._get_client()
            # Try to get heartbeat (ChromaDB way to check connection)
            _ = client.heartbeat()
            logger.debug("ChromaDB connection test: SUCCESS")
            return True
        except Exception as e:
            logger.warning(f"ChromaDB connection test: FAILED - {e}")
            return False

    # =====================================================
    # Collection Management
    # =====================================================

    def get_collection(self):
        """
        Get or create the evaluation memory collection.

        The collection stores evaluation embeddings with metadata
        for similarity search and pattern recognition.

        Collection name: "evaluation_memory" (from settings)
        Embedding function: OpenAI text-embedding-3-small
        Similarity metric: cosine (default)

        Returns:
            ChromaDB collection object

        Raises:
            RuntimeError: If collection retrieval/creation fails
        """
        try:
            client = self._get_client()

            # Get or create collection without embedding function (API compatibility)
            # We'll use the embedding function directly when adding/querying documents
            collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "User evaluation patterns and past mistakes",
                    "hnsw:space": "cosine"  # Similarity metric
                }
            )

            logger.debug(f"Retrieved collection: {self.collection_name}")
            return collection

        except Exception as e:
            logger.error(f"Failed to get collection: {e}")
            raise RuntimeError(f"Collection retrieval failed: {e}")

    def get_collection_count(self) -> int:
        """
        Get the number of documents in the collection.

        Useful for health checks and monitoring.

        Returns:
            Number of documents in collection (0 if empty)

        Raises:
            RuntimeError: If query fails
        """
        try:
            collection = self.get_collection()
            count = collection.count()
            logger.debug(f"Collection count: {count}")
            return count
        except Exception as e:
            logger.error(f"Failed to get collection count: {e}")
            return 0

    # =====================================================
    # Memory Operations (Tasks 4.2 & 4.3)
    # =====================================================

    def add_to_memory(
        self,
        db_session: Any,
        user_eval_id: str,
        judge_eval_id: str
    ) -> None:
        """
        Store evaluation in ChromaDB vector memory (Task 4.2).

        Fetches evaluation data from PostgreSQL, creates a document with
        balanced detail level (~500 chars), and stores as embedding for
        pattern recognition in future judge evaluations.

        Args:
            db_session: SQLAlchemy database session (dependency injection)
            user_eval_id: User evaluation ID (format: eval_YYYYMMDD_...)
            judge_eval_id: Judge evaluation ID (format: judge_YYYYMMDD_...)

        Raises:
            ValueError: If evaluation data not found
            RuntimeError: If ChromaDB operation fails
        """
        from backend.models.user_evaluation import UserEvaluation
        from backend.models.judge_evaluation import JudgeEvaluation
        from backend.models.model_response import ModelResponse
        from backend.models.question import Question

        # Fetch evaluation data (4-table join via manual queries)
        user_eval = db_session.query(UserEvaluation).filter_by(id=user_eval_id).first()
        if not user_eval:
            raise ValueError(f"User evaluation {user_eval_id} not found")

        judge_eval = db_session.query(JudgeEvaluation).filter_by(id=judge_eval_id).first()
        if not judge_eval:
            raise ValueError(f"Judge evaluation {judge_eval_id} not found")

        model_response = db_session.query(ModelResponse).filter_by(id=user_eval.response_id).first()
        if not model_response:
            raise ValueError(f"Model response {user_eval.response_id} not found")

        question = db_session.query(Question).filter_by(id=model_response.question_id).first()
        if not question:
            raise ValueError(f"Question {model_response.question_id} not found")

        # Determine primary metric
        primary_metric = judge_eval.primary_metric
        bonus_metrics = question.bonus_metrics or []

        # Create balanced document text (~500 chars)
        document_text = self._create_document_text(
            user_eval=user_eval,
            judge_eval=judge_eval,
            question=question,
            model_response=model_response,
            primary_metric=primary_metric
        )

        # Create metadata for filtering
        metadata = {
            "evaluation_id": user_eval_id,
            "judge_id": judge_eval_id,
            "category": question.category,
            "primary_metric": primary_metric,
            "difficulty": question.difficulty,
            "judge_meta_score": judge_eval.judge_meta_score,
            "primary_metric_gap": judge_eval.primary_metric_gap,
            "weighted_gap": judge_eval.weighted_gap,
            "model_name": model_response.model_name,
            "timestamp": judge_eval.created_at.isoformat(),
            "mistake_pattern": self._extract_mistake_pattern(judge_eval.alignment_analysis)
        }

        # Add to ChromaDB collection
        try:
            collection = self.get_collection()
            collection.add(
                ids=[user_eval_id],  # Use user_eval_id as document ID
                documents=[document_text],
                metadatas=[metadata]
            )
            logger.info(f"Added evaluation {user_eval_id} to ChromaDB memory")
        except Exception as e:
            logger.error(f"Failed to add to ChromaDB: {e}")
            raise RuntimeError(f"ChromaDB add failed: {e}")

    def query_past_mistakes(
        self,
        primary_metric: str,
        category: str,
        n: int = 5
    ) -> dict:
        """
        Query similar past evaluations from memory (Task 4.3).

        Searches for evaluations matching the same primary_metric and category
        to find patterns in user mistakes for context in Stage 2 feedback.

        Args:
            primary_metric: Metric being evaluated (e.g., "Truthfulness")
            category: Question category (e.g., "Math")
            n: Number of results to return (default: 5)

        Returns:
            {
                "evaluations": [
                    {
                        "evaluation_id": "eval_...",
                        "category": "Math",
                        "judge_meta_score": 3,
                        "primary_gap": 1.2,
                        "feedback": "Overestimated minor errors...",
                        "mistake_pattern": "Truthfulness_bias",
                        "timestamp": "2025-01-30T14:30:00Z"
                    },
                    ...
                ]
            }

        Raises:
            RuntimeError: If ChromaDB query fails
        """
        try:
            collection = self.get_collection()

            # Query text for embedding
            query_text = f"User evaluating {primary_metric} in {category} category"

            # Query with metadata filter (ChromaDB 1.x syntax)
            results = collection.query(
                query_texts=[query_text],
                n_results=n,
                where={"$and": [
                    {"primary_metric": primary_metric},
                    {"category": category}
                ]}
            )

            # Handle empty results
            if not results or not results['ids'] or not results['ids'][0]:
                logger.info(f"No past mistakes found for {primary_metric} in {category}")
                return {"evaluations": []}

            # Format results into simplified structure
            evaluations = []
            for i, doc_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                # Extract feedback from document if available
                feedback = self._extract_feedback_from_doc(
                    results.get('documents', [[]])[0][i] if results.get('documents') else ""
                )
                evaluations.append({
                    "evaluation_id": metadata.get('evaluation_id', doc_id),
                    "category": metadata.get('category', ''),
                    "judge_meta_score": metadata.get('judge_meta_score', 0),
                    "primary_gap": metadata.get('primary_metric_gap', 0.0),
                    "feedback": feedback,
                    "mistake_pattern": metadata.get('mistake_pattern', ''),
                    "timestamp": metadata.get('timestamp', '')
                })

            logger.info(f"Found {len(evaluations)} past mistakes for {primary_metric} in {category}")
            return {"evaluations": evaluations}

        except Exception as e:
            logger.error(f"Failed to query ChromaDB: {e}")
            raise RuntimeError(f"ChromaDB query failed: {e}")

    # =====================================================
    # Helper Methods
    # =====================================================

    def _create_document_text(
        self,
        user_eval: Any,
        judge_eval: Any,
        question: Any,
        model_response: Any,
        primary_metric: str
    ) -> str:
        """
        Create balanced document text for embedding (~500 chars).

        Includes key fields for semantic search while keeping size
        manageable for embedding generation.

        Args:
            user_eval: UserEvaluation ORM object
            judge_eval: JudgeEvaluation ORM object
            question: Question ORM object
            model_response: ModelResponse ORM object
            primary_metric: Primary metric name

        Returns:
            Document text string (~500 chars)
        """
        # Extract user scores (only non-null scores)
        user_scores = {
            k: v['score']
            for k, v in user_eval.evaluations.items()
            if v.get('score') is not None
        }

        # Extract judge scores
        judge_scores = {
            k: v['score']
            for k, v in judge_eval.independent_scores.items()
        }

        # Build document text
        doc = (
            f"User evaluated {model_response.model_name} on {question.category} question. "
            f"Primary metric: {primary_metric}. "
            f"User scores: {json.dumps(user_scores)}. "
            f"Judge scores: {json.dumps(judge_scores)}. "
            f"Meta score: {judge_eval.judge_meta_score}/5. "
            f"Primary gap: {judge_eval.primary_metric_gap}. "
        )

        # Truncate feedback if needed (keep first 150 chars)
        feedback = judge_eval.overall_feedback or ""
        if len(feedback) > 150:
            feedback = feedback[:147] + "..."
        doc += f"Feedback: {feedback}"

        # Add timestamp
        doc += f". Timestamp: {judge_eval.created_at.strftime('%Y-%m-%d %H:%M')}"

        return doc

    def _extract_mistake_pattern(self, alignment_analysis: dict) -> str:
        """
        Extract common mistake pattern from alignment analysis.

        Analyzes verdicts to detect patterns like overestimation,
        underestimation, or significant misalignment.

        Args:
            alignment_analysis: Alignment analysis dict from judge evaluation

        Returns:
            Pattern string (e.g., "Truthfulness_bias", "no_clear_pattern")
        """
        patterns = []
        for metric, data in alignment_analysis.items():
            if isinstance(data, dict):
                verdict = data.get('verdict', '')
                if 'significantly_over' in verdict or 'over_estimated' in verdict:
                    patterns.append(f"{metric}_over")
                elif 'significantly_under' in verdict or 'under_estimated' in verdict:
                    patterns.append(f"{metric}_under")
                elif 'significantly_off' in verdict:
                    patterns.append(f"{metric}_off")

        return "_".join(patterns) if patterns else "no_clear_pattern"

    def _extract_feedback_from_doc(self, document: str) -> str:
        """
        Extract feedback text from stored document.

        Args:
            document: Document text string

        Returns:
            Feedback excerpt (up to 200 chars)
        """
        if not document:
            return ""

        # Find "Feedback: " in document
        if "Feedback: " in document:
            try:
                feedback_start = document.index("Feedback: ") + len("Feedback: ")
                feedback_end = document.find(".", feedback_start)
                if feedback_end > feedback_start:
                    feedback = document[feedback_start:feedback_end]
                    return feedback[:200] if len(feedback) > 200 else feedback
            except (ValueError, IndexError):
                pass

        # Fallback: return last 200 chars of document
        return document[-200:] if len(document) > 200 else document


# =====================================================
# Global Service Instance
# =====================================================

chromadb_service = ChromaDBService()
