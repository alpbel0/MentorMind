"""
MentorMind - Main Application Entry Point

This module initializes the FastAPI application and configures
all middleware, routers, and event handlers.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings

# =====================================================
# Configure Logging
# =====================================================
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# =====================================================
# Lifespan Context Manager
# =====================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events.

    Startup:
    - Log application start
    - Log environment configuration

    Shutdown:
    - Log application shutdown
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting MentorMind API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info(f"API Host: {settings.api_host}")
    logger.info(f"API Port: {settings.api_port}")
    logger.info(f"Hot Reload: {settings.reload}")
    logger.info(f"Judge Model: {settings.judge_model}")
    logger.info(f"Claude Model: {settings.claude_model}")
    logger.info(f"K Models: {settings.k_models_list}")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("Shutting down MentorMind API...")
    logger.info("=" * 60)


# =====================================================
# Create FastAPI Application
# =====================================================
app = FastAPI(
    title="MentorMind API",
    description="AI Evaluator Training System - Learn to evaluate LLM responses across 8 critical metrics",
    version="1.0.0-MVP",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# =====================================================
# Configure CORS Middleware
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# Root Endpoint
# =====================================================
@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint - API information.

    Returns basic API information including status, version, and environment.
    """
    return {
        "message": "MentorMind API",
        "status": "healthy",
        "version": "1.0.0-MVP",
        "environment": settings.environment,
        "documentation": "/docs",
    }


# =====================================================
# Health Check Endpoint
# =====================================================
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns the current health status of the API and its dependencies.
    Database and ChromaDB connections will be updated in later tasks.
    """
    return {
        "status": "healthy",
        "api": "connected",
        "database": "not yet connected",
        "chromadb": "not yet connected",
    }


# =====================================================
# Detailed Health Check Endpoint
# =====================================================
@app.get("/health/detailed", tags=["Health"])
async def health_check_detailed() -> dict:
    """
    Detailed health check endpoint.

    Returns detailed health information for all system components.
    Will be expanded in later tasks to include database and
    ChromaDB connection status with latency metrics.
    """
    return {
        "status": "healthy",
        "api": {
            "status": "running",
            "version": "1.0.0-MVP",
            "environment": settings.environment,
        },
        "database": {
            "status": "not connected",
            "message": "Database connection will be established in Task 1.5",
        },
        "chromadb": {
            "status": "not connected",
            "message": "ChromaDB connection will be established in Task 1.5",
        },
    }


# =====================================================
# Info Endpoint (Development Only)
# =====================================================
if settings.environment == "development":
    @app.get("/info", tags=["Development"])
    async def info() -> dict:
        """
        Development info endpoint.

        Returns detailed configuration information for debugging.
        Only available in development environment.
        """
        return {
            "environment": settings.environment,
            "version": "1.0.0-MVP",
            "api": {
                "host": settings.api_host,
                "port": settings.api_port,
                "reload": settings.reload,
            },
            "models": {
                "claude": settings.claude_model,
                "judge": settings.judge_model,
                "k_models": settings.k_models_list,
                "embedding": settings.embedding_model,
            },
            "cors_origins": settings.cors_origins_list,
            "logging": {
                "level": settings.log_level,
                "llm_logging": settings.enable_llm_logging,
            },
        }


# =====================================================
# Startup Event (Alternative to lifespan for simple cases)
# =====================================================
@app.on_event("startup")
async def startup_event():
    """Additional startup event handler."""
    logger.info("FastAPI application initialized successfully")
    logger.info("API Documentation available at: http://localhost:8000/docs")


# =====================================================
# Shutdown Event
# =====================================================
@app.on_event("shutdown")
async def shutdown_event():
    """Additional shutdown event handler."""
    logger.info("FastAPI application shutdown complete")


# =====================================================
# Run Application (for development)
# =====================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
