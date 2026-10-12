from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Protocol

from openai import OpenAI

from .config import ProviderConfig
from .errors import ConfigError, ProviderError
from .models import TokenUsage


@dataclass(frozen=True)
class ModelResponse:
    content: str
    returned_model: str | None
    finish_reason: str | None
    usage: TokenUsage = field(default_factory=TokenUsage)


class ModelProvider(Protocol):
    def complete(self, *, system: str, user: str) -> ModelResponse: ...


class DeepSeekProvider:
    def __init__(self, config: ProviderConfig) -> None:
        key = os.environ.get(config.api_key_env, "").strip()
        if not key:
            raise ConfigError(f"Required environment variable is not configured: {config.api_key_env}")
        self.config = config
        self.client = OpenAI(api_key=key, base_url=config.base_url)

    def complete(self, *, system: str, user: str) -> ModelResponse:
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_output_tokens,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except Exception as exc:
            raise ProviderError(str(exc)) from exc
        choice = response.choices[0] if response.choices else None
        usage = response.usage
        details = getattr(usage, "prompt_tokens_details", None) if usage else None
        cached = getattr(details, "cached_tokens", None) if details else None
        return ModelResponse(
            content=(choice.message.content or "") if choice else "",
            returned_model=getattr(response, "model", None),
            finish_reason=getattr(choice, "finish_reason", None),
            usage=TokenUsage(
                input=getattr(usage, "prompt_tokens", None),
                output=getattr(usage, "completion_tokens", None),
                total=getattr(usage, "total_tokens", None),
                cached=cached,
            ),
        )


def parse_json_object(content: str) -> dict:
    text = (content or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"Model returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ProviderError("Model response must be a JSON object")
    return value
