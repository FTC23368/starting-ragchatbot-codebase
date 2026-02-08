import sys
import os
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def rag_system():
    """Create a RAGSystem with all dependencies mocked."""
    with patch("rag_system.VectorStore"), \
         patch("rag_system.AIGenerator"), \
         patch("rag_system.DocumentProcessor"), \
         patch("rag_system.SessionManager"), \
         patch("rag_system.ToolManager") as MockToolManager, \
         patch("rag_system.CourseSearchTool"), \
         patch("rag_system.CourseOutlineTool"):

        from rag_system import RAGSystem
        from config import Config

        config = Config()
        rag = RAGSystem(config)

    # Replace with fresh mocks for test control
    rag.ai_generator = Mock()
    rag.ai_generator.generate_response.return_value = "AI response text"
    rag.session_manager = Mock()
    rag.session_manager.get_conversation_history.return_value = "User: hi\nAI: hello"
    rag.tool_manager = Mock()
    rag.tool_manager.get_tool_definitions.return_value = [{"name": "search"}]
    rag.tool_manager.get_last_sources.return_value = [{"text": "Source 1", "link": None}]

    return rag


class TestRAGSystemQuery:
    def test_query_prompt_format(self, rag_system):
        rag_system.query("What is MCP?", session_id="s1")

        call_kwargs = rag_system.ai_generator.generate_response.call_args[1]
        assert "Answer this question about course materials: What is MCP?" in call_kwargs["query"]

    def test_query_passes_tools(self, rag_system):
        rag_system.query("test", session_id="s1")

        call_kwargs = rag_system.ai_generator.generate_response.call_args[1]
        assert call_kwargs["tools"] == [{"name": "search"}]

    def test_query_passes_tool_manager(self, rag_system):
        rag_system.query("test", session_id="s1")

        call_kwargs = rag_system.ai_generator.generate_response.call_args[1]
        assert call_kwargs["tool_manager"] is rag_system.tool_manager

    def test_query_gets_history(self, rag_system):
        rag_system.query("test", session_id="s1")

        rag_system.session_manager.get_conversation_history.assert_called_once_with("s1")
        call_kwargs = rag_system.ai_generator.generate_response.call_args[1]
        assert call_kwargs["conversation_history"] == "User: hi\nAI: hello"

    def test_query_no_session_no_history(self, rag_system):
        rag_system.query("test")

        rag_system.session_manager.get_conversation_history.assert_not_called()
        call_kwargs = rag_system.ai_generator.generate_response.call_args[1]
        assert call_kwargs["conversation_history"] is None

    def test_query_retrieves_sources(self, rag_system):
        _, sources = rag_system.query("test", session_id="s1")

        rag_system.tool_manager.get_last_sources.assert_called_once()
        assert sources == [{"text": "Source 1", "link": None}]

    def test_query_resets_sources(self, rag_system):
        rag_system.query("test", session_id="s1")

        rag_system.tool_manager.reset_sources.assert_called_once()

    def test_query_saves_exchange(self, rag_system):
        rag_system.query("What is MCP?", session_id="s1")

        rag_system.session_manager.add_exchange.assert_called_once_with(
            "s1", "What is MCP?", "AI response text"
        )

    def test_query_no_session_no_save(self, rag_system):
        rag_system.query("test")

        rag_system.session_manager.add_exchange.assert_not_called()

    def test_query_returns_tuple(self, rag_system):
        result = rag_system.query("test", session_id="s1")

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "AI response text"
        assert isinstance(result[1], list)
