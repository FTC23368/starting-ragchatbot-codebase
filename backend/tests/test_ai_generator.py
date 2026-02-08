import sys
import os
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_generator import AIGenerator


@pytest.fixture
def generator():
    """Create an AIGenerator with a mocked Anthropic client."""
    gen = AIGenerator(api_key="test-key", model="test-model")
    gen.client = Mock()
    return gen


@pytest.fixture
def tool_definitions():
    return [{"name": "search_course_content", "description": "Search", "input_schema": {}}]


class TestAIGenerator:
    def test_direct_response_no_tools(self, generator, mock_anthropic_response_text):
        generator.client.messages.create.return_value = mock_anthropic_response_text

        result = generator.generate_response(query="What is Python?")

        assert result == "This is a direct answer."

    def test_direct_response_with_tools_no_use(
        self, generator, tool_definitions, mock_anthropic_response_text
    ):
        generator.client.messages.create.return_value = mock_anthropic_response_text

        result = generator.generate_response(
            query="What is Python?", tools=tool_definitions
        )

        assert result == "This is a direct answer."

    def test_tool_use_calls_tool_manager(
        self, generator, tool_definitions, mock_anthropic_response_tool_use
    ):
        # First call returns tool use, second call returns text
        final_response = Mock()
        final_response.stop_reason = "end_turn"
        final_response.content = [Mock(type="text", text="Final answer")]
        generator.client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            final_response,
        ]

        tool_manager = Mock()
        tool_manager.execute_tool.return_value = "Search results here"

        generator.generate_response(
            query="Search MCP", tools=tool_definitions, tool_manager=tool_manager
        )

        tool_manager.execute_tool.assert_called_once_with(
            "search_course_content", query="MCP basics"
        )

    def test_tool_use_sends_results_back(
        self, generator, tool_definitions, mock_anthropic_response_tool_use
    ):
        final_response = Mock()
        final_response.stop_reason = "end_turn"
        final_response.content = [Mock(type="text", text="Final answer")]
        generator.client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            final_response,
        ]

        tool_manager = Mock()
        tool_manager.execute_tool.return_value = "Search results here"

        generator.generate_response(
            query="Search MCP", tools=tool_definitions, tool_manager=tool_manager
        )

        # Check the second API call
        second_call_kwargs = generator.client.messages.create.call_args_list[1][1]
        messages = second_call_kwargs["messages"]

        # Should have: user msg, assistant tool_use msg, user tool_result msg
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"

        # The tool result content
        tool_result_content = messages[2]["content"]
        assert tool_result_content[0]["type"] == "tool_result"
        assert tool_result_content[0]["tool_use_id"] == "toolu_123"
        assert tool_result_content[0]["content"] == "Search results here"

    def test_tool_use_followup_includes_tools(
        self, generator, tool_definitions, mock_anthropic_response_tool_use
    ):
        final_response = Mock()
        final_response.stop_reason = "end_turn"
        final_response.content = [Mock(type="text", text="Final answer")]
        generator.client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            final_response,
        ]

        tool_manager = Mock()
        tool_manager.execute_tool.return_value = "results"

        generator.generate_response(
            query="Search MCP", tools=tool_definitions, tool_manager=tool_manager
        )

        second_call_kwargs = generator.client.messages.create.call_args_list[1][1]
        assert second_call_kwargs["tools"] == tool_definitions
        assert second_call_kwargs["tool_choice"] == {"type": "auto"}

    def test_tool_use_returns_final_response(
        self, generator, tool_definitions, mock_anthropic_response_tool_use
    ):
        final_response = Mock()
        final_response.stop_reason = "end_turn"
        final_response.content = [Mock(type="text", text="The final answer")]
        generator.client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            final_response,
        ]

        tool_manager = Mock()
        tool_manager.execute_tool.return_value = "results"

        result = generator.generate_response(
            query="Search MCP", tools=tool_definitions, tool_manager=tool_manager
        )

        assert result == "The final answer"

    def test_conversation_history_in_system(self, generator, mock_anthropic_response_text):
        generator.client.messages.create.return_value = mock_anthropic_response_text

        generator.generate_response(
            query="Follow up question", conversation_history="User: Hi\nAI: Hello"
        )

        call_kwargs = generator.client.messages.create.call_args[1]
        assert "Previous conversation:" in call_kwargs["system"]
        assert "User: Hi" in call_kwargs["system"]

    def test_no_history_system_prompt(self, generator, mock_anthropic_response_text):
        generator.client.messages.create.return_value = mock_anthropic_response_text

        generator.generate_response(query="Hello")

        call_kwargs = generator.client.messages.create.call_args[1]
        assert "Previous conversation:" not in call_kwargs["system"]
        assert "AI assistant" in call_kwargs["system"]

    def test_tools_and_tool_choice_in_params(
        self, generator, tool_definitions, mock_anthropic_response_text
    ):
        generator.client.messages.create.return_value = mock_anthropic_response_text

        generator.generate_response(query="Hello", tools=tool_definitions)

        call_kwargs = generator.client.messages.create.call_args[1]
        assert call_kwargs["tools"] == tool_definitions
        assert call_kwargs["tool_choice"] == {"type": "auto"}

    def test_two_sequential_tool_calls(
        self,
        generator,
        tool_definitions,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_tool_use_outline,
    ):
        """Claude makes two tool calls in separate rounds, then returns text."""
        final_response = Mock()
        final_response.stop_reason = "end_turn"
        final_response.content = [Mock(type="text", text="Combined answer")]
        generator.client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,          # initial: search tool
            mock_anthropic_response_tool_use_outline,  # round 1: outline tool
            final_response,                            # round 2: text
        ]

        tool_manager = Mock()
        tool_manager.execute_tool.side_effect = ["Search results", "Outline results"]

        result = generator.generate_response(
            query="Compare MCP with outline",
            tools=tool_definitions,
            tool_manager=tool_manager,
        )

        assert result == "Combined answer"
        assert generator.client.messages.create.call_count == 3
        assert tool_manager.execute_tool.call_count == 2
        tool_manager.execute_tool.assert_any_call("search_course_content", query="MCP basics")
        tool_manager.execute_tool.assert_any_call("get_course_outline", course_name="MCP")

    def test_two_sequential_tool_calls_message_accumulation(
        self,
        generator,
        tool_definitions,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_tool_use_outline,
    ):
        """Verify messages accumulate correctly across two tool rounds."""
        final_response = Mock()
        final_response.stop_reason = "end_turn"
        final_response.content = [Mock(type="text", text="Done")]
        generator.client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            mock_anthropic_response_tool_use_outline,
            final_response,
        ]

        tool_manager = Mock()
        tool_manager.execute_tool.side_effect = ["Result 1", "Result 2"]

        generator.generate_response(
            query="Multi-step", tools=tool_definitions, tool_manager=tool_manager
        )

        # Third API call should have 5 messages:
        # user, assistant(tool1), user(result1), assistant(tool2), user(result2)
        third_call_kwargs = generator.client.messages.create.call_args_list[2][1]
        messages = third_call_kwargs["messages"]
        assert len(messages) == 5
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"
        assert messages[3]["role"] == "assistant"
        assert messages[4]["role"] == "user"

        # Verify tool results
        assert messages[2]["content"][0]["tool_use_id"] == "toolu_123"
        assert messages[2]["content"][0]["content"] == "Result 1"
        assert messages[4]["content"][0]["tool_use_id"] == "toolu_456"
        assert messages[4]["content"][0]["content"] == "Result 2"

    def test_max_rounds_stops_tool_calls(
        self, generator, tool_definitions, mock_anthropic_response_tool_use
    ):
        """After MAX_TOOL_ROUNDS, stop even if Claude keeps requesting tools."""
        # Create a third tool_use response for the case where Claude won't stop
        third_tool_response = Mock()
        third_tool_response.stop_reason = "tool_use"
        text_block = Mock(type="text", text="Still need more info")
        tool_block = Mock()
        tool_block.type = "tool_use"
        tool_block.name = "search_course_content"
        tool_block.id = "toolu_789"
        tool_block.input = {"query": "more stuff"}
        third_tool_response.content = [text_block, tool_block]

        # All 3 calls return tool_use (but only 2 rounds execute in the handler)
        generator.client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,   # initial call
            mock_anthropic_response_tool_use,    # round 1
            third_tool_response,                 # round 2 (loop ends here)
        ]

        tool_manager = Mock()
        tool_manager.execute_tool.return_value = "results"

        result = generator.generate_response(
            query="Complex query", tools=tool_definitions, tool_manager=tool_manager
        )

        # 3 API calls total: initial + 2 rounds in handler
        assert generator.client.messages.create.call_count == 3
        # Text extracted from last response's text block
        assert result == "Still need more info"

    def test_tool_execution_error_sent_as_result(
        self, generator, tool_definitions, mock_anthropic_response_tool_use
    ):
        """Tool execution errors are sent back to Claude as tool_result content."""
        final_response = Mock()
        final_response.stop_reason = "end_turn"
        final_response.content = [Mock(type="text", text="Sorry, I encountered an error")]
        generator.client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            final_response,
        ]

        tool_manager = Mock()
        tool_manager.execute_tool.side_effect = RuntimeError("Connection failed")

        result = generator.generate_response(
            query="Search MCP", tools=tool_definitions, tool_manager=tool_manager
        )

        assert result == "Sorry, I encountered an error"

        # Verify error was sent as tool_result
        second_call_kwargs = generator.client.messages.create.call_args_list[1][1]
        tool_result = second_call_kwargs["messages"][2]["content"][0]
        assert tool_result["type"] == "tool_result"
        assert "Error executing tool" in tool_result["content"]
        assert "Connection failed" in tool_result["content"]
