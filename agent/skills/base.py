"""Base skill interface that all tool integrations implement."""

from __future__ import annotations

import abc
from typing import Any

from agent.utils.logging import get_logger


class BaseSkill(abc.ABC):
    """Abstract base class for all skills (tool integrations).

    Each skill wraps an external API/service and exposes typed async methods.
    Skills are stateless - they receive configuration at init and expose
    pure async functions for each capability.
    """

    name: str = "base"
    description: str = ""

    def __init__(self) -> None:
        self.logger = get_logger(f"skill.{self.name}")

    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Verify that the skill's backing service is reachable and configured."""
        ...

    @abc.abstractmethod
    async def close(self) -> None:
        """Release any held resources (HTTP clients, browsers, etc.)."""
        ...

    def capabilities(self) -> list[dict[str, str]]:
        """Return a list of capabilities this skill provides (for LLM tool-use)."""
        caps: list[dict[str, str]] = []
        for attr_name in dir(self):
            if attr_name.startswith("_") or attr_name in ("health_check", "close", "capabilities"):
                continue
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "__doc__") and attr.__doc__:
                caps.append({"name": attr_name, "description": attr.__doc__.strip()})
        return caps

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
