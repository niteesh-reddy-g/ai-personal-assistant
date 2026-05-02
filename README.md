# Extensible Gemini AI Personal Assistant

## Setup

1. Create venv and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```
2. Configure environment variables in `.env`:
   ```env
   GEMINI_API_KEY=...
   GEMINI_MODEL=gemini-2.5-flash
   SQLITE_PATH=assistant_memory.db
   TELEGRAM_BOT_TOKEN=...
   TELEGRAM_CHAT_ID=...
   GMAIL_CREDENTIALS_FILE=credentials.json
   GMAIL_TOKEN_FILE=token.json
   EMAIL_AUTO_SEND=false
   ```
3. Add Google OAuth desktop app `credentials.json` file.

## Run

```bash
python -m assistant.main "Check my email and notify important ones"
```

```bash
python -m assistant.main "Find cheapest iPhone 17 Pro Max"
```

## Notes

- Agents are modular and registered through `AgentRegistry`.
- Orchestrator uses Gemini to plan multi-agent execution dynamically.
- Tools are separate low-level reusable integrations.
