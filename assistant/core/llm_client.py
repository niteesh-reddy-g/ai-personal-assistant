from __future__ import annotations

import json
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from assistant.core.config import AppConfig

try:
    from google import genai
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("google-genai is required") from exc


class LLMClient:
    def __init__(self, config: AppConfig) -> None:
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
        self._client = genai.Client(api_key=config.gemini_api_key)
        self._model = config.gemini_model

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    async def generate_json(self, prompt: str, schema_hint: str = "{}") -> dict[str, Any]:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=(
                "Return ONLY valid JSON."
                f"\nSchema hint:\n{schema_hint}\n\nTask:\n{prompt}"
            ),
        )
        text = (response.text or "").strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Model did not return JSON")
        return json.loads(text[start : end + 1])
