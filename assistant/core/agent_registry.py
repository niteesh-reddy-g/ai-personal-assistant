from __future__ import annotations

from typing import Iterable

from assistant.agents.base_agent import BaseAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def get(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def list_agents(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def by_capability(self, capability: str) -> list[BaseAgent]:
        return [a for a in self._agents.values() if capability in getattr(a, "capabilities", [])]

    def register_many(self, agents: Iterable[BaseAgent]) -> None:
        for agent in agents:
            self.register(agent)
