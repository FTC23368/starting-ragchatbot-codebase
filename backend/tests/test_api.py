"""
API endpoint tests for the FastAPI application.

Defines API routes inline using a test app to avoid import issues
with static file mounts that reference non-existent directories.
"""

from unittest.mock import Mock, patch, MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import List, Optional


# ── Test app (mirrors backend/app.py routes without static file mount) ──


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    session_id: str


class CourseStats(BaseModel):
    total_courses: int
    course_titles: List[str]


def create_test_app(mock_rag_system):
    """Build a minimal FastAPI app with the same endpoints as app.py."""
    app = FastAPI()

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag_system.session_manager.create_session()
            answer, sources = mock_rag_system.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = mock_rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def mock_rag():
    """Mock RAGSystem with sensible defaults."""
    rag = Mock()
    rag.query.return_value = ("This is the answer.", [{"text": "Source 1", "link": None}])
    rag.session_manager.create_session.return_value = "session_1"
    rag.get_course_analytics.return_value = {
        "total_courses": 3,
        "course_titles": ["Intro to APIs", "MCP Course", "Python Basics"],
    }
    return rag


@pytest.fixture
def client(mock_rag):
    """TestClient wired to the test app."""
    app = create_test_app(mock_rag)
    return TestClient(app)


# ── /api/query tests ────────────────────────────────────────────────


class TestQueryEndpoint:
    def test_query_returns_200(self, client):
        resp = client.post("/api/query", json={"query": "What is MCP?"})
        assert resp.status_code == 200

    def test_query_response_shape(self, client):
        resp = client.post("/api/query", json={"query": "What is MCP?"})
        data = resp.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data

    def test_query_returns_answer(self, client):
        data = client.post("/api/query", json={"query": "What is MCP?"}).json()
        assert data["answer"] == "This is the answer."

    def test_query_returns_sources(self, client):
        data = client.post("/api/query", json={"query": "What is MCP?"}).json()
        assert len(data["sources"]) == 1
        assert data["sources"][0]["text"] == "Source 1"

    def test_query_creates_session_when_missing(self, client, mock_rag):
        data = client.post("/api/query", json={"query": "Hello"}).json()
        mock_rag.session_manager.create_session.assert_called_once()
        assert data["session_id"] == "session_1"

    def test_query_uses_provided_session(self, client, mock_rag):
        data = client.post(
            "/api/query", json={"query": "Hello", "session_id": "existing_session"}
        ).json()
        mock_rag.session_manager.create_session.assert_not_called()
        assert data["session_id"] == "existing_session"

    def test_query_passes_query_to_rag(self, client, mock_rag):
        client.post("/api/query", json={"query": "Tell me about MCP"})
        mock_rag.query.assert_called_once_with("Tell me about MCP", "session_1")

    def test_query_missing_body_returns_422(self, client):
        resp = client.post("/api/query", json={})
        assert resp.status_code == 422

    def test_query_empty_string_returns_200(self, client):
        resp = client.post("/api/query", json={"query": ""})
        assert resp.status_code == 200

    def test_query_rag_error_returns_500(self, client, mock_rag):
        mock_rag.query.side_effect = RuntimeError("Anthropic API down")
        resp = client.post("/api/query", json={"query": "test"})
        assert resp.status_code == 500
        assert "Anthropic API down" in resp.json()["detail"]

    def test_query_wrong_method_returns_405(self, client):
        resp = client.get("/api/query")
        assert resp.status_code == 405


# ── /api/courses tests ──────────────────────────────────────────────


class TestCoursesEndpoint:
    def test_courses_returns_200(self, client):
        resp = client.get("/api/courses")
        assert resp.status_code == 200

    def test_courses_response_shape(self, client):
        data = client.get("/api/courses").json()
        assert "total_courses" in data
        assert "course_titles" in data

    def test_courses_returns_count(self, client):
        data = client.get("/api/courses").json()
        assert data["total_courses"] == 3

    def test_courses_returns_titles(self, client):
        data = client.get("/api/courses").json()
        assert data["course_titles"] == ["Intro to APIs", "MCP Course", "Python Basics"]

    def test_courses_error_returns_500(self, client, mock_rag):
        mock_rag.get_course_analytics.side_effect = RuntimeError("DB offline")
        resp = client.get("/api/courses")
        assert resp.status_code == 500
        assert "DB offline" in resp.json()["detail"]

    def test_courses_wrong_method_returns_405(self, client):
        resp = client.post("/api/courses")
        assert resp.status_code == 405


# ── / (root) tests ─────────────────────────────────────────────────


class TestRootEndpoint:
    def test_unknown_api_route_returns_404(self, client):
        resp = client.get("/api/nonexistent")
        assert resp.status_code in (404, 405)
