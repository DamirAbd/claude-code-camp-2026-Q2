# The Prompt Builder

Step 3 adds provider-specific serialization to the Python BOUKENSHA baseline.
`PromptBuilder` turns the current `Context` into the messages, tool schemas,
headers, URL, and request payload expected by a selected LLM provider.

This step does not call any API. Its output consists only of JSON-serializable
Python dictionaries and lists that a later HTTP layer can send.

## New modules

| Module | Purpose |
|---|---|
| `boukensha.prompt_builder` | Provider-independent facade over the active backend |
| `boukensha.backends.base` | Model validation, metadata, and cost estimation |
| `boukensha.backends.anthropic` | Anthropic Messages API serialization |
| `boukensha.backends.openai` | OpenAI Chat Completions serialization |
| `boukensha.backends.gemini` | Gemini `generateContent` serialization |
| `boukensha.backends.ollama` | Local Ollama chat serialization |
| `boukensha.backends.ollama_cloud` | Hosted Ollama serialization |

The registry, task configuration, messages, tools, and context from earlier
steps remain the source objects:

```text
Context
   ↓
PromptBuilder
   ↓
Selected backend
   ↓
API payload (dict/list)
```

## PromptBuilder

```python
builder = PromptBuilder(context, backend)

builder.to_messages()
builder.to_tools()
builder.to_api_payload(max_output_tokens=1024)
builder.headers
builder.url
```

The builder keeps references to the context and backend. It does not cache, so
messages and tools added after construction appear in subsequent payloads.

## Provider differences

- Anthropic puts `system` at payload level, uses `input_schema` for tools, and
  wraps tool results in a user message.
- OpenAI puts the system prompt in the message list, wraps tools as
  `type: function`, and identifies tool results with `tool_call_id`.
- Gemini uses `systemInstruction`, calls assistant messages `model`, groups
  tools under `functionDeclarations`, and uses `functionResponse`.
- Ollama and Ollama Cloud put the system prompt in the message list, use the
  function tool envelope, and identify results with `tool_name`.

All parameter keys are marked as required, matching the Ruby tutorial step.
Tool callables stay inside BOUKENSHA and are never included in a payload.

## Model metadata

Each backend owns a static `MODELS` table copied from the Ruby Step 3 source.
Unknown models raise `UnsupportedModelError` at construction time.

Backend instances expose:

- `model` and `model_metadata`;
- `context_window`;
- input and output token cost per million;
- `usage_unit` and optional `usage_level`;
- `estimate_cost(input_tokens=..., output_tokens=...)`.

Local Ollama has zero token API cost. Ollama Cloud uses plan-based usage with
unknown token prices, so its cost estimate is `None`. These values are tutorial
data current as of June 16, 2026, not live provider pricing.

## Configuration and prompts

The example reads `tasks.player.provider` and `tasks.player.model` from
`.boukensha/settings.yaml`. Supported provider values are:

- `anthropic` (`ANTHROPIC_API_KEY`);
- `openai` (`OPENAI_API_KEY`);
- `gemini` (`GEMINI_API_KEY`);
- `ollama_cloud` (`OLLAMA_API_KEY`);
- `ollama` (no key).

The player task first checks its configured user prompt override and otherwise
loads the packaged `prompts/system.md`.

## Run

From the repository root:

```sh
./week1_baseline/bin/03_prompt_builder_py
```

The command prints provider, model, and the formatted JSON payload. It makes no
network request.

Run the tests with:

```sh
UV_CACHE_DIR=/tmp/boukensha-uv-cache \
  uv run --project week1_baseline/python/03_prompt_builder \
  python -m unittest discover -v \
  -s week1_baseline/python/03_prompt_builder/tests
```
