from __future__ import annotations

import argparse
import asyncio
import json

from assistant.agents.email_agent import EmailAgent
from assistant.agents.shopping_agent import ShoppingAgent
from assistant.core.agent_registry import AgentRegistry
from assistant.core.config import get_config
from assistant.core.llm_client import LLMClient
from assistant.core.memory import SQLiteMemoryStore
from assistant.core.orchestrator import Orchestrator
from assistant.integrations.gmail import GmailClient
from assistant.integrations.telegram import TelegramClient
from assistant.tools.browser_tool import BrowserTool
from assistant.tools.gmail_tool import GmailTool
from assistant.tools.telegram_tool import TelegramNotifier


async def async_main(instruction: str) -> None:
    config = get_config()
    llm = LLMClient(config)
    memory = SQLiteMemoryStore(config.sqlite_path)

    registry = AgentRegistry()

    telegram_notifier = TelegramNotifier(TelegramClient(config.telegram_bot_token, config.telegram_chat_id))
    gmail_tool = GmailTool(GmailClient(config.gmail_credentials_file, config.gmail_token_file))
    browser_tool = BrowserTool()

    registry.register(EmailAgent(gmail_tool, llm, telegram_notifier, auto_send=config.email_auto_send))
    registry.register(ShoppingAgent(browser_tool))

    orchestrator = Orchestrator(registry, llm, memory)
    result = await orchestrator.run(instruction)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Extensible Gemini-powered AI personal assistant")
    parser.add_argument("instruction", type=str, help='Example: "Check my email and notify important ones"')
    args = parser.parse_args()
    asyncio.run(async_main(args.instruction))


if __name__ == "__main__":
    main()
