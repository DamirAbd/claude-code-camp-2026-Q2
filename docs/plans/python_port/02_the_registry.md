# Port Plan: 02_the_registry — Ruby → Python

Complete the existing `week1_baseline/python/02_the_registry` directory by
porting only the changes introduced in
`week1_baseline/ruby/02_the_registry`.

The Python directory is already a copy of
`week1_baseline/python/01_struct_skeleton`. Keep the working Step 1
implementation intact and add the registry-specific delta. Do not recopy the
directory or modify either earlier Python step.

---

## Current state

The following Step 1 functionality is already present in the Python Step 2
directory and should remain unchanged:

- `Config`, `TaskBase`, and `Player`;
- `Message`, `Tool`, and `Context`;
- the `uv` project and dependencies;
- prompt assets;
- the existing struct tests.

The Ruby comparison shows that Step 2 adds two library files, two top-level
exports, a new example, and a new runner. There are no changes to the Ruby
implementations of `Config`, `Context`, `Message`, `Tool`, or the task
classes.

---

## Missing Ruby changes to port

| Ruby change | Python target | Purpose |
|---|---|---|
| `lib/boukensha/errors.rb` | `boukensha/errors.py` | Define the domain-specific unknown-tool error |
| `lib/boukensha/registry.rb` | `boukensha/registry.py` | Register tools on a context and dispatch calls |
| additions in `lib/boukensha.rb` | additions in `boukensha/__init__.py` | Export `Registry` and `UnknownToolError` |
| Step 2 `examples/example.rb` | replace `examples/example.py` | Demonstrate registration, dispatch, and failure handling |
| Step 2 Ruby README | replace the copied Python README | Document the registry step |
| `week1_baseline/bin/02_the_registry` | new `week1_baseline/bin/02_the_registry_py` | Run the Python example |

---

## Target layout

```text
week1_baseline/python/02_the_registry/
  pyproject.toml               # keep unchanged
  boukensha/
    __init__.py                # add Registry and UnknownToolError exports
    config.py                  # keep unchanged
    context.py                 # keep unchanged
    errors.py                  # new
    message.py                 # keep unchanged
    registry.py                # new
    tool.py                    # keep unchanged
    tasks/                     # keep unchanged
  examples/
    example.py                 # replace with Step 2 example
  prompts/                     # keep unchanged
  tests/
    test_structs.py            # keep existing coverage
    test_registry.py           # new registry coverage
```

Runner:

```text
week1_baseline/bin/02_the_registry_py
```

No new dependency is required; the registry uses only existing project types
and Python standard-library behavior.

---

## `UnknownToolError`

Create `boukensha/errors.py`:

```python
class UnknownToolError(Exception):
    pass
```

This is the Python equivalent of the Ruby `StandardError` subclass. It gives
callers a precise error boundary for an unrecognized tool instead of silently
returning `None` or exposing a raw dictionary lookup error.

---

## `Registry`

Create `boukensha/registry.py` with a `Registry` class that holds a reference
to the existing `Context`:

```python
class Registry:
    def __init__(self, context: Context):
        self.context = context
```

### Tool registration

Map Ruby's block-based API:

```ruby
registry.tool("move", description: "...", parameters: {...}) do |direction:|
  ...
end
```

to an explicit Python callable:

```python
registry.tool(
    "move",
    description="...",
    parameters={"direction": {"type": "string"}},
    block=lambda direction: ...,
)
```

Use this signature:

```python
def tool(
    self,
    name: str,
    *,
    description: str,
    block: Callable[..., Any],
    parameters: dict[str, Any] | None = None,
) -> Tool:
```

Behavior to preserve:

- Normalize `name` with `str(name)`.
- Replace `None` parameters with a new empty dictionary; do not use a mutable
  `{}` default.
- Construct the existing `Tool` dataclass.
- Register it through `context.register_tool()` rather than writing directly
  to the context dictionary.
- Return the constructed `Tool`.
- Preserve same-name replacement behavior supplied by `Context`.

### Dispatch

Use this signature:

```python
def dispatch(self, name: str, args: dict[str, Any] | None = None) -> Any:
```

Behavior to preserve:

1. Normalize the lookup name with `str(name)`.
2. Look up the tool in `context.tools`.
3. If absent, raise:

   ```python
   UnknownToolError(f"No tool registered as '{name}'")
   ```

4. Treat omitted arguments as an empty dictionary.
5. Invoke the stored callable with keyword expansion:

   ```python
   tool.block(**args)
   ```

Ruby converts incoming string keys to symbols because Ruby keyword arguments
use symbols. Python JSON/YAML mappings already have string keys suitable for
`**kwargs`, so no equivalent key conversion is necessary. Do not swallow
`TypeError` or other exceptions raised by invalid arguments or by the tool
itself.

---

## Package exports

Extend `boukensha/__init__.py` while retaining all existing exports:

```python
from .errors import UnknownToolError
from .registry import Registry
```

The complete public API should support:

```python
from boukensha import (
    Config,
    Context,
    Message,
    Player,
    Registry,
    Tool,
    UnknownToolError,
)
```

Add the new names to `__all__`.

---

## Replace the copied example

Replace the current Step 1 example with a behavioral translation of
`week1_baseline/ruby/02_the_registry/examples/example.rb`:

1. Keep the early `BOUKENSHA_DIR` setup.
2. Load `Config`, player settings, and the player system prompt.
3. Create `Context(task=Player, system=system_prompt)`.
4. Create `Registry(ctx)`.
5. Register `move` and `shout` through `registry.tool`, not directly through
   the context.
6. Keep the same descriptions and parameter schemas.
7. Implement `shout` with a callable returning `message.upper()`.
8. Print the Step 2 heading, config, context, and both tools.
9. Dispatch `shout` and `move` with string-keyed argument dictionaries and
   print their results.
10. Dispatch the missing `flee` tool, catch `UnknownToolError`, and print the
    same error message as Ruby.

Expected output:

```text
=== BOUKENSHA Step 2: Tool Registry ===

Config:  #<Boukensha::Config dir=.../.boukensha tasks=player>
Context: #<Context task=player turns=0 tools=2>
Tools:
  #<Tool name=move description=Move the player in a direction (north, so params=['direction']>
  #<Tool name=shout description=Shout a message so everyone in the zone c params=['message']>

Dispatching 'shout' with message='dragon spotted'...
Result: DRAGON SPOTTED

Dispatching 'move' with direction='north'...
Result: You move north into a torch-lit corridor.

UnknownToolError caught: No tool registered as 'flee'
```

As in Step 1, Python list notation for parameter keys is the intentional
difference from Ruby symbol notation.

---

## README and runner

Replace the copied Step 1 README with Step 2 documentation covering:

- the registry's registration and dispatch responsibilities;
- `UnknownToolError`;
- the Python callable-based `tool()` API;
- the runner and test commands.

Create `week1_baseline/bin/02_the_registry_py`:

```bash
#!/usr/bin/env bash

cd "$(dirname "$0")/../python/02_the_registry"
uv run python examples/example.py
```

Mark it executable. Keep all existing Ruby and Python runners unchanged.

---

## Tests

Keep `tests/test_structs.py` and add `tests/test_registry.py` using
standard-library `unittest`.

Cover:

- `tool()` constructs, registers, and returns a `Tool`;
- omitted parameters produce an independent empty dictionary for each tool;
- names are normalized to strings;
- same-name registration replaces the previous tool;
- `dispatch()` forwards string-keyed dictionaries as keyword arguments;
- `dispatch()` works with omitted/empty arguments;
- callable return values pass through unchanged;
- a missing tool raises `UnknownToolError` with the exact Ruby message;
- exceptions from a registered callable propagate unchanged.

---

## Verification

1. Confirm unchanged Python files still match
   `week1_baseline/python/01_struct_skeleton`.
2. Run all Python Step 2 tests:

   ```bash
   cd week1_baseline/python/02_the_registry
   uv run python -m unittest discover -v
   ```

3. Run the Ruby baseline:

   ```bash
   ./week1_baseline/bin/02_the_registry
   ```

4. Run the Python example:

   ```bash
   ./week1_baseline/bin/02_the_registry_py
   ```

5. Compare the outputs, allowing only the documented Python parameter-key
   representation and environment-dependent absolute config path.
6. Run `git diff --check`.

---

## Decisions

1. **Port strategy** → Complete the existing Python Step 2 copy and implement
   only the Ruby Step 2 delta. ✓
2. **Unchanged code** → Do not redesign or edit the Step 1 configuration,
   tasks, structs, or context. ✓
3. **Ruby block mapping** → Accept an explicit keyword-only Python `block`
   callable. ✓
4. **Parameters default** → Use `None` and allocate a fresh dictionary to
   avoid shared mutable defaults. ✓
5. **Argument conversion** → Pass string-keyed mappings directly through
   `**args`; Python needs no Ruby-style string-to-symbol conversion. ✓
6. **Error boundary** → Raise the dedicated `UnknownToolError` with the exact
   Ruby message. ✓
7. **Failure behavior** → Allow tool errors and invalid argument errors to
   propagate. ✓
8. **Runner** → Add `02_the_registry_py` without changing existing runners. ✓
