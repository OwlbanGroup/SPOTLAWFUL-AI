"""Utility script to rewrite `spotlawful_ai/logging_config.py` with a clean logging implementation."""

from pathlib import Path


LOGGING_CONFIG_SOURCE = '''"""
Logging configuration and utilities for SPOTLAWFUL-AI.
Provides structured logging with file and console handlers.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional

from spotlawful_ai.config import Config


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure logging with file and console handlers.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file path
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured logger
    """
    level = getattr(logging, log_level or Config.LOG_LEVEL, logging.INFO)
    filename = log_file or Config.LOG_FILE

    logger = logging.getLogger("spotlawful_ai")
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        filename,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("Logging configured")
    return logger


class StructuredLogger:
    """Logger with structured logging capabilities."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log with structured data."""
        if extra:
            message = "%s | %s" % (message, extra)
        self.logger.log(level, message)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, kwargs if kwargs else None)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, kwargs if kwargs else None)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, kwargs if kwargs else None)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, message, kwargs if kwargs else None)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, message, kwargs if kwargs else None)

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, exc_info=True)


class RequestLogger:
    """Logger for HTTP requests."""

    def __init__(self):
        self.logger = logging.getLogger("spotlawful_ai.requests")

    def log_request(
        self,
        method: str,
        path: str,
        user_id: Optional[str] = None,
        status_code: Optional[int] = None,
        duration_ms: Optional[float] = None
    ):
        """Log HTTP request."""
        self.logger.info(
            "%s %s | user=%s | status=%s | duration=%sms",
            method, path, user_id, status_code, duration_ms
        )

    def log_error(
        self,
        method: str,
        path: str,
        error: str,
        user_id: Optional[str] = None
    ):
        """Log HTTP request error."""
        self.logger.error(
            "%s %s | user=%s | error=%s",
            method, path, user_id, error
        )


class ModelLogger:
    """Logger for AI model operations."""

    def __init__(self):
        self.logger = logging.getLogger("spotlawful_ai.model")

    def log_training(
        self,
        model_name: str,
        epoch: int,
        loss: float,
        val_loss: Optional[float] = None
    ):
        """Log model training progress."""
        val_loss_str = "%.4f" % val_loss if val_loss else "N/A"
        self.logger.info(
            "Training %s | epoch=%s | loss=%.4f | val_loss=%s",
            model_name, epoch, loss, val_loss_str
        )

    def log_prediction(
        self,
        model_name: str,
        prediction: Any,
        confidence: float
    ):
        """Log model prediction."""
        self.logger.debug(
            "Prediction %s | pred=%s | confidence=%.4f",
            model_name, prediction, confidence
        )

    def log_evaluation(
        self,
        model_name: str,
        accuracy: float,
        precision: float,
        recall: float
    ):
        """Log model evaluation."""
        self.logger.info(
            "Evaluation %s | accuracy=%.4f | precision=%.4f | recall=%.4f",
            model_name, accuracy, precision, recall
        )


logger = setup_logging()


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger for a module."""
    return StructuredLogger(name)
'''


def main() -> None:
    """Write the logging configuration source file."""
    Path("spotlawful_ai/logging_config.py").write_text(
        LOGGING_CONFIG_SOURCE,
        encoding="utf-8",
    )
    print("File written successfully")


if __name__ == "__main__":
    main()
