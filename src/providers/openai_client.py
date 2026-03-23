from __future__ import annotations

from typing import Any

from openai import OpenAI


def build_responses_input(
    system_prompt: str | None, user_prompt: str
) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    if system_prompt:
        payload.append(
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            }
        )
    payload.append(
        {
            "role": "user",
            "content": [{"type": "input_text", "text": user_prompt}],
        }
    )
    return payload


def extract_response_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    output_items = getattr(response, "output", [])
    for item in output_items:
        for content in getattr(item, "content", []):
            text = getattr(content, "text", None)
            if text:
                return text
    raise ValueError("OpenAI response did not contain text output")


class OpenAIAnalysisClient:
    def __init__(self, api_key: str, model: str, timeout: float = 90.0) -> None:
        self.model = model
        self.client = OpenAI(api_key=api_key, timeout=timeout)

    def generate_text(
        self,
        *,
        system_prompt: str | None,
        user_prompt: str,
        temperature: float = 0.2,
        max_output_tokens: int = 4000,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "input": build_responses_input(system_prompt, user_prompt),
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }
        response = self.client.responses.create(**payload)
        return {
            "text": extract_response_text(response),
            "raw": response.model_dump(),
        }
