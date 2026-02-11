# Course Materials RAG System

A Retrieval-Augmented Generation (RAG) system designed to answer questions about course materials using semantic search and AI-powered responses.

## Overview

This application is a full-stack web application that enables users to query course materials and receive intelligent, context-aware responses. It uses ChromaDB for vector storage, Anthropic's Claude for AI generation, and provides a web interface for interaction.


## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- An Anthropic API key (for Claude AI)
- **For Windows**: Use Git Bash to run the application commands - [Download Git for Windows](https://git-scm.com/downloads/win)

## Installation

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Python dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Running the Application

### Quick Start

Use the provided shell script:
```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

The application will be available at:
- Web Interface: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## Development with Claude Code

This repository is integrated with [Claude Code](https://claude.ai/code) for AI-assisted development and code review.

### Using @Claude Code in Pull Requests

You can mention `@Claude Code` in PR comments to get AI assistance:

**Code Review:**
```
@Claude Code please review this PR for potential issues
```

**Specific Questions:**
```
@Claude Code what are the security implications of this change?
@Claude Code how can I improve the performance of this function?
@Claude Code suggest test cases for this feature
```

**Documentation:**
```
@Claude Code help me write documentation for this new endpoint
@Claude Code explain what this code does
```

### Claude Code Review (Automated)

This repository has Claude Code Review enabled, which automatically:
- Reviews all pull requests for code quality and potential issues
- Checks for security vulnerabilities
- Suggests improvements following project conventions
- Validates adherence to architecture patterns

The review process uses the `CLAUDE.md` file for context about project architecture and coding standards.

### GitHub Actions Workflows

Several workflows support the Claude Code integration:

- **CI Workflow** (`ci.yml`): Runs tests, linting, and security scans
- **Claude Integration** (`claude-integration.yml`): Adds helpful comments to PRs and validates changes
- Both workflows run on every pull request and push to main

### Best Practices

1. **Before creating a PR:**
   - Run `bash run.sh` to test locally
   - Check that all endpoints work as expected
   - Review `CLAUDE.md` for coding standards

2. **In your PR description:**
   - Clearly describe what changed and why
   - Mention any potential risks or breaking changes
   - Use the PR template to ensure completeness

3. **When using @Claude Code:**
   - Be specific in your requests
   - Ask one question at a time for clearer responses
   - Review AI suggestions carefully before implementing

4. **Code review guidelines:**
   - See `CLAUDE.md` for detailed review criteria
   - Focus on security, especially API key handling
   - Ensure proper error handling and input validation

### Configuration Files

- **`CLAUDE.md`**: Project context and guidelines for Claude Code (both CLI and GitHub)
- **`.github/pull_request_template.md`**: Template for new pull requests
- **`.github/workflows/`**: Automated workflows for CI/CD and Claude integration

