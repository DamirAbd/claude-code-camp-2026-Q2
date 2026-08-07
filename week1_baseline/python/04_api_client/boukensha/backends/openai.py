from typing import Any

from .base import Base
from ..context import Context
from ..message import Message
from ..tool import Tool


class OpenAI(Base):
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    MODELS = {
        "gpt-5.5": {
            "context_window": 1_000_000,
            "cost_per_million": {"input": 5.0, "output": 30.0},
            "usage_unit": "tokens",
        },
        "gpt-5.4": {
            "context_window": 1_000_000,
            "cost_per_million": {"input": 2.5, "output": 15.0},
            "usage_unit": "tokens",
        },
        "gpt-5.4-mini": {
            "context_window": 400_000,
            "cost_per_million": {"input": 0.75, "output": 4.5},
            "usage_unit": "tokens",
        },
        "gpt-5.6-terra": {
            "context_window": 400_000,
            "cost_per_million": {"input": 2.5, "output": 15},
            "usage_unit": "tokens",
        },
    }

    def __init__(self, *, api_key: str, model: str):
        self.api_key = api_key
        self._configure_model(model)

    def to_messages(
        self, messages: list[Message], *, system: str | None = None
    ) -> list[dict[str, Any]]:
        result = [{"role": "system", "content": system}]
        for message in messages:
            if message.role == "tool_result":
                result.append(
                    {
                        "role": "tool",
                        "tool_call_id": message.tool_use_id,
                        "content": message.content,
                    }
                )
            else:
                result.append({"role": str(message.role), "content": message.content})
        return result

    def to_tools(self, tools: dict[str, Tool]) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.parameters,
                        "required": [str(key) for key in tool.parameters],
                    },
                },
            }
            for tool in tools.values()
        ]

    def to_payload(
        self, context: Context, *, max_output_tokens: int = 1024
    ) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": self.to_messages(context.messages, system=context.system),
            "tools": self.to_tools(context.tools),
            "max_completion_tokens": max_output_tokens,
            "reasoning_effort": "none",
        }

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @property
    def url(self) -> str:
        return self.BASE_URL
