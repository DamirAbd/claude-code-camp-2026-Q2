# 00 · Configuration (Python)

Python port of `week1_baseline/ruby/00_config`.

Loads config from `~/.boukensha/settings.yaml`, resolves system prompts, and exposes typed accessors for tasks and MUD connection settings.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Run

From the repo root:

```bash
./week1_baseline/bin/00_config_py
```

Or from this directory:

```bash
uv run python examples/example.py
```

`uv run` automatically creates a virtualenv and installs dependencies on first run.

## Config directory

Resolved in order:

1. `BOUKENSHA_DIR` environment variable
2. `~/.boukensha` (default)

Expected structure:

```
.boukensha/
  .env              # ANTHROPIC_API_KEY and other secrets (never commit)
  settings.yaml     # non-secret settings
  prompts/
    player/
      system.md     # optional system prompt override for the player task
```

Minimal `settings.yaml`:

```yaml
tasks:
  player:
    provider: anthropic
    model: claude-haiku-4-5
    prompt_override:
      system: true   # use .boukensha/prompts/player/system.md if present

mud:
  host: localhost
  port: 4000
  username: dummy
  password: helloworld
```

## Expected output

```
=== Boukensha Step 0: Configuration ===

Config dir:     /home/user/.boukensha
Tasks:          player

-- player task --
Provider:       anthropic
Model:          claude-haiku-4-5
Prompt override?true
System prompt:  You are a MUD player assistant. Use the tools available to y...

MUD host:       localhost:4000
MUD user:       dummy

API key set?    true

#<Boukensha::Config dir=/home/user/.boukensha tasks=player>
```
