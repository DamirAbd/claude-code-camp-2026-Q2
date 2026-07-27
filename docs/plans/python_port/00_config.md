# Port Plan: 00_config — Ruby → Python

Port the `week1_baseline/ruby/00_config` configuration module to Python,
producing an equivalent `week1_baseline/python/00_config` that passes the same
smoke-test and produces identical output.

---

## Source files to port

| Ruby source | Purpose |
|---|---|
| `week1_baseline/ruby/00_config/lib/boukensha.rb` | Top-level require/entry point |
| `week1_baseline/ruby/00_config/lib/boukensha/config.rb` | `Boukensha::Config` class |
| `week1_baseline/ruby/00_config/lib/boukensha/tasks/base.rb` | Abstract `Boukensha::Tasks::Base` |
| `week1_baseline/ruby/00_config/lib/boukensha/tasks/player.rb` | Concrete `Boukensha::Tasks::Player` |
| `week1_baseline/ruby/00_config/prompts/system.md` | Default system prompt (copy verbatim) |
| `week1_baseline/ruby/00_config/examples/example.rb` | Smoke-test script |
| `week1_baseline/ruby/00_config/Gemfile` | Dependencies → `pyproject.toml` |
| `week1_baseline/bin/00_config` (bash) | Runner script — new Python equivalent needed |

---

## Target layout

```
week1_baseline/python/00_config/
  pyproject.toml               # dependencies (python-dotenv, PyYAML)
  boukensha/
    __init__.py                # re-exports Config + Tasks (mirrors lib/boukensha.rb)
    config.py                  # Config class (mirrors config.rb)
    tasks/
      __init__.py
      base.py                  # TaskBase (mirrors tasks/base.rb)
      player.py                # Player(TaskBase) (mirrors tasks/player.rb)
  prompts/
    system.md                  # copied verbatim from ruby/00_config/prompts/system.md
  examples/
    example.py                 # smoke-test (mirrors examples/example.rb)
```

Runner script (mirrors `week1_baseline/bin/00_config`):
```
week1_baseline/bin/00_config_py   # bash wrapper that cds and runs uv run python examples/example.py
```

---

## Dependency mapping

Managed with `uv`. The `pyproject.toml` will declare:
- `requires-python = ">=3.14"`
- `dependencies = ["python-dotenv", "PyYAML"]`

Run `uv sync` to install. The runner script uses `uv run python examples/example.py`.

| Ruby gem | Python package | Notes |
|---|---|---|
| `dotenv` | `python-dotenv` | `dotenv.load_dotenv(path)` |
| stdlib `yaml` | `PyYAML` (`yaml.safe_load`) | same API shape |
| stdlib `pathname` | `pathlib.Path` | direct equivalent |

---

## Class / method mapping

### `Config` (`config.rb` → `config.py`)

| Ruby | Python |
|---|---|
| `Boukensha::Config` | `class Config` |
| `DEFAULT_DIR = File.join(Dir.home, ".boukensha")` | `DEFAULT_DIR = Path.home() / ".boukensha"` |
| `PROMPTS_DIR = File.expand_path("../../prompts", __dir__)` | `PROMPTS_DIR = Path(__file__).parent.parent / "prompts"` |
| `attr_reader :dir, :settings` | `self.dir`, `self.settings` as instance attrs |
| `resolve_dir` (private) | `_resolve_dir()` |
| `load_env` (private) | `_load_env()` |
| `load_settings` (private) | `_load_settings()` |
| `tasks(name = nil)` | `tasks(name=None)` — returns dict or sub-dict |
| `dig(*keys)` | `_dig(*keys)` — reduce over nested dict |
| `mud_host`, `mud_port`, etc. | properties `mud_host`, `mud_port`, etc. |
| `to_s` / `inspect` | `__str__` / `__repr__` |

Key behaviour to preserve:
- Config dir resolves from `BOUKENSHA_DIR` env var first, then `~/.boukensha`.
- `_load_env` calls `load_dotenv` on `<dir>/.env` if it exists.
- `_load_settings` reads `<dir>/settings.yaml` with `yaml.safe_load`; returns `{}` if absent.
- `_dig` must handle both string and symbol-style keys — in Python all YAML keys
  are strings, so no symbol lookup is needed (simplification over Ruby).
- `tasks(name)` looks up `all[name]` (string keys only in Python).

### `TaskBase` (`tasks/base.rb` → `tasks/base.py`)

| Ruby | Python |
|---|---|
| `class Base` with class methods | `class TaskBase` with `@classmethod` methods |
| `def self.task_name` → `raise NotImplementedError` | `@classmethod def task_name(cls)` → `raise NotImplementedError` |
| `def self.provider(settings)` | `@classmethod def provider(cls, settings)` |
| `def self.model(settings)` | `@classmethod def model(cls, settings)` |
| `def self.prompt_override?(settings, prompt)` | `@classmethod def prompt_override(cls, settings, prompt="system")` |
| `def self.prompt(settings, name, ...)` | `@classmethod def prompt(cls, settings, name="system", ...)` |
| `def self.system_prompt(settings, ...)` | `@classmethod def system_prompt(cls, settings, ...)` |
| private `fetch(settings, key)` | `@classmethod def _fetch(cls, settings, key)` |
| private `read_user_prompt` | `@classmethod def _read_user_prompt` |
| private `read_default_prompt` | `@classmethod def _read_default_prompt` |
| private `read_file` | `@classmethod def _read_file` |

Key behaviour to preserve:
- `_fetch` returns `settings.get(key)` — Python dicts only have string keys from
  YAML so no symbol fallback needed (simplification).
- `provider` and `model` raise `ValueError` (not `ArgumentError`) if missing.
- `prompt_override` returns `bool` — check `node.get(prompt) is True`.
- `_read_file` returns `None` if path doesn't exist, else `path.read_text().strip()`.

### `Player` (`tasks/player.rb` → `tasks/player.py`)

```python
from .base import TaskBase

class Player(TaskBase):
    @classmethod
    def task_name(cls):
        return "player"
```

### `examples/example.py` (`examples/example.rb` → `examples/example.py`)

Mirror the Ruby example exactly:
- Set `BOUKENSHA_DIR` env var to `../../../.boukensha` relative to the script's
  directory (same three-levels-up logic as the Ruby version).
- Instantiate `Config`, call the same accessors, print the same output lines.
- Check `os.environ.get("ANTHROPIC_API_KEY") is not None`.

---

## Runner script

Create `week1_baseline/bin/00_config_py`:

```bash
#!/usr/bin/env bash
cd "$(dirname "$0")/../python/00_config"
uv run python examples/example.py
```

---

## Decisions

1. ~~**Package manager**~~ → `uv` + `pyproject.toml`. ✓
2. ~~**Python version**~~ → `>=3.14`. ✓
3. ~~**Runner script name**~~ → `week1_baseline/bin/00_config_py` (keeps the Ruby runner intact). ✓
4. ~~**`TaskBase` design**~~ → `@classmethod` on `TaskBase` — mirrors Ruby class methods, easiest to follow side-by-side. ✓
5. ~~**Symbol/string key handling**~~ → Drop the double-lookup; PyYAML always produces string keys. ✓
6. ~~**`__init__.py` exports**~~ → Re-export `Config` and `Player` at the top level (`from boukensha import Config, Player`). ✓
