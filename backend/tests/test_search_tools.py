import sys
import os
from unittest.mock import Mock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from search_tools import CourseSearchTool, ToolManager
from vector_store import SearchResults


# ── CourseSearchTool tests ───────────────────────────────────────────


class TestCourseSearchTool:
    def test_execute_with_results(self, mock_vector_store, sample_search_results):
        mock_vector_store.search.return_value = sample_search_results
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="APIs")

        assert "[Intro to APIs - Lesson 1]" in result
        assert "Doc 1 content about APIs" in result
        assert "[MCP Course - Lesson 3]" in result
        assert "Doc 2 content about MCP" in result

    def test_execute_empty_results(self, mock_vector_store):
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="nonexistent topic")

        assert "No relevant content found" in result

    def test_execute_empty_with_filters(self, mock_vector_store):
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="test", course_name="MCP", lesson_number=5)

        assert "No relevant content found" in result
        assert "MCP" in result
        assert "lesson 5" in result

    def test_execute_with_error(self, mock_vector_store):
        mock_vector_store.search.return_value = SearchResults(
            documents=[], metadata=[], distances=[], error="Search error: connection failed"
        )
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="test")

        assert result == "Search error: connection failed"

    def test_execute_passes_course_filter(self, mock_vector_store):
        tool = CourseSearchTool(mock_vector_store)

        tool.execute(query="test", course_name="MCP")

        mock_vector_store.search.assert_called_once_with(
            query="test", course_name="MCP", lesson_number=None
        )

    def test_execute_passes_lesson_filter(self, mock_vector_store):
        tool = CourseSearchTool(mock_vector_store)

        tool.execute(query="test", lesson_number=3)

        mock_vector_store.search.assert_called_once_with(
            query="test", course_name=None, lesson_number=3
        )

    def test_execute_passes_both_filters(self, mock_vector_store):
        tool = CourseSearchTool(mock_vector_store)

        tool.execute(query="test", course_name="MCP", lesson_number=3)

        mock_vector_store.search.assert_called_once_with(
            query="test", course_name="MCP", lesson_number=3
        )

    def test_sources_tracking(self, mock_vector_store, sample_search_results):
        mock_vector_store.search.return_value = sample_search_results
        tool = CourseSearchTool(mock_vector_store)

        tool.execute(query="APIs")

        assert len(tool.last_sources) == 2
        assert tool.last_sources[0]["text"] == "Intro to APIs - Lesson 1"
        assert "link" in tool.last_sources[0]

    def test_sources_include_lesson_links(self, mock_vector_store, sample_search_results):
        mock_vector_store.search.return_value = sample_search_results
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson1"
        tool = CourseSearchTool(mock_vector_store)

        tool.execute(query="APIs")

        mock_vector_store.get_lesson_link.assert_called()
        assert tool.last_sources[0]["link"] == "https://example.com/lesson1"

    def test_get_tool_definition(self, mock_vector_store):
        tool = CourseSearchTool(mock_vector_store)

        defn = tool.get_tool_definition()

        assert defn["name"] == "search_course_content"
        assert "description" in defn
        assert "input_schema" in defn
        assert "query" in defn["input_schema"]["properties"]


# ── ToolManager tests ────────────────────────────────────────────────


class TestToolManager:
    def _make_mock_tool(self, name="mock_tool", result="mock result"):
        tool = Mock()
        tool.get_tool_definition.return_value = {"name": name, "description": "A mock tool"}
        tool.execute.return_value = result
        return tool

    def test_register_and_execute(self):
        manager = ToolManager()
        tool = self._make_mock_tool("my_tool", "hello")
        manager.register_tool(tool)

        result = manager.execute_tool("my_tool", query="test")

        assert result == "hello"
        tool.execute.assert_called_once_with(query="test")

    def test_execute_unknown_tool(self):
        manager = ToolManager()

        result = manager.execute_tool("nonexistent")

        assert "not found" in result.lower()

    def test_get_tool_definitions(self):
        manager = ToolManager()
        manager.register_tool(self._make_mock_tool("tool_a"))
        manager.register_tool(self._make_mock_tool("tool_b"))

        defs = manager.get_tool_definitions()

        assert len(defs) == 2
        names = {d["name"] for d in defs}
        assert names == {"tool_a", "tool_b"}

    def test_get_last_sources(self):
        manager = ToolManager()
        tool = self._make_mock_tool("search")
        tool.last_sources = [{"text": "Source 1", "link": None}]
        manager.register_tool(tool)

        sources = manager.get_last_sources()

        assert len(sources) == 1
        assert sources[0]["text"] == "Source 1"

    def test_reset_sources(self):
        manager = ToolManager()
        tool = self._make_mock_tool("search")
        tool.last_sources = [{"text": "Source 1", "link": None}]
        manager.register_tool(tool)

        manager.reset_sources()

        assert tool.last_sources == []
