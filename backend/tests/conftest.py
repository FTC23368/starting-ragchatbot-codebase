import sys
import os
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass

import pytest

# Add backend to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vector_store import SearchResults


@pytest.fixture
def mock_vector_store():
    """Mock VectorStore with default empty search results."""
    store = Mock()
    store.search.return_value = SearchResults(documents=[], metadata=[], distances=[])
    store.get_lesson_link.return_value = None
    return store


@pytest.fixture
def sample_search_results():
    """SearchResults with 2 documents and metadata."""
    return SearchResults(
        documents=["Doc 1 content about APIs", "Doc 2 content about MCP"],
        metadata=[
            {"course_title": "Intro to APIs", "lesson_number": 1, "chunk_index": 0},
            {"course_title": "MCP Course", "lesson_number": 3, "chunk_index": 2},
        ],
        distances=[0.3, 0.5],
    )


@pytest.fixture
def mock_anthropic_response_text():
    """Mock Anthropic response with stop_reason='end_turn' and text content."""
    response = Mock()
    response.stop_reason = "end_turn"
    text_block = Mock()
    text_block.type = "text"
    text_block.text = "This is a direct answer."
    response.content = [text_block]
    return response


@pytest.fixture
def mock_anthropic_response_tool_use():
    """Mock Anthropic response with stop_reason='tool_use' and a search tool call."""
    response = Mock()
    response.stop_reason = "tool_use"

    text_block = Mock()
    text_block.type = "text"
    text_block.text = "Let me search for that."

    tool_block = Mock()
    tool_block.type = "tool_use"
    tool_block.name = "search_course_content"
    tool_block.id = "toolu_123"
    tool_block.input = {"query": "MCP basics"}

    response.content = [text_block, tool_block]
    return response


@pytest.fixture
def mock_anthropic_response_tool_use_outline():
    """Mock Anthropic response with stop_reason='tool_use' and a course outline tool call."""
    response = Mock()
    response.stop_reason = "tool_use"

    text_block = Mock()
    text_block.type = "text"
    text_block.text = "Let me get the course outline."

    tool_block = Mock()
    tool_block.type = "tool_use"
    tool_block.name = "get_course_outline"
    tool_block.id = "toolu_456"
    tool_block.input = {"course_name": "MCP"}

    response.content = [text_block, tool_block]
    return response
