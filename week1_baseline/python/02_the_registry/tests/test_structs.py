import unittest

from boukensha import Context, Message, Player, Tool


def make_tool(name="move"):
    return Tool(
        name,
        "Move the player in a direction (north, south, east, west, up, down)",
        {"direction": {"type": "string"}},
        lambda direction: f"You move {direction}.",
    )


class MessageTest(unittest.TestCase):
    def test_formats_message_without_tool_use_id(self):
        message = Message("user", "Explore north.")

        self.assertEqual(
            str(message),
            "#<Message role=user content=Explore north....>",
        )

    def test_formats_message_with_tool_use_id_and_truncates_content(self):
        message = Message("tool_result", "x" * 70, "toolu_01X")

        self.assertEqual(
            str(message),
            f"#<Message role=tool_result [toolu_01X] content={'x' * 61}...>",
        )


class ToolTest(unittest.TestCase):
    def test_formats_tool_and_retains_callable(self):
        tool = make_tool()

        self.assertEqual(
            str(tool),
            "#<Tool name=move description=Move the player in a direction (north, so "
            "params=['direction']>",
        )
        self.assertEqual(tool.block("north"), "You move north.")


class ContextTest(unittest.TestCase):
    def test_registers_and_replaces_tools_by_name(self):
        context = Context(task=Player)
        first = make_tool()
        replacement = make_tool()

        context.register_tool(first)
        context.register_tool(replacement)

        self.assertEqual(context.tool_count, 1)
        self.assertIs(context.tools["move"], replacement)

    def test_appends_messages_in_order_and_propagates_tool_use_id(self):
        context = Context(task=Player)

        context.add_message("user", "Go north")
        context.add_message(
            "tool_result",
            "You move north.",
            tool_use_id="toolu_01X",
        )

        self.assertEqual(context.turn_count, 2)
        self.assertEqual([message.role for message in context.messages], ["user", "tool_result"])
        self.assertEqual(context.messages[1].tool_use_id, "toolu_01X")
        self.assertEqual(str(context), "#<Context task=player turns=2 tools=0>")


if __name__ == "__main__":
    unittest.main()
