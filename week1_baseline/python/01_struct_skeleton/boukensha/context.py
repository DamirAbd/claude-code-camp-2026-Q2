from typing import Any

from .message import Message
from .tasks.base import TaskBase
from .tool import Tool


class Context:
    def __init__(self, *, task: type[TaskBase], system: str | None = None):
        self.task = task
        self.system = system
        self.messages: list[Message] = []
        self.tools: dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def add_message(
        self,
        role: str,
        content: Any,
        *,
        tool_use_id: str | None = None,
    ) -> None:
        self.messages.append(Message(role, content, tool_use_id))

    @property
    def tool_count(self):
        return len(self.tools)

    @property
    def turn_count(self):
        return len(self.messages)

    def __str__(self):
        task_name = self.task.task_name() if self.task else None
        return (
            f"#<Context task={task_name} turns={self.turn_count} "
            f"tools={self.tool_count}>"
        )
