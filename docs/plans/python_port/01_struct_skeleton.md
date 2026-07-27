# Port Plan: 01_struct_skeleton — Ruby → Python

Create `week1_baseline/python/01_struct_skeleton` by copying the completed
`week1_baseline/python/00_config` implementation, then port only the changes
introduced by Ruby step `01_struct_skeleton`.

The copied step must remain independently runnable. Do not modify
`week1_baseline/python/00_config`.

---

## Starting point

Copy the entire existing Python step:

```text
week1_baseline/python/00_config/
```

to:

```text
week1_baseline/python/01_struct_skeleton/
```

This carries forward the existing:

- `pyproject.toml` and `uv` dependency setup;
- `Config` implementation;
- `TaskBase` and `Player`;
- package exports and package structure;
- prompt assets;
- example structure.

After copying, change only what is required for Step 1. The Ruby configuration
and task files are unchanged between `00_config` and `01_struct_skeleton`, so
they do not need to be ported again.

---

## New Ruby changes to port

| New Ruby source | Python target | Purpose |
|---|---|---|
| `lib/boukensha/message.rb` | `boukensha/message.py` | Conversation message data structure |
| `lib/boukensha/tool.rb` | `boukensha/tool.py` | Tool definition and callable |
| `lib/boukensha/context.rb` | `boukensha/context.py` | Conversation and tool state |
| additions in `lib/boukensha.rb` | additions in `boukensha/__init__.py` | Export the new public types |
| Step 1 `examples/example.rb` | replace copied `examples/example.py` | Demonstrate the new structures |

Also add a Python runner corresponding to
`week1_baseline/bin/01_struct_skeleton`.

---

## Target layout after the copy and delta

```text
week1_baseline/python/01_struct_skeleton/
  pyproject.toml               # copied unchanged from python/00_config
  boukensha/
    __init__.py                # extend exports with Context, Message, Tool
    config.py                  # copied unchanged
    context.py                 # new
    message.py                 # new
    tool.py                    # new
    tasks/
      __init__.py              # copied unchanged
      base.py                  # copied unchanged
      player.py                # copied unchanged
  prompts/
    system.md                  # copied unchanged
  examples/
    example.py                 # replace with the Step 1 example
```

Runner:

```text
week1_baseline/bin/01_struct_skeleton_py
```

---

## New data structures

### `Message`

Port `Boukensha::Message` as a standard-library dataclass:

```python
@dataclass
class Message:
    role: str
    content: Any
    tool_use_id: str | None = None
```

Implement `__str__` with the Ruby behavior:

- Add ` [<tool_use_id>]` only when the ID is present.
- Convert `content` to a string.
- Include the first 61 characters, matching Ruby's inclusive `[0..60]`.
- Always append `...`.

Example:

```text
#<Message role=user content=Explore north and tell me what you find....>
```

### `Tool`

Port `Boukensha::Tool` as a dataclass:

```python
@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    block: Callable[..., Any]
```

Implement `__str__` with the Ruby behavior:

- Include the first 41 description characters, matching `[0..40]`.
- Display the parameter names in insertion order.
- Use Python string-list notation, such as `params=['direction']`, as the
  equivalent of Ruby's `params=[:direction]`.

Keep the field name `block` so later steps can invoke the stored callable
without another API change.

### `Context`

Port `Boukensha::Context` as a regular class:

```python
class Context:
    def __init__(self, *, task: type[TaskBase], system: str | None = None):
        self.task = task
        self.system = system
        self.messages: list[Message] = []
        self.tools: dict[str, Tool] = {}
```

Implement:

| Ruby | Python |
|---|---|
| `register_tool(tool)` | `register_tool(tool: Tool) -> None` |
| `add_message(role, content, tool_use_id: nil)` | `add_message(role, content, *, tool_use_id=None) -> None` |
| `tool_count` | read-only property returning `len(self.tools)` |
| `turn_count` | read-only property returning `len(self.messages)` |
| `to_s` | `__str__` |

Preserve these behaviors:

- Tools are stored by name.
- Registering the same name replaces the previous tool.
- Messages are appended in order as `Message` instances.
- The context label comes from `task.task_name()`.
- String output is `#<Context task=player turns=2 tools=1>`.

Do not implement the token-budget examples mentioned in the README; that
behavior is not present in the Step 1 Ruby source.

---

## Package exports

Extend the copied `boukensha/__init__.py` so the public API is:

```python
from boukensha import Config, Context, Message, Player, Tool
```

Keep the existing `Config` and `Player` exports and add the three new types to
`__all__`.

---

## Replace the copied example

Replace `examples/example.py` with a behavioral translation of the Step 1 Ruby
example:

1. Preserve the copied Python example's early `BOUKENSHA_DIR` setup.
2. Instantiate `Config` and get the player task settings.
3. Resolve the player system prompt using `config.user_prompts_dir`.
4. Create `Context(task=Player, system=system_prompt)`.
5. Register the `move` tool with the same description, schema, and callable.
6. Add the same user and assistant messages.
7. Print the Step 1 heading, config, context, tool, and messages.

Expected output:

```text
=== Boukensha Step 1: Struct Skeleton ===

Config:   #<Boukensha::Config dir=.../.boukensha tasks=player>
Context:  #<Context task=player turns=2 tools=1>
Tool:     #<Tool name=move description=Move the player in a direction (north, so params=['direction']>
Messages:
  #<Message role=user content=Explore north and tell me what you find....>
  #<Message role=assistant content=Sure, let me head north and take a look....>
```

Python's parameter-key formatting is the only intentional output difference
from Ruby's symbol notation.

---

## Runner

Create `week1_baseline/bin/01_struct_skeleton_py`:

```bash
#!/usr/bin/env bash

cd "$(dirname "$0")/../python/01_struct_skeleton"
uv run python examples/example.py
```

Mark it executable and leave both the Ruby runner and the Step 0 Python runner
unchanged.

---

## Verification

1. Confirm the copied configuration/task files match
   `week1_baseline/python/00_config`.
2. Run the existing Step 0 Python example to ensure the source step remains
   unchanged.
3. Run the Ruby Step 1 baseline:
   `week1_baseline/bin/01_struct_skeleton`.
4. Run the new Python Step 1 example:
   `week1_baseline/bin/01_struct_skeleton_py`.
5. Compare both outputs, allowing only Python's parameter-key representation
   and environment-dependent absolute paths.
6. Add focused `unittest` coverage for:
   - message formatting with and without `tool_use_id`;
   - tool formatting and callable invocation;
   - tool registration and same-name replacement;
   - message ordering and `tool_use_id` propagation;
   - context counts and formatting.
7. Run tests with `uv run python -m unittest discover`.

---

## Decisions

1. **Port strategy** → Copy `python/00_config` in full, then implement only the
   Step 1 delta. ✓
2. **Unchanged code** → Do not re-port or redesign `Config`, `TaskBase`, or
   `Player`. ✓
3. **Struct representation** → Use dataclasses for `Message` and `Tool`, and a
   regular class for mutable `Context`. ✓
4. **Callable field** → Preserve the Ruby name `block`. ✓
5. **Counts** → Use read-only properties for `tool_count` and `turn_count`. ✓
6. **Scope** → Port implemented Ruby behavior only; defer token-budget
   behavior. ✓
7. **Runner** → Add `01_struct_skeleton_py` without changing existing
   runners. ✓
