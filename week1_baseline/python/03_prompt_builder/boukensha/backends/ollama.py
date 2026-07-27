from typing import Any

from .base import Base
from ..context import Context
from ..message import Message
from ..tool import Tool


class Ollama(Base):
    MODELS = {
        "gemma4": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:e2b": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:e4b": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:12b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:26b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:31b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "qwen3:30b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "qwen3:8b": {
            "context_window": 40_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "deepseek-r1:8b": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
    }

    def __init__(self, *, model: str, host: str = "http://localhost:11434"):
        self.host = host.rstrip("/")
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
                        "tool_name": message.tool_use_id,
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
            "stream": False,
            "messages": self.to_messages(context.messages, system=context.system),
            "tools": self.to_tools(context.tools),
        }

    @property
    def headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    @property
    def url(self) -> str:
        return f"{self.host}/api/chat"
