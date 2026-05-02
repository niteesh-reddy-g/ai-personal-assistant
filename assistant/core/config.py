from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class AppConfig:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    sqlite_path: str = os.getenv("SQLITE_PATH", "assistant_memory.db")
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    gmail_credentials_file: str = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
    gmail_token_file: str = os.getenv("GMAIL_TOKEN_FILE", "token.json")
    email_auto_send: bool = os.getenv("EMAIL_AUTO_SEND", "false").lower() == "true"


def get_config(**overrides: object) -> AppConfig:
    base = AppConfig()
    for key, value in overrides.items():
        if hasattr(base, key):
            setattr(base, key, value)
    return base
