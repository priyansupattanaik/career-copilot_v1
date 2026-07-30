"""
Groq OpenAI-compatible chat client.

Used for dedicated tasks (mock interview questions). This is intentionally
separate from NVIDIA and must NOT be wired as an NVIDIA fallback.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx
from pydantic import ValidationError

from app.config import Settings
from app.errors import ApiError

TRANSIENT_STATUS = {408, 429, 500, 502, 503, 504}
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class GroqClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings
        self.transport = transport

    def capability(self) -> dict[str, Any]:
        return {
            "configured": self.settings.groq_configured,
            "model": self.settings.groq_model or None,
            "provider": "groq",
            "tasks": ["interview_questions"],
        }

    def _strip_json_fence(self, content: str) -> str:
        text = (content or "").strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema_model: type,
        temperature: float | None = None,
    ) -> Any:
        if not self.settings.groq_configured:
            raise ApiError(
                503,
                "groq_not_configured",
                "Groq is not configured. Set GROQ_API_KEY and GROQ_MODEL for interview questions.",
            )
        schema = schema_model.model_json_schema()
        payload = {
            "model": self.settings.groq_model,
            "temperature": self.settings.groq_temperature if temperature is None else temperature,
            "max_tokens": self.settings.groq_max_output_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {"input": user_payload, "output_schema": schema},
                        separators=(",", ":"),
                    ),
                },
            ],
        }
        raw = await self._request(payload)
        try:
            cleaned = self._strip_json_fence(raw)
            return schema_model.model_validate(json.loads(cleaned))
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
            raise ApiError(
                502,
                "invalid_groq_response",
                "Groq returned an invalid structured response.",
            ) from exc

    async def _request(self, payload: dict[str, Any]) -> str:
        headers = {
            "Authorization": f"Bearer {self.settings.groq_api_key}",
            "Content-Type": "application/json",
        }
        timeout = httpx.Timeout(self.settings.groq_timeout_seconds)
        attempts = self.settings.groq_max_retries + 1
        async with httpx.AsyncClient(timeout=timeout, transport=self.transport) as client:
            for attempt in range(attempts):
                try:
                    response = await client.post(
                        f"{self.settings.groq_base_url.rstrip('/')}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    if attempt + 1 < attempts:
                        await asyncio.sleep(min(0.25 * (2**attempt), 1.0))
                        continue
                    raise ApiError(503, "groq_unavailable", "Groq is temporarily unavailable.") from exc
                if response.status_code in TRANSIENT_STATUS and attempt + 1 < attempts:
                    await asyncio.sleep(min(0.25 * (2**attempt), 1.0))
                    continue
                if response.status_code in {401, 403}:
                    raise ApiError(
                        503,
                        "groq_authentication_failed",
                        "Groq API authentication failed. Check GROQ_API_KEY.",
                    )
                if response.status_code == 429:
                    raise ApiError(429, "groq_rate_limited", "Groq rate limit reached. Try again later.")
                if response.status_code >= 500:
                    raise ApiError(503, "groq_unavailable", "Groq is temporarily unavailable.")
                if response.status_code >= 400:
                    raise ApiError(502, "groq_request_rejected", "Groq rejected the request.")
                try:
                    body = response.json()
                    content = body["choices"][0]["message"]["content"]
                except (ValueError, KeyError, IndexError, TypeError) as exc:
                    raise ApiError(
                        502, "groq_response_unreadable", "Groq response could not be read."
                    ) from exc
                if not isinstance(content, str) or not content.strip():
                    raise ApiError(502, "groq_empty_response", "Groq returned an empty response.")
                return content
        raise ApiError(503, "groq_unavailable", "Groq is temporarily unavailable.")
