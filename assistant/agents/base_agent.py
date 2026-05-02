from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    name: str
    description: str
    capabilities: list[str]

    @abstractmethod
    async def run(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Execute a structured task and return structured output."""
        raise NotImplementedError
