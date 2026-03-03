"""Structured logging setup for the agent system."""

from __future__ import annotations

import logging
import sys
from typing import Any


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a configured logger with structured formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger


def log_skill_call(logger: logging.Logger, skill_name: str, method: str, params: dict[str, Any] | None = None) -> None:
    """Standardized logging for skill invocations."""
    params_str = ", ".join(f"{k}={v!r}" for k, v in (params or {}).items())
    logger.info("SKILL_CALL  | %s.%s(%s)", skill_name, method, params_str)


def log_agent_step(logger: logging.Logger, agent_name: str, step: str, details: str = "") -> None:
    """Standardized logging for agent workflow steps."""
    msg = f"AGENT_STEP  | {agent_name} | {step}"
    if details:
        msg += f" | {details}"
    logger.info(msg)
