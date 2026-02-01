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

    # Future: Add to memory (Task 4.2)
    # chromadb_service.add_to_memory("eval_123", "judge_456")

    # Future: Query past mistakes (Task 4.3)
    # results = chromadb_service.query_past_mistakes("Truthfulness", "Math", n=5)
"""

import logging
from typing import Optional

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
    # Placeholder for Future Tasks
    # =====================================================

    def add_to_memory(self, user_eval_id: str, judge_eval_id: str) -> None:
        """
        Store evaluation in ChromaDB vector memory.

        **IMPLEMENTATION IN TASK 4.2**

        Creates an embedding from evaluation data and stores
        in collection with metadata for filtering.

        Args:
            user_eval_id: User evaluation ID
            judge_eval_id: Judge evaluation ID

        Raises:
            NotImplementedError: Until Task 4.2
        """
        raise NotImplementedError(
            "add_to_memory() will be implemented in Task 4.2"
        )

    def query_past_mistakes(
        self,
        primary_metric: str,
        category: str,
        n: int = 5
    ) -> dict:
        """
        Query similar past evaluations from memory.

        **IMPLEMENTATION IN TASK 4.3**

        Searches for evaluations matching the same primary_metric
        and category to find patterns in user mistakes.

        Args:
            primary_metric: Metric being evaluated (e.g., "Truthfulness")
            category: Question category (e.g., "Math")
            n: Number of results to return (default: 5)

        Returns:
            {
                "ids": [["eval_001", "eval_042", ...]],
                "documents": [["...", ...]],
                "metadatas": [[{...}, ...]],
                "distances": [[0.12, 0.18, ...]]
            }

        Raises:
            NotImplementedError: Until Task 4.3
        """
        raise NotImplementedError(
            "query_past_mistakes() will be implemented in Task 4.3"
        )


# =====================================================
# Global Service Instance
# =====================================================

chromadb_service = ChromaDBService()
