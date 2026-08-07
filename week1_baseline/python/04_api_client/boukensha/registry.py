from collections.abc import Callable
from typing import Any

from .context import Context
from .errors import UnknownToolError
from .tool import Tool


class Registry:
    def __init__(self, context: Context):
        self.context = context

    def tool(
        self,
        name: str,
        *,
        description: str,
        block: Callable[..., Any],
        parameters: dict[str, Any] | None = None,
    ) -> Tool:
        tool = Tool(
            str(name),
            description,
            {} if parameters is None else parameters,
            block,
        )
        self.context.register_tool(tool)
        return tool

    def dispatch(self, name: str, args: dict[str, Any] | None = None) -> Any:
        normalized_name = str(name)
        tool = self.context.tools.get(normalized_name)
        if tool is None:
            raise UnknownToolError(f"No tool registered as '{name}'")
        return tool.block(**(args or {}))
