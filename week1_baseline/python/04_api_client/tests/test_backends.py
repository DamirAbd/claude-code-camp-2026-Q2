import json
import unittest

from boukensha import (
    Anthropic,
    Context,
    Gemini,
    Ollama,
    OllamaCloud,
    OpenAI,
    Player,
    Registry,
    UnsupportedModelError,
)
from boukensha.backends import Base


class BackendTestCase(unittest.TestCase):
    def setUp(self):
        self.context = Context(task=Player, system="System prompt")
        registry = Registry(self.context)
        registry.tool(
            "move",
            description="Move somewhere",
            parameters={"direction": {"type": "string"}},
            block=lambda direction: direction,
        )
        self.context.add_message("user", "Go north")
        self.context.add_message("assistant", "I will move.")
        self.context.add_message(
            "tool_result", "Moved north", tool_use_id="call-1"
        )

    def assert_json_payload(self, backend):
        json.dumps(backend.to_payload(self.context))


class BaseBackendTest(unittest.TestCase):
    def test_base_requires_model_table(self):
        with self.assertRaisesRegex(NotImplementedError, "Base must define MODELS"):
            Base.models()

    def test_unknown_model_lists_sorted_supported_models(self):
        with self.assertRaisesRegex(
            UnsupportedModelError,
            r"OpenAI does not support model 'bad'. "
            r"Supported models: gpt-5.4, gpt-5.4-mini, gpt-5.5, gpt-5.6-terra",
        ):
            OpenAI(api_key="key", model="bad")

    def test_paid_model_cost_and_metadata(self):
        backend = Anthropic(api_key="key", model="claude-haiku-4-5")
        self.assertEqual(backend.context_window, 200_000)
        self.assertEqual(backend.usage_unit, "tokens")
        self.assertIsNone(backend.usage_level)
        self.assertEqual(
            backend.estimate_cost(input_tokens=1_000_000, output_tokens=2_000_000),
            11.0,
        )

    def test_local_and_cloud_costs(self):
        local = Ollama(model="gemma4")
        cloud = OllamaCloud(api_key="key", model="minimax-m3:cloud")
        self.assertEqual(
            local.estimate_cost(input_tokens=100, output_tokens=100), 0.0
        )
        self.assertIsNone(
            cloud.estimate_cost(input_tokens=100, output_tokens=100)
        )
        self.assertEqual(cloud.usage_level, "high")
        self.assertEqual(
            cloud.model_metadata["advertised_context_window"], 1_000_000
        )

    def test_every_declared_model_can_initialize(self):
        factories = [
            (Anthropic, lambda cls, model: cls(api_key="key", model=model)),
            (Gemini, lambda cls, model: cls(api_key="key", model=model)),
            (Ollama, lambda cls, model: cls(model=model)),
            (OllamaCloud, lambda cls, model: cls(api_key="key", model=model)),
            (OpenAI, lambda cls, model: cls(api_key="key", model=model)),
        ]
        for backend_class, factory in factories:
            for model, metadata in backend_class.MODELS.items():
                with self.subTest(backend=backend_class.__name__, model=model):
                    backend = factory(backend_class, model)
                    self.assertEqual(backend.model, model)
                    self.assertEqual(backend.model_metadata, metadata)


class AnthropicBackendTest(BackendTestCase):
    def test_serializes_payload_headers_and_url(self):
        backend = Anthropic(api_key="secret", model="claude-haiku-4-5")
        payload = backend.to_payload(self.context, max_output_tokens=77)
        self.assertEqual(payload["system"], "System prompt")
        self.assertEqual(payload["max_tokens"], 77)
        self.assertEqual(
            payload["messages"][-1],
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "call-1",
                        "content": "Moved north",
                    }
                ],
            },
        )
        self.assertIn("input_schema", payload["tools"][0])
        self.assertEqual(payload["tools"][0]["input_schema"]["required"], ["direction"])
        self.assertEqual(
            backend.url, "https://api.anthropic.com/v1/messages"
        )
        self.assertEqual(backend.headers["x-api-key"], "secret")
        self.assert_json_payload(backend)


class OpenAIBackendTest(BackendTestCase):
    def test_serializes_payload_headers_and_url(self):
        backend = OpenAI(api_key="secret", model="gpt-5.4")
        payload = backend.to_payload(self.context, max_output_tokens=88)
        self.assertEqual(
            payload["messages"][0],
            {"role": "system", "content": "System prompt"},
        )
        self.assertEqual(
            payload["messages"][-1],
            {"role": "tool", "tool_call_id": "call-1", "content": "Moved north"},
        )
        self.assertEqual(payload["max_completion_tokens"], 88)
        self.assertEqual(payload["reasoning_effort"], "none")
        self.assertEqual(payload["tools"][0]["type"], "function")
        self.assertEqual(
            backend.headers["Authorization"], "Bearer secret"
        )
        self.assertEqual(
            backend.url, "https://api.openai.com/v1/chat/completions"
        )
        self.assert_json_payload(backend)


class GeminiBackendTest(BackendTestCase):
    def test_serializes_payload_headers_and_url(self):
        backend = Gemini(api_key="secret", model="gemini-2.5-flash")
        payload = backend.to_payload(self.context, max_output_tokens=99)
        self.assertEqual(
            payload["systemInstruction"],
            {"parts": [{"text": "System prompt"}]},
        )
        self.assertEqual(
            payload["contents"][1],
            {"role": "model", "parts": [{"text": "I will move."}]},
        )
        self.assertEqual(
            payload["contents"][-1]["parts"][0]["functionResponse"]["name"],
            "call-1",
        )
        self.assertEqual(payload["generationConfig"]["maxOutputTokens"], 99)
        self.assertIn("functionDeclarations", payload["tools"][0])
        self.assertEqual(
            backend.url,
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.5-flash:generateContent",
        )
        self.assertEqual(backend.headers["x-goog-api-key"], "secret")
        self.assertEqual(backend.to_tools({}), [])
        self.assert_json_payload(backend)


class OllamaBackendTest(BackendTestCase):
    def test_local_ollama_serialization(self):
        backend = Ollama(model="gemma4", host="http://example.test/")
        payload = backend.to_payload(self.context, max_output_tokens=55)
        self.assertEqual(payload["stream"], False)
        self.assertNotIn("max_output_tokens", payload)
        self.assertEqual(
            payload["messages"][-1],
            {"role": "tool", "tool_name": "call-1", "content": "Moved north"},
        )
        self.assertEqual(backend.url, "http://example.test/api/chat")
        self.assertEqual(backend.headers, {"Content-Type": "application/json"})
        self.assert_json_payload(backend)

    def test_cloud_ollama_serialization(self):
        backend = OllamaCloud(api_key="secret", model="gemma4:31b-cloud")
        self.assertEqual(backend.url, "https://ollama.com/api/chat")
        self.assertEqual(
            backend.headers["Authorization"], "Bearer secret"
        )
        self.assert_json_payload(backend)


if __name__ == "__main__":
    unittest.main()
