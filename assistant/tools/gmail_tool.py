from __future__ import annotations

from email.header import decode_header
from typing import Any

from assistant.integrations.gmail import GmailClient


class GmailTool:
    def __init__(self, client: GmailClient) -> None:
        self.client = client

    @staticmethod
    def _header(headers: list[dict[str, str]], name: str) -> str:
        for h in headers:
            if h.get("name", "").lower() == name.lower():
                raw = h.get("value", "")
                parts = decode_header(raw)
                return "".join((p.decode(enc or "utf-8") if isinstance(p, bytes) else p) for p, enc in parts)
        return ""

    def fetch_inbox(self, max_results: int = 10) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for msg in self.client.list_messages("in:inbox", max_results=max_results):
            full = self.client.get_message(msg["id"])
            headers = full.get("payload", {}).get("headers", [])
            out.append(
                {
                    "id": msg["id"],
                    "subject": self._header(headers, "Subject"),
                    "from": self._header(headers, "From"),
                    "snippet": full.get("snippet", ""),
                }
            )
        return out

    def save_draft_reply(self, to: str, subject: str, body: str) -> dict[str, Any]:
        return self.client.create_draft(to, subject, body)
