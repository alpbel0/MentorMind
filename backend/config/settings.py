"""
MentorMind - Settings Configuration

This module loads and validates all environment variables using Pydantic Settings.
Environment variables are loaded from .env file in the project root.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =====================================================
    # API Keys (REQUIRED)
    # =====================================================
    anthropic_api_key: str
    openai_api_key: str
    google_api_key: str
    openrouter_api_key: str

    # =====================================================
    # PostgreSQL Database (REQUIRED)
    # =====================================================
    database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # =====================================================
    # ChromaDB Vector Database (REQUIRED)
    # =====================================================
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_persist_dir: str = "/chroma_data"
    chroma_collection_name: str = "evaluation_memory"

    # =====================================================
    # Application Settings
    # =====================================================
    environment: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    reload: bool = True

    # =====================================================
    # Judge Configuration
    # =====================================================
    judge_timeout_seconds: int = 60

    # =====================================================
    # LLM Model Configuration
    # =====================================================
    # Question generation model (Haiku 4.5 - faster, cost-effective)
    claude_question_model: str = "claude-haiku-4-5-20251001"
    # Legacy: Backward compatibility (deprecated, use claude_question_model)
    claude_model: str = "claude-sonnet-4-20250514"
    claude_api_timeout: int = 30  # Timeout for Claude API calls in seconds
    # Judge model (unchanged - GPT-4o)
    judge_model: str = "gpt-4o"
    # K Models (6 models via OpenRouter)
    k_models: str = "mistralai/mistral-nemo,qwen/qwen-2.5-7b-instruct,deepseek/deepseek-chat,google/gemini-2.0-flash-001,openai/gpt-4o-mini,openai/gpt-3.5-turbo"
    # OpenRouter Configuration
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    # Embedding model
    embedding_model: str = "text-embedding-3-small"

    # =====================================================
    # CORS Settings
    # =====================================================
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # =====================================================
    # Monitoring & Analytics
    # =====================================================
    enable_llm_logging: bool = True
    llm_log_file: str = "data/logs/llm_calls.jsonl"

    # =====================================================
    # Validators
    # =====================================================
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the valid options."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"log_level must be one of {valid_levels}, got '{v}'"
            )
        return v_upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is either development or production."""
        valid_envs = ["development", "production"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(
                f"environment must be one of {valid_envs}, got '{v}'"
            )
        return v_lower

    @field_validator("reload")
    @classmethod
    def validate_reload(cls, v: bool) -> bool:
        """Validate reload setting."""
        return v

    # =====================================================
    # Properties
    # =====================================================
    @property
    def k_models_list(self) -> List[str]:
        """Parse K_MODELS string into a list."""
        return [m.strip() for m in self.k_models.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [o.strip() for o in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
