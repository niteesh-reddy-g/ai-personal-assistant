from __future__ import annotations

from typing import Any

from assistant.core.agent_registry import AgentRegistry
from assistant.core.llm_client import LLMClient
from assistant.core.memory import MemoryStore


class Orchestrator:
    def __init__(self, registry: AgentRegistry, llm: LLMClient, memory: MemoryStore) -> None:
        self.registry = registry
        self.llm = llm
        self.memory = memory

    async def _plan(self, instruction: str, context: dict[str, Any]) -> dict[str, Any]:
        agent_catalog = [
            {"name": a.name, "description": a.description, "capabilities": a.capabilities}
            for a in self.registry.list_agents()
        ]
        prompt = (
            "Create an execution plan for the user instruction using available agents."
            "Return JSON with steps: [{agent, task}], and updated_context object.\n"
            f"Agents: {agent_catalog}\n"
            f"Instruction: {instruction}\n"
            f"Current context: {context}"
        )
        return await self.llm.generate_json(prompt, '{"steps":[],"updated_context":{}}')

    async def run(self, instruction: str) -> dict[str, Any]:
        context = (await self.memory.load("context")) or {}
        plan = await self._plan(instruction, context)
        context.update(plan.get("updated_context", {}))
        execution_log: list[dict[str, Any]] = []
        for step in plan.get("steps", []):
            agent = self.registry.get(step["agent"])
            if not agent:
                execution_log.append({"step": step, "error": "Agent not found"})
                continue
            result = await agent.run(step.get("task", {}), context)
            execution_log.append({"step": step, "result": result})
            context[f"result_{agent.name}"] = result
        await self.memory.save("context", context)
        return {"instruction": instruction, "plan": plan, "execution_log": execution_log, "context": context}
