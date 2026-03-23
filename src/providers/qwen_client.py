from __future__ import annotations

from typing import Any

from openai import OpenAI


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def build_chat_messages(
    system_prompt: str | None, user_prompt: str
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    return messages


class QwenChatClient:
    def __init__(
        self, api_key: str, base_url: str, model: str, timeout: float = 90.0
    ) -> None:
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=normalize_base_url(base_url),
            timeout=timeout,
        )

    def generate_text(
        self,
        *,
        system_prompt: str | None,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": build_chat_messages(system_prompt, user_prompt),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        response = self.client.chat.completions.create(**payload)
        choice = response.choices[0]
        text = choice.message.content or ""
        usage = response.usage.model_dump() if response.usage else None
        return {
            "text": text,
            "finish_reason": choice.finish_reason,
            "raw": response.model_dump(),
            "usage": usage,
        }
