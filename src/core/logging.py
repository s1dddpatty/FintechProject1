"""
Production-ready logging configuration using Python's built-in logging module.
Features:
- RotatingFileHandler
- Console logger
- Configurable log level
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from src.core.config import PROJECT_ROOT, settings

LOGS_DIR = PROJECT_ROOT / "logs"


def get_logger(module_name: str) -> logging.Logger:
    logger = logging.getLogger(module_name)

    if logger.hasHandlers():
        return logger

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Rotating File Handler (max 10MB per file, keep 5 backups)
    log_file_path = PROJECT_ROOT / settings.log_file
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
