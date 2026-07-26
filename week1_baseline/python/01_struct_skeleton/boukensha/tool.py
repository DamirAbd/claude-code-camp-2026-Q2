from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    block: Callable[..., Any]

    def __str__(self):
        return (
            f"#<Tool name={self.name} description={str(self.description)[:41]} "
            f"params={list(self.parameters.keys())}>"
        )
