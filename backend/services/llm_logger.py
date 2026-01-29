"""
MentorMind - LLM Call Logger

This module provides logging functionality for LLM API calls.
It logs all LLM interactions in JSONL format for cost analysis and debugging.
"""

import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from backend.config.settings import settings


logger = logging.getLogger(__name__)


# =====================================================
# LLM Provider Types
# =====================================================

LLMProvider = Literal["anthropic", "openai", "google", "unknown"]


# =====================================================
# LLM Call Logger (Singleton)
# =====================================================

class LLMCallLogger:
    """
    Singleton logger for tracking LLM API calls.

    Logs are written in JSONL format (one JSON object per line)
    for easy parsing and analysis.

    Thread-safe for concurrent usage.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "LLMCallLogger":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the logger (only once)."""
        if self._initialized:
            return

        self._enabled = settings.enable_llm_logging
        self._log_file_path = Path(settings.llm_log_file)
        self._lock = threading.Lock()

        # Create log directory if it doesn't exist
        self._log_file_path.parent.mkdir(parents=True, exist_ok=True)

        self._initialized = True

    def _write_log_entry(self, entry: dict[str, Any]) -> None:
        """
        Write a log entry to the JSONL file.

        Thread-safe file writing.

        Args:
            entry: Dictionary containing log entry data
        """
        with self._lock:
            try:
                with open(self._log_file_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception as e:
                logger.error(f"Failed to write LLM log entry: {e}")

    def log_call(
        self,
        provider: LLMProvider,
        model: str,
        purpose: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        duration_seconds: float = 0.0,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """
        Log an LLM API call.

        Args:
            provider: LLM provider (anthropic, openai, google)
            model: Model name (e.g., "gpt-4o", "claude-sonnet-4-20250514")
            purpose: Purpose of the call (e.g., "question_generation", "judge_evaluation")
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            total_tokens: Total tokens used
            duration_seconds: API call duration in seconds
            success: Whether the call was successful
            error: Error message if the call failed
        """
        if not self._enabled:
            return

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "provider": provider,
            "model": model,
            "purpose": purpose,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "duration_seconds": duration_seconds,
            "success": success,
            "error": error,
        }

        self._write_log_entry(entry)

        # Also log to standard logger for immediate visibility
        if success:
            logger.debug(
                f"LLM call: {provider}/{model} - {purpose} - "
                f"{total_tokens} tokens - {duration_seconds:.2f}s"
            )
        else:
            logger.warning(
                f"LLM call failed: {provider}/{model} - {purpose} - {error}"
            )


# =====================================================
# Global Logger Instance
# =====================================================

llm_logger = LLMCallLogger()


# =====================================================
# Convenience Functions
# =====================================================

def log_llm_call(
    provider: LLMProvider,
    model: str,
    purpose: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    duration_seconds: float = 0.0,
    success: bool = True,
    error: str | None = None,
) -> None:
    """
    Log an LLM API call using the global logger instance.

    This is the preferred way to log LLM calls from other modules.

    Args:
        provider: LLM provider (anthropic, openai, google)
        model: Model name
        purpose: Purpose of the call
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        total_tokens: Total tokens used
        duration_seconds: API call duration in seconds
        success: Whether the call was successful
        error: Error message if the call failed
    """
    llm_logger.log_call(
        provider=provider,
        model=model,
        purpose=purpose,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        duration_seconds=duration_seconds,
        success=success,
        error=error,
    )
