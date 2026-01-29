"""
MentorMind - Health Endpoint Tests

Tests for the health check endpoints.
"""

import pytest


def test_root_endpoint(test_client):
    """Test the root endpoint returns API information."""
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "MentorMind API"
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
    assert "documentation" in data
    assert data["documentation"] == "/docs"


def test_health_basic(test_client):
    """Test the basic health check endpoint."""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "api" in data
    assert data["api"] == "connected"
    assert "database" in data
    assert data["database"] in ["connected", "disconnected"]
    assert "chromadb" in data


def test_health_detailed(test_client):
    """Test the detailed health check endpoint."""
    response = test_client.get("/health/detailed")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]

    # Check API section
    assert "api" in data
    api_data = data["api"]
    assert "status" in api_data
    assert api_data["status"] == "running"
    assert "version" in api_data
    assert "environment" in api_data

    # Check database section
    assert "database" in data
    db_data = data["database"]
    assert "status" in db_data
    assert "latency_ms" in db_data
    assert isinstance(db_data["latency_ms"], (int, float))

    # Check ChromaDB section
    assert "chromadb" in data
    chroma_data = data["chromadb"]
    assert "status" in chroma_data


def test_health_response_headers(test_client):
    """Test that health endpoints include proper headers."""
    response = test_client.get("/health")

    # Check content type
    assert "content-type" in response.headers
    assert "application/json" in response.headers["content-type"]

    # Check for request ID header (added by logging middleware)
    assert "x-request-id" in response.headers


def test_info_endpoint_development(test_client):
    """Test the info endpoint (development only)."""
    response = test_client.get("/info")

    # Info endpoint should be available in development
    assert response.status_code == 200

    data = response.json()
    assert "environment" in data
    assert data["environment"] == "development"
    assert "version" in data
    assert "api" in data
    assert "models" in data
    assert "cors_origins" in data
    assert "logging" in data
