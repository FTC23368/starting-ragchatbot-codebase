# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Course Materials RAG (Retrieval-Augmented Generation) Chatbot** - a full-stack web application that enables users to ask questions about educational course materials and receive AI-powered answers with source citations.

**Tech Stack:**
- Backend: Python 3.13+, FastAPI, ChromaDB (vector database), Anthropic Claude Sonnet 4
- Frontend: Vanilla JavaScript, HTML, CSS (no frameworks)
- Package Manager: uv (not pip)

## Development Commands

### Setup & Installation
```bash
# Install dependencies (use uv, not pip)
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your-key-here
```

### Running the Application
```bash
# Quick start (recommended)
./run.sh

# Manual start
cd backend && uv run uvicorn app:app --reload --port 8000

# Access points:
# - Web UI: http://localhost:8000
# - API docs: http://localhost:8000/docs
```

### Development Workflow
```bash
# Run any Python script with uv
uv run python backend/script.py

# Install new dependency
# 1. Add to pyproject.toml dependencies list
# 2. Run: uv sync

# Clear ChromaDB and reload documents
# Delete ./backend/chroma_db/ directory, then restart server
```

## Architecture Overview

### RAG Pipeline Flow

The application uses a **tool-calling RAG architecture** where Claude autonomously decides when to search:

```
User Query → FastAPI Endpoint → RAG System → AI Generator
                                      ↓
                            Claude API Call #1 (with tools)
                                      ↓
                            Claude decides to use search_course_content tool
                                      ↓
                            Tool Manager → CourseSearchTool → VectorStore
                                      ↓
                            ChromaDB semantic search (top 5 results)
                                      ↓
                            Format results with [Course - Lesson N] headers
                                      ↓
                            Claude API Call #2 (with search results)
                                      ↓
                            Return answer + sources → Frontend
```

**Key difference from traditional RAG:** Claude actively chooses whether/when to search using function calling, rather than always retrieving context upfront.

### Core Components

**Backend (`backend/`):**

1. **rag_system.py** - Main orchestrator
   - Coordinates all RAG components
   - Manages query flow and session history
   - Entry point for all query processing

2. **ai_generator.py** - Claude API wrapper
   - Handles TWO API calls per query:
     - Call #1: Claude receives query + available tools, returns tool_use request
     - Call #2: Claude receives tool results, returns final answer
   - System prompt in `AIGenerator.SYSTEM_PROMPT`
   - Temperature=0, max_tokens=800

3. **document_processor.py** - Document parsing & chunking
   - Expected format: First 3 lines = `Course Title:`, `Course Link:`, `Course Instructor:`
   - Detects lessons via regex: `Lesson \d+: Title`
   - Sentence-based chunking (800 chars, 100 char overlap)
   - **Important:** First chunk of each lesson gets prefix: `"Lesson {N} content: {chunk}"`

4. **vector_store.py** - ChromaDB interface
   - **Two collections:**
     - `course_catalog`: Course metadata (title, instructor, lessons_json)
     - `course_content`: Chunked text with embeddings
   - Uses sentence-transformers: `all-MiniLM-L6-v2`
   - Course name resolution via semantic search (fuzzy matching)

5. **search_tools.py** - Tool definitions for Claude
   - `CourseSearchTool`: Implements search_course_content tool
   - Tracks `last_sources[]` for UI display
   - Formats results with `[Course Title - Lesson N]` headers

6. **session_manager.py** - Conversation history
   - Stores last 2 exchanges (4 messages) per session
   - History injected into system prompt for context

7. **config.py** - Centralized settings
   - All tunable parameters in `Config` dataclass
   - Loads `ANTHROPIC_API_KEY` from `.env`

**Frontend (`frontend/`):**
- `index.html`: Chat UI with sidebar (course stats, suggested questions)
- `script.js`: Handles `/api/query` and `/api/courses` endpoints, manages session_id
- `style.css`: Dark theme (#0f172a background)

### Data Models (`models.py`)

```python
Course(title, course_link, instructor, lessons=[])
Lesson(lesson_number, title, lesson_link)
CourseChunk(content, course_title, lesson_number, chunk_index)
```

**Important:** `Course.title` is used as the unique identifier throughout the system.

### Document Processing Details

**Input format** (`docs/*.txt`):
```
Course Title: Building Towards Computer Use
Course Link: https://example.com
Course Instructor: Colt Steele

Lesson 0: Introduction
Lesson Link: https://example.com/lesson0
[lesson content...]

Lesson 1: Next Topic
[lesson content...]
```

**Processing steps:**
1. Parse metadata from first 3 lines
2. Split by `Lesson \d+:` markers
3. Chunk each lesson's content (sentence-based, 800 chars with 100 overlap)
4. Add contextual prefixes: `"Course {title} Lesson {N} content: {text}"`
5. Generate embeddings using sentence-transformers
6. Store in ChromaDB with metadata: `{course_title, lesson_number, chunk_index}`

### ChromaDB Schema

**Collection: `course_catalog`**
- Documents: Course titles (plain text)
- Metadata: `{title, instructor, course_link, lessons_json, lesson_count}`
- IDs: Course title (used as unique identifier)

**Collection: `course_content`**
- Documents: Text chunks with contextual prefixes
- Metadata: `{course_title, lesson_number, chunk_index}`
- IDs: `{course_title_with_underscores}_{chunk_index}`

### Session Management

- Session IDs: `session_1`, `session_2`, etc.
- History format injected into system prompt:
  ```
  Previous conversation:
  User: [previous question]
  Assistant: [previous answer]
  User: [another question]
  Assistant: [another answer]
  ```
- Limit: Last 2 exchanges (`MAX_HISTORY=2` in config)

## Key Implementation Patterns

### Adding New Search Parameters

To add a new search filter (e.g., search by instructor):

1. Update tool definition in `search_tools.py`:
   ```python
   "input_schema": {
       "properties": {
           "instructor": {"type": "string", "description": "..."}
       }
   }
   ```

2. Update `CourseSearchTool.execute()` to accept parameter

3. Update `VectorStore.search()` to handle new filter

4. Update `VectorStore._build_filter()` to construct ChromaDB where clause

### Modifying Chunking Strategy

All chunking logic is in `DocumentProcessor.chunk_text()`:
- Current: Sentence-based with overlap
- To change: Modify sentence splitting regex or chunk size calculation
- **Remember:** Update `CHUNK_SIZE` and `CHUNK_OVERLAP` in `config.py`

### Changing AI Behavior

**System prompt:** `ai_generator.py` line 8-30 (`AIGenerator.SYSTEM_PROMPT`)
- Controls when Claude searches vs. answers directly
- Response format and style
- Search result usage instructions

**Model parameters:** `ai_generator.py` line 37-41
- `temperature=0`: Deterministic responses
- `max_tokens=800`: Response length limit
- Model: `config.ANTHROPIC_MODEL`

### Debugging the RAG Pipeline

**Enable verbose logging:**
```python
# In vector_store.py, ai_generator.py, etc.
print(f"Search query: {query}")
print(f"Results: {results}")
```

**Check ChromaDB contents:**
```python
# In Python REPL
from backend.vector_store import VectorStore
vs = VectorStore("./backend/chroma_db", "all-MiniLM-L6-v2", 5)
vs.course_catalog.get()  # See all courses
vs.course_content.get(limit=10)  # See first 10 chunks
```

**Reset vector database:**
```bash
rm -rf backend/chroma_db
./run.sh  # Will recreate and reload documents
```

## Important Constraints

1. **Use uv, not pip:** All dependency management via `uv sync` and `uv run`

2. **Course title is the ID:** Throughout the codebase, `Course.title` serves as the unique identifier. Changing a course title requires recreating the vector database.

3. **Two ChromaDB collections required:** The system needs both `course_catalog` (metadata) and `course_content` (searchable chunks). Don't delete one without the other.

4. **Document format is strict:** First 3 lines must follow the `Course Title:`, `Course Link:`, `Course Instructor:` format. Lessons must use `Lesson N:` markers.

5. **Claude makes two API calls per query:** The tool-calling pattern requires sequential calls - don't try to parallelize.

6. **Sentence-transformers download on first run:** The `all-MiniLM-L6-v2` model (~90MB) downloads automatically on first startup. This is normal.

7. **Session history is in-memory:** Restarting the server clears all conversation history. For persistence, implement database storage in `session_manager.py`.

## Configuration Parameters

All tunable settings in `backend/config.py`:

- `CHUNK_SIZE=800`: Text chunk size for embeddings (balance between context and precision)
- `CHUNK_OVERLAP=100`: Overlap between chunks (prevents losing context at boundaries)
- `MAX_RESULTS=5`: Number of search results returned to Claude
- `MAX_HISTORY=2`: Conversation exchanges to remember (2 = 4 messages)
- `ANTHROPIC_MODEL`: Claude model to use
- `EMBEDDING_MODEL`: Sentence-transformers model for embeddings

**Tuning guidance:**
- Increase `CHUNK_SIZE` if answers lack context
- Increase `MAX_RESULTS` if relevant information is missed
- Increase `MAX_HISTORY` for longer conversations (increases token usage)
- Decrease `CHUNK_OVERLAP` to reduce storage size (may lose context)
- always use uv to run the server do not use pip directly
- make sure to use uv to manage all depenedencies