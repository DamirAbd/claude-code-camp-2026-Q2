# 02 · The Tool Registry (Python)

Python port of `week1_baseline/ruby/02_the_registry`.

The registry manages the capabilities available to an agent. It registers
tools on a `Context`, looks them up by name, and dispatches calls with keyword
arguments. Dispatching an unregistered name raises `UnknownToolError`.

## API

Python uses an explicit callable in place of Ruby's block:

```python
registry.tool(
    "move",
    description="Move the player north",
    parameters={"direction": {"type": "string"}},
    block=lambda direction: f"You move {direction}.",
)

result = registry.dispatch("move", {"direction": "north"})
```

Registering a name again replaces the existing tool with that name. Exceptions
from tool callables and invalid arguments propagate to the caller.

## Run

From the repository root:

```bash
./week1_baseline/bin/02_the_registry_py
```

Or from this directory:

```bash
uv run python examples/example.py
```

## Test

```bash
uv run python -m unittest discover -v
```
