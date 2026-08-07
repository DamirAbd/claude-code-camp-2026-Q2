from typing import Any

from .base import Base
from ..context import Context
from ..message import Message
from ..tool import Tool


class Gemini(Base):
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    MODELS = {
        "gemini-3.5-flash": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 1.5, "output": 9.0},
            "usage_unit": "tokens",
        },
        "gemini-3.1-flash-lite": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 0.25, "output": 1.5},
            "usage_unit": "tokens",
        },
        "gemini-2.5-pro": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 1.25, "output": 10.0},
            "usage_unit": "tokens",
        },
        "gemini-2.5-flash": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 0.30, "output": 2.50},
            "usage_unit": "tokens",
        },
        "gemini-2.5-flash-lite": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 0.10, "output": 0.40},
            "usage_unit": "tokens",
        },
    }

    def __init__(self, *, api_key: str, model: str):
        self.api_key = api_key
        self._configure_model(model)

    def to_messages(
        self, messages: list[Message], *, system: str | None = None
    ) -> list[dict[str, Any]]:
        result = []
        for message in messages:
            if message.role == "assistant":
                result.append(
                    {"role": "model", "parts": [{"text": message.content}]}
                )
            elif message.role == "tool_result":
                result.append(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": message.tool_use_id,
                                    "response": {"content": message.content},
                                }
                            }
                        ],
                    }
                )
            else:
                result.append(
                    {
                        "role": str(message.role),
                        "parts": [{"text": message.content}],
                    }
                )
        return result

    def to_tools(self, tools: dict[str, Tool]) -> list[dict[str, Any]]:
        if not tools:
            return []
        return [
            {
                "functionDeclarations": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": tool.parameters,
                            "required": [str(key) for key in tool.parameters],
                        },
                    }
                    for tool in tools.values()
                ]
            }
        ]

    def to_payload(
        self, context: Context, *, max_output_tokens: int = 1024
    ) -> dict[str, Any]:
        return {
            "systemInstruction": {"parts": [{"text": context.system}]},
            "contents": self.to_messages(context.messages, system=context.system),
            "tools": self.to_tools(context.tools),
            "generationConfig": {"maxOutputTokens": max_output_tokens},
        }

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

    @property
    def url(self) -> str:
        return f"{self.BASE_URL}/{self.model}:generateContent"
