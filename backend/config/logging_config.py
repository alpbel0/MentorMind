"""
MentorMind - Logging Configuration

This module provides centralized logging configuration for the MentorMind application.
It sets up rotating file handlers, console output, and specialized error logging.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.config.settings import settings


# =====================================================
# Log Directory Setup
# =====================================================

LOG_DIR = Path("data/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================
# Custom Formatters
# =====================================================

class DefaultFormatter(logging.Formatter):
    """Standard log formatter with timestamp, level, name, and message."""

    def __init__(self):
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        super().__init__(fmt=fmt, datefmt=datefmt)


class DetailedFormatter(logging.Formatter):
    """Extended log formatter with file location and function name."""

    def __init__(self):
        fmt = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(pathname)s:%(lineno)d:%(funcName)s] - %(message)s"
        )
        datefmt = "%Y-%m-%d %H:%M:%S"
        super().__init__(fmt=fmt, datefmt=datefmt)


# =====================================================
# Handler Setup
# =====================================================

def setup_file_handler(
    filename: str,
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    formatter: logging.Formatter | None = None,
) -> RotatingFileHandler:
    """
    Create a rotating file handler.

    Args:
        filename: Name of the log file
        level: Logging level (default: INFO)
        max_bytes: Maximum file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        formatter: Optional formatter (uses DefaultFormatter if None)

    Returns:
        Configured RotatingFileHandler
    """
    log_path = LOG_DIR / filename
    handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(formatter or DefaultFormatter())
    return handler


def setup_console_handler(
    level: int = logging.INFO,
    formatter: logging.Formatter | None = None,
) -> logging.StreamHandler:
    """
    Create a console handler for stdout.

    Args:
        level: Logging level (default: INFO)
        formatter: Optional formatter (uses DefaultFormatter if None)

    Returns:
        Configured StreamHandler
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(formatter or DefaultFormatter())
    return handler


# =====================================================
# Main Configuration Function
# =====================================================

def setup_logging() -> None:
    """
    Configure logging for the entire application.

    Sets up:
    - Root logger with console output
    - File handler for all logs (mentormind.log)
    - Separate error file handler (errors.log)
    - Application-specific loggers

    The log level is controlled by the LOG_LEVEL environment variable.
    """
    # Get the log level from settings
    log_level = getattr(logging, settings.log_level, logging.INFO)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler (INFO and above)
    console_handler = setup_console_handler(level=log_level)
    root_logger.addHandler(console_handler)

    # Main log file (all logs at configured level)
    main_file_handler = setup_file_handler(
        "mentormind.log",
        level=log_level,
    )
    root_logger.addHandler(main_file_handler)

    # Error log file (ERROR and CRITICAL only)
    error_file_handler = setup_file_handler(
        "errors.log",
        level=logging.ERROR,
    )
    root_logger.addHandler(error_file_handler)

    # Silence noisy third-party loggers
    for logger_name in ["uvicorn.access", "uvicorn.error", "fastapi"]:
        third_party_logger = logging.getLogger(logger_name)
        third_party_logger.setLevel(logging.WARNING)


# =====================================================
# Logger Getter
# =====================================================

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module (usually __name__)

    Returns:
        Logger instance with the specified name
    """
    return logging.getLogger(name)


# =====================================================
# Auto-initialization on import
# =====================================================

# Setup logging when this module is imported
# This ensures logging is configured before any application code runs
setup_logging()
