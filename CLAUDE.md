# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the application (from project root)
bash run.sh
# Or manually:
cd backend && uv run uvicorn app:app --reload --port 8000

# Install dependencies
uv sync

# Access points (when running)
# Web UI: http://localhost:8000
# API docs: http://localhost:8000/docs
```

Always use `uv` to run commands and manage dependencies. Never use `pip` directly.

There are no tests or linting configured in this project.

## Architecture

This is a RAG (Retrieval-Augmented Generation) chatbot for course materials. FastAPI backend serves a vanilla JS frontend as static files, all on port 8000.

### Query flow

1. **Frontend** (`frontend/script.js`) POSTs `{query, session_id}` to `/api/query`
2. **app.py** creates a session if needed, calls `rag_system.query()`
3. **rag_system.py** orchestrates: gets conversation history, calls `ai_generator.generate_response()` with tool definitions (`search_course_content` and `get_course_outline`)
4. **ai_generator.py** makes a Claude API call (claude-sonnet-4-20250514, temp=0, max_tokens=800). If Claude returns `stop_reason: "tool_use"`, it executes the tool and makes a second API call with the results (no tools) for the final answer
5. **search_tools.py** tool execution:
   - `CourseSearchTool.execute()` calls `vector_store.search()`, which does semantic similarity search on ChromaDB, then formats results and tracks sources
   - `CourseOutlineTool.execute()` resolves the course name, fetches metadata from `course_catalog`, and returns a formatted outline (title, link, lesson list)
6. Response flows back: `rag_system` saves to session history, `app.py` returns `{answer, sources, session_id}`

### Document ingestion flow

On startup (`app.py` startup event), files from `docs/` are loaded via `rag_system.add_course_folder()`:
- **document_processor.py** parses structured course files (header metadata + `Lesson N:` markers), chunks text into 800-char sentence-based pieces with 100-char overlap
- **vector_store.py** stores chunks in ChromaDB with SentenceTransformer (`all-MiniLM-L6-v2`) embeddings across two collections: `course_catalog` (metadata) and `course_content` (chunks)

### Key design decisions

- **Tool-based search**: Claude decides when to search via Anthropic tool calling (`search_course_content`) or retrieve outlines (`get_course_outline`), rather than always searching. General knowledge questions get direct answers.
- **Semantic course name resolution**: Partial course names (e.g., "MCP") are resolved to full titles via vector similarity on the `course_catalog` collection.
- **Sessions are in-memory**: `SessionManager` stores conversation history in a dict, limited to `MAX_HISTORY * 2` messages (default: 4 messages / 2 exchanges). No persistence across restarts.
- **ChromaDB is persistent**: Vector data persists in `backend/chroma_db/`.

### Expected document format

```
Course Title: [title]
Course Link: [url]
Course Instructor: [name]

Lesson 0: [title]
Lesson Link: [url]
[content...]
```

### Configuration

All settings in `backend/config.py` via `Config` dataclass. API key loaded from `.env` in project root.
