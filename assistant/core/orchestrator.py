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
            "Create an execution plan for the user instruction using available agents. "
            "Return JSON with steps: [{agent, task}], and updated_context object. "
            "Every step.task must be an object (JSON dictionary).\n"
            f"Agents: {agent_catalog}\n"
            f"Instruction: {instruction}\n"
            f"Current context: {context}"
        )
        return await self.llm.generate_json(prompt, '{"steps":[],"updated_context":{}}')

    @staticmethod
    def _normalize_plan(raw_plan: Any) -> dict[str, Any]:
        if not isinstance(raw_plan, dict):
            return {"steps": [], "updated_context": {}}

        normalized: dict[str, Any] = {
            "steps": raw_plan.get("steps", []),
            "updated_context": raw_plan.get("updated_context", {}),
        }

        if not isinstance(normalized["steps"], list):
            normalized["steps"] = []
        if not isinstance(normalized["updated_context"], dict):
            normalized["updated_context"] = {}

        clean_steps: list[dict[str, Any]] = []
        for raw_step in normalized["steps"]:
            if not isinstance(raw_step, dict):
                continue
            agent_name = raw_step.get("agent")
            if not isinstance(agent_name, str) or not agent_name.strip():
                continue
            task = raw_step.get("task", {})
            if not isinstance(task, dict):
                task = {"input": task}
            clean_steps.append({"agent": agent_name, "task": task})

        normalized["steps"] = clean_steps
        return normalized

    async def run(self, instruction: str) -> dict[str, Any]:
        context = (await self.memory.load("context")) or {}
        raw_plan = await self._plan(instruction, context)
        plan = self._normalize_plan(raw_plan)
        context.update(plan.get("updated_context", {}))

        execution_log: list[dict[str, Any]] = []
        for step in plan["steps"]:
            agent = self.registry.get(step["agent"])
            if not agent:
                execution_log.append({"step": step, "error": "Agent not found"})
                continue
            try:
                result = await agent.run(step.get("task", {}), context)
                execution_log.append({"step": step, "result": result})
                context[f"result_{agent.name}"] = result
            except Exception as exc:  # pragma: no cover - runtime safety branch
                execution_log.append({"step": step, "error": f"{type(exc).__name__}: {exc}"})

        await self.memory.save("context", context)
        return {"instruction": instruction, "plan": plan, "execution_log": execution_log, "context": context}
