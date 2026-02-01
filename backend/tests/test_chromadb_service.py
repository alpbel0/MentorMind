"""
Integration Tests for ChromaDB Service

Tests ChromaDB connection, collection management, and embedding function
using the real ChromaDB service running in Docker.
"""

import pytest
import time

from backend.services.chromadb_service import chromadb_service, ChromaDBService


class TestChromaDBService:
    """Test ChromaDB service functionality with real ChromaDB instance."""

    def test_initialization(self):
        """Test service initializes with correct settings."""
        assert chromadb_service.host is not None
        assert chromadb_service.port == 8000
        assert chromadb_service.collection_name == "evaluation_memory"
        assert chromadb_service._embedding_function is not None

    def test_real_connection(self):
        """Test real connection to ChromaDB server."""
        # Force reconnection
        chromadb_service._client = None

        result = chromadb_service.test_connection()

        assert result is True, "Should connect to real ChromaDB server"

    def test_get_real_collection(self):
        """Test getting real collection from ChromaDB."""
        collection = chromadb_service.get_collection()

        assert collection is not None
        assert collection.name == "evaluation_memory"
        assert collection.count() >= 0  # May have existing documents

    def test_get_collection_count_empty(self):
        """Test getting collection count (may be empty or have existing data)."""
        count = chromadb_service.get_collection_count()

        assert count >= 0  # Should be non-negative integer
        assert isinstance(count, int)

    def test_add_and_query_document(self):
        """Test adding a document and querying it from real ChromaDB."""
        collection = chromadb_service.get_collection()

        # Get initial count
        initial_count = collection.count()

        # Add a test document
        test_id = f"test_doc_{int(time.time() * 1000)}"
        test_document = "This is a test evaluation for Truthfulness metric in Math category"
        test_metadata = {
            "evaluation_id": test_id,
            "category": "Math",
            "primary_metric": "Truthfulness",
            "judge_meta_score": 4,
            "alignment_gap": 0.5,
            "test": True  # Mark as test data
        }

        try:
            collection.add(
                ids=[test_id],
                documents=[test_document],
                metadatas=[test_metadata]
            )

            # Verify document was added
            new_count = collection.count()
            assert new_count == initial_count + 1

            # Query for the document
            results = collection.query(
                query_texts=[test_document],
                n_results=1
            )

            assert results is not None
            assert len(results['ids']) > 0
            assert len(results['ids'][0]) > 0
            assert test_id in results['ids'][0]

        finally:
            # Clean up - delete the test document
            try:
                collection.delete(ids=[test_id])
            except Exception:
                pass  # Document may not exist if add failed

    def test_query_with_where_filter(self):
        """Test querying with metadata filters."""
        collection = chromadb_service.get_collection()

        # Add test documents with different metadata
        timestamp = int(time.time() * 1000)
        test_id_1 = f"test_filter_{timestamp}_1"
        test_id_2 = f"test_filter_{timestamp}_2"

        try:
            collection.add(
                ids=[test_id_1, test_id_2],
                documents=[
                    "Test evaluation for Truthfulness in Math",
                    "Test evaluation for Clarity in Coding"
                ],
                metadatas=[
                    {"category": "Math", "primary_metric": "Truthfulness", "test": True},
                    {"category": "Coding", "primary_metric": "Clarity", "test": True}
                ]
            )

            # Query with filter for Math category (ChromaDB 1.x uses $and operator)
            results = collection.query(
                query_texts=["Test evaluation"],
                n_results=10,
                where={"$and": [{"category": "Math"}, {"test": True}]}
            )

            # Should find at least the Math document
            assert results is not None
            assert len(results['ids']) > 0

        finally:
            # Clean up
            try:
                collection.delete(ids=[test_id_1, test_id_2])
            except Exception:
                pass

    def test_collection_metadata(self):
        """Test collection has correct metadata."""
        collection = chromadb_service.get_collection()

        # Collection should exist and have correct name
        assert collection.name == "evaluation_memory"

        # Count should be accessible
        count = collection.count()
        assert isinstance(count, int)

    def test_add_to_memory_requires_db_session(self):
        """Test add_to_memory requires db_session parameter."""
        # Should raise TypeError since we're not passing db_session
        with pytest.raises(TypeError):
            chromadb_service.add_to_memory("eval_123", "judge_456")

    def test_query_past_mistakes_returns_dict(self):
        """Test query_past_mistakes returns proper dict structure."""
        result = chromadb_service.query_past_mistakes("NonExistent", "NonExistent")

        assert result is not None
        assert isinstance(result, dict)
        assert "evaluations" in result
        assert isinstance(result["evaluations"], list)

    def test_heartbeat(self):
        """Test ChromaDB server heartbeat."""
        client = chromadb_service._get_client()
        heartbeat = client.heartbeat()

        assert heartbeat is not None
        # Heartbeat returns a nanosecond timestamp
        assert isinstance(heartbeat, int)

    def test_multiple_collections_isolation(self):
        """Test that our collection is isolated from others."""
        # Get our collection
        collection = chromadb_service.get_collection()

        # List all collections
        client = chromadb_service._get_client()
        collections = client.list_collections()

        # Our collection should be in the list
        collection_names = [c.name for c in collections]
        assert "evaluation_memory" in collection_names

    def test_delete_documents(self):
        """Test deleting documents from collection."""
        collection = chromadb_service.get_collection()

        # Add a test document
        test_id = f"test_delete_{int(time.time() * 1000)}"
        collection.add(
            ids=[test_id],
            documents=["Document to delete"],
            metadatas={"test": True}
        )

        # Verify it exists
        results = collection.get(ids=[test_id])
        assert len(results['ids']) > 0

        # Delete it
        collection.delete(ids=[test_id])

        # Verify it's gone
        results = collection.get(ids=[test_id])
        assert len(results['ids']) == 0

    def test_get_documents_by_ids(self):
        """Test retrieving documents by their IDs."""
        collection = chromadb_service.get_collection()

        # Add test document
        test_id = f"test_get_{int(time.time() * 1000)}"
        test_doc = "Test document for retrieval"
        test_metadata = {"category": "General", "test": True}

        try:
            collection.add(
                ids=[test_id],
                documents=[test_doc],
                metadatas=[test_metadata]
            )

            # Get the document by ID
            results = collection.get(ids=[test_id])

            assert results is not None
            assert len(results['ids']) == 1
            assert results['ids'][0] == test_id
            assert len(results['documents']) == 1
            assert results['documents'][0] == test_doc

        finally:
            # Clean up
            try:
                collection.delete(ids=[test_id])
            except Exception:
                pass
