# The API Client

Step 4 adds `Client`, which takes the payload assembled by `PromptBuilder` and
sends it to the API. One HTTP POST, one response. No tool loop yet — just
proving the round trip works.

## New modules

| Module | Purpose |
|---|---|
| `boukensha.client` | Makes the HTTP request and parses the response |

## Updated modules

| Module | Change |
|---|---|
| `boukensha.errors` | Added `ApiError` for failed HTTP requests |
| `boukensha.backends.openai` | Added the `gpt-5.6-terra` model and `reasoning_effort` on the payload |

## How it works

```text
PromptBuilder
      |
      v
   Client
      |
      v
POST to API endpoint
      |
      v
Raw JSON response
```

## Client

```python
client = Client(builder)
client.call(max_output_tokens=1024)
```

`call` POSTs the payload returned by `builder.to_api_payload(...)` to
`builder.url` with `builder.headers`, and returns the parsed JSON response.

Non-2xx responses and transient network errors (timeouts, connection resets,
SSL errors) are retried up to 3 times with exponential backoff before raising
`ApiError`. Non-retryable HTTP errors (e.g. `400`, `401`) raise `ApiError`
immediately.

## No dependencies

`Client` uses Python's standard `urllib.request` library — no third-party HTTP
package. This mirrors the Ruby step, which uses `net/http` for the same
reason: the HTTP call itself is trivial and should be visible, not hidden
behind a library. SSL verification for `https` endpoints is handled
automatically by `urllib`/`ssl` using the system's trusted certificates.

## Task configuration

Unchanged from step 3. `Client` reads its target and headers from the
`PromptBuilder`, which in turn reads `tasks.player.provider` and
`tasks.player.model` from `.boukensha/settings.yaml`.

## Considerations

**The client raises `ApiError` on failure.** A non-2xx response means
something went wrong — bad API key, malformed payload, server error. BOUKENSHA
surfaces this explicitly rather than returning a confusing `None` or partial
response.

**The response shape differs by backend.** Anthropic returns `content` blocks
with a `stop_reason`; OpenAI returns `choices` with a `finish_reason`. Handling
those differences uniformly is the job of step 5 — the Agent Loop.

## Run

From the repository root:

```sh
./week1_baseline/bin/04_api_client_py
```

This makes a real network request to the configured provider using the
credentials in `.boukensha/.env`.

Run the tests with:

```sh
UV_CACHE_DIR=/tmp/boukensha-uv-cache \
  uv run --project week1_baseline/python/04_api_client \
  python -m unittest discover -v \
  -s week1_baseline/python/04_api_client/tests
```
