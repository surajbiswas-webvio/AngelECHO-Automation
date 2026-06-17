from __future__ import annotations

"""Logging factory used by fixtures, page objects, and API helpers."""

import logging
import os
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.settings import ROOT_DIR


def get_logger(name: str) -> logging.Logger:
    """
    Purpose:
        Creates or returns a configured project logger.

    Why Needed:
        Standardizes log formatting, file rotation, and console output across
        the automation framework.

    Args:
        name: Logger name, usually the class or module requesting logging.

    Returns:
        Configured logging.Logger instance.

    Notes:
        Existing handlers are reused to avoid duplicate log lines when modules
        are imported multiple times.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    log_dir = ROOT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        file_handler = RotatingFileHandler(
            log_dir / "automation.log",
            maxBytes=5_000_000,
            backupCount=5,
            encoding="utf-8",
        )
    except PermissionError:
        fallback_dir = Path(tempfile.gettempdir()) / "angelecho-automation-logs"
        fallback_dir.mkdir(exist_ok=True)
        file_handler = RotatingFileHandler(
            fallback_dir / f"automation-{os.getpid()}.log",
            maxBytes=5_000_000,
            backupCount=2,
            encoding="utf-8",
        )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger
