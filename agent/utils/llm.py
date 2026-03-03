"""LLM integration utilities for agent reasoning and synthesis."""

from __future__ import annotations

import json
from typing import Any

import httpx

from agent.config import LLMConfig
from agent.utils.logging import get_logger
from agent.utils.retry import retry_async

logger = get_logger(__name__)


class LLMClient:
    """Thin async wrapper around Anthropic / OpenAI chat completions."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._client = httpx.AsyncClient(timeout=120.0)

    async def complete(self, system: str, prompt: str, max_tokens: int | None = None) -> str:
        """Send a completion request and return the text response."""
        max_tokens = max_tokens or self.config.max_tokens

        if self.config.provider == "anthropic":
            return await self._anthropic_complete(system, prompt, max_tokens)
        return await self._openai_complete(system, prompt, max_tokens)

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError, httpx.TimeoutException))
    async def _anthropic_complete(self, system: str, prompt: str, max_tokens: int) -> str:
        resp = await self._client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.config.model,
                "max_tokens": max_tokens,
                "temperature": self.config.temperature,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError, httpx.TimeoutException))
    async def _openai_complete(self, system: str, prompt: str, max_tokens: int) -> str:
        resp = await self._client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.model,
                "max_tokens": max_tokens,
                "temperature": self.config.temperature,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def extract_json(self, system: str, prompt: str) -> Any:
        """Request a JSON response and parse it."""
        full_system = system + "\n\nYou MUST respond with valid JSON only. No markdown, no extra text."
        raw = await self.complete(full_system, prompt)
        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        return json.loads(cleaned)

    async def close(self) -> None:
        await self._client.aclose()
