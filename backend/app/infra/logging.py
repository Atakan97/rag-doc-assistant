"""
Structured logging configuration for the backend application.

Sets up JSON-formatted logging with request context tracking.
Log level is configurable with the LOG_LEVEL environment variable.
"""

import os
import logging
import sys


def setup_logging():
    """
    Configure the application logging format and level.
    Log level defaults to INFO but can be overridden with LOG_LEVEL env var.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Configure the root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,  # Override any existing logging config
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at {log_level} level")
