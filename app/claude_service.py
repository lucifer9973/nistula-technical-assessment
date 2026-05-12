"""Anthropic Claude integration service."""

import asyncio
import logging
from typing import Any

from anthropic import APIError, APITimeoutError, AsyncAnthropic

from app.config import settings
from app.prompts import build_system_prompt, build_user_prompt
from app.schemas import NormalizedMessage

logger = logging.getLogger(__name__)


class ClaudeService:
    """Reusable async service wrapper for Claude text generation."""

    def __init__(self) -> None:
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key or "missing")
        self._model = settings.anthropic_model
        self._max_tokens = settings.anthropic_max_tokens
        self._timeout_seconds = settings.anthropic_timeout_seconds

    async def generate_reply(
        self,
        normalized_message: NormalizedMessage,
        property_context: str,
    ) -> str:
        """Generate a hospitality-safe drafted reply from Claude."""

        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(normalized_message, property_context)

        try:
            response = await asyncio.wait_for(
                self._client.messages.create(
                    model=self._model,
                    max_tokens=self._max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=0.2,
                ),
                timeout=self._timeout_seconds,
            )
        except TimeoutError as exc:
            logger.exception("Claude request timed out")
            raise RuntimeError("Claude request timeout") from exc
        except APITimeoutError as exc:
            logger.exception("Claude API timeout")
            raise RuntimeError("Claude API timeout") from exc
        except APIError as exc:
            logger.exception("Claude API error")
            raise RuntimeError("Claude API error") from exc
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected Claude failure")
            raise RuntimeError("Unexpected Claude service failure") from exc

        return self._extract_text(response)

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Extract plaintext from Anthropic response content blocks."""

        blocks = getattr(response, "content", None)
        if not blocks:
            return "Thank you for your message. Our team will assist you shortly."

        text_chunks: list[str] = []
        for block in blocks:
            if getattr(block, "type", "") == "text" and getattr(block, "text", ""):
                text_chunks.append(block.text.strip())

        return (
            "\n".join(text_chunks).strip()
            or "Thank you for your message. Our team will assist you shortly."
        )
