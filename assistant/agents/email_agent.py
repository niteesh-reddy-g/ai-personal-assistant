from __future__ import annotations

from typing import Any

from assistant.agents.base_agent import BaseAgent
from assistant.core.llm_client import LLMClient
from assistant.interfaces.notifier import Notifier
from assistant.tools.gmail_tool import GmailTool


class EmailAgent(BaseAgent):
    name = "email_agent"
    description = "Process inbox messages: classify, draft replies, and notify on high priority items"
    capabilities = ["email_triage", "notifications"]

    def __init__(self, gmail_tool: GmailTool, llm: LLMClient, notifier: Notifier, auto_send: bool = False) -> None:
        self.gmail_tool = gmail_tool
        self.llm = llm
        self.notifier = notifier
        self.auto_send = auto_send

    async def run(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        task = task if isinstance(task, dict) else {"input": task}
        labels = task.get("labels", ["HIGH_PRIORITY", "LOW_PRIORITY", "IGNORE"])
        if not isinstance(labels, list):
            labels = ["HIGH_PRIORITY", "LOW_PRIORITY", "IGNORE"]

        emails = self.gmail_tool.fetch_inbox(max_results=task.get("max_results", 10))
        results: list[dict[str, Any]] = []
        for email in emails:
            prompt = (
                "Classify this email and produce optional reply draft. "
                f"Allowed labels: {labels}. "
                "Return JSON with keys label, reason, reply_text.\n"
                f"Email:\n{email}"
            )
            out = await self.llm.generate_json(prompt, '{"label":"","reason":"","reply_text":""}')
            label = out.get("label", "IGNORE")
            if label == "HIGH_PRIORITY":
                await self.notifier.send(f"High priority email from {email['from']}: {email['subject']}")
            elif label == "LOW_PRIORITY" and out.get("reply_text"):
                self.gmail_tool.save_draft_reply(email["from"], email["subject"], out["reply_text"])
            results.append({"email": email, "classification": out})
        return {"agent": self.name, "processed": len(results), "results": results}
