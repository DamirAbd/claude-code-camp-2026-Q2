import unittest

from boukensha import Context, Player, Registry, Tool, UnknownToolError


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.context = Context(task=Player)
        self.registry = Registry(self.context)

    def test_tool_constructs_registers_and_returns_tool(self):
        block = lambda direction: direction
        tool = self.registry.tool(
            "move",
            description="Move somewhere",
            parameters={"direction": {"type": "string"}},
            block=block,
        )

        self.assertIsInstance(tool, Tool)
        self.assertIs(self.context.tools["move"], tool)
        self.assertEqual(tool.name, "move")
        self.assertEqual(tool.description, "Move somewhere")
        self.assertEqual(tool.parameters, {"direction": {"type": "string"}})
        self.assertIs(tool.block, block)

    def test_omitted_parameters_are_independent(self):
        first = self.registry.tool("first", description="First", block=lambda: None)
        second = self.registry.tool(
            "second", description="Second", block=lambda: None
        )

        first.parameters["added"] = True

        self.assertEqual(second.parameters, {})
        self.assertIsNot(first.parameters, second.parameters)

    def test_names_are_normalized_to_strings(self):
        tool = self.registry.tool(123, description="Numbered", block=lambda: "ok")

        self.assertEqual(tool.name, "123")
        self.assertEqual(self.registry.dispatch(123), "ok")

    def test_same_name_replaces_previous_tool(self):
        first = self.registry.tool("move", description="First", block=lambda: 1)
        second = self.registry.tool("move", description="Second", block=lambda: 2)

        self.assertIsNot(first, second)
        self.assertIs(self.context.tools["move"], second)
        self.assertEqual(self.registry.dispatch("move"), 2)

    def test_dispatch_forwards_string_keys_as_keyword_arguments(self):
        self.registry.tool(
            "join",
            description="Join values",
            block=lambda left, right: f"{left}:{right}",
        )

        result = self.registry.dispatch("join", {"left": "a", "right": "b"})

        self.assertEqual(result, "a:b")

    def test_dispatch_accepts_omitted_and_empty_arguments(self):
        self.registry.tool("ping", description="Ping", block=lambda: "pong")

        self.assertEqual(self.registry.dispatch("ping"), "pong")
        self.assertEqual(self.registry.dispatch("ping", {}), "pong")

    def test_dispatch_passes_return_value_through(self):
        value = object()
        self.registry.tool("value", description="Value", block=lambda: value)

        self.assertIs(self.registry.dispatch("value"), value)

    def test_missing_tool_raises_domain_error_with_exact_message(self):
        with self.assertRaisesRegex(
            UnknownToolError, r"^No tool registered as 'flee'$"
        ):
            self.registry.dispatch("flee")

    def test_callable_exceptions_propagate_unchanged(self):
        error = RuntimeError("tool failed")

        def fail():
            raise error

        self.registry.tool("fail", description="Fail", block=fail)

        with self.assertRaises(RuntimeError) as raised:
            self.registry.dispatch("fail")

        self.assertIs(raised.exception, error)


if __name__ == "__main__":
    unittest.main()
