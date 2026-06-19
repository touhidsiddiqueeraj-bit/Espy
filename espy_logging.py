"""Shared logger for Espy.

All discovery / worker code should use this logger so users can debug
"why isn't my device being detected" by reading espy_debug.log next to
the executable.

Run with `python main.py --debug` to also mirror the log to stderr.
"""
from __future__ import annotations
import logging
import os
import sys
from pathlib import Path


def _default_log_path() -> Path:
    """Put the log next to the executable (frozen) or next to main.py."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        # Walk up from this file to find the project root (where main.py lives).
        base = Path(__file__).resolve().parent
    return base / "espy_debug.log"


LOG_PATH = _default_log_path()

_logger = logging.getLogger("espy")
_logger.setLevel(logging.DEBUG)

_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(threadName)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

_file_handler = logging.FileHandler(str(LOG_PATH), encoding="utf-8")
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(_formatter)
_logger.addHandler(_file_handler)

if "--debug" in sys.argv:
    _stream_handler = logging.StreamHandler(sys.stderr)
    _stream_handler.setLevel(logging.DEBUG)
    _stream_handler.setFormatter(_formatter)
    _logger.addHandler(_stream_handler)

_logger.info("=== Espy logger initialized, log file: %s ===", LOG_PATH)


def get_logger(name: str = "espy") -> logging.Logger:
    """Get a child logger under the 'espy' namespace."""
    return _logger.getChild(name) if name != "espy" else _logger
