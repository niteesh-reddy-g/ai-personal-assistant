from __future__ import annotations

import httpx


class TelegramClient:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

    async def send_message(self, text: str) -> None:
        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram credentials are not configured")
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(url, json={"chat_id": self.chat_id, "text": text})
            resp.raise_for_status()
