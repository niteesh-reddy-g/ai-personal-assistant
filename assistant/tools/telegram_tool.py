from __future__ import annotations

from assistant.integrations.telegram import TelegramClient
from assistant.interfaces.notifier import Notifier


class TelegramNotifier(Notifier):
    def __init__(self, client: TelegramClient) -> None:
        self.client = client

    async def send(self, message: str) -> None:
        await self.client.send_message(message)
