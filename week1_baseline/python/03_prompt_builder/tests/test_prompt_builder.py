import unittest

from boukensha import Context, Player, PromptBuilder, Registry


class FakeBackend:
    headers = {"X-Test": "yes"}
    url = "https://example.test"

    def to_messages(self, messages, *, system=None):
        return {"messages": list(messages), "system": system}

    def to_tools(self, tools):
        return list(tools)

    def to_payload(self, context, *, max_output_tokens=1024):
        return {
            "messages": len(context.messages),
            "tools": len(context.tools),
            "max_output_tokens": max_output_tokens,
        }


class PromptBuilderTest(unittest.TestCase):
    def setUp(self):
        self.context = Context(task=Player, system="System")
        self.backend = FakeBackend()
        self.builder = PromptBuilder(self.context, self.backend)

    def test_delegates_messages_tools_headers_and_url(self):
        Registry(self.context).tool(
            "look", description="Look", block=lambda: "room"
        )
        self.context.add_message("user", "Look")

        messages = self.builder.to_messages()
        self.assertEqual(messages["system"], "System")
        self.assertEqual(messages["messages"], self.context.messages)
        self.assertEqual(self.builder.to_tools(), ["look"])
        self.assertEqual(self.builder.headers, {"X-Test": "yes"})
        self.assertEqual(self.builder.url, "https://example.test")

    def test_payload_uses_default_and_custom_output_limit(self):
        self.assertEqual(
            self.builder.to_api_payload()["max_output_tokens"], 1024
        )
        self.assertEqual(
            self.builder.to_api_payload(max_output_tokens=42)[
                "max_output_tokens"
            ],
            42,
        )

    def test_builder_reflects_later_context_changes(self):
        self.assertEqual(self.builder.to_api_payload()["messages"], 0)
        self.context.add_message("user", "New message")
        self.assertEqual(self.builder.to_api_payload()["messages"], 1)


if __name__ == "__main__":
    unittest.main()
