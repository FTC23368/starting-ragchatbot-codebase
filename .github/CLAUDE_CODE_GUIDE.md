# Claude Code Quick Reference Guide

This guide helps you get the most out of Claude Code integration in this repository.

## Table of Contents
- [Getting Started](#getting-started)
- [Common Commands](#common-commands)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites
1. You need access to the Claude Code GitHub integration
2. The repository must have Claude Code installed (already done for this repo)
3. You should be familiar with the project structure (see `CLAUDE.md`)

### First Steps
1. Create a branch for your changes: `git checkout -b feature/your-feature-name`
2. Make your changes following the project conventions
3. Create a pull request
4. Use `@Claude Code` in PR comments for assistance

## Common Commands

### Code Review Requests

**Full PR Review:**
```
@Claude Code please review this PR
```

**Focused Review:**
```
@Claude Code review the changes in backend/app.py
@Claude Code check for security issues in this endpoint
@Claude Code review the error handling in this function
```

### Code Improvements

**Performance:**
```
@Claude Code how can I optimize this query?
@Claude Code suggest performance improvements for this function
```

**Security:**
```
@Claude Code are there any security vulnerabilities here?
@Claude Code check if API keys are properly protected
@Claude Code review input validation in this endpoint
```

**Code Quality:**
```
@Claude Code suggest improvements to make this code more maintainable
@Claude Code how can I make this function more testable?
@Claude Code is this following Python best practices?
```

### Testing & Documentation

**Test Suggestions:**
```
@Claude Code suggest test cases for this feature
@Claude Code what edge cases should I test?
@Claude Code help me write a pytest test for this function
```

**Documentation:**
```
@Claude Code help me write a docstring for this function
@Claude Code explain what this code does
@Claude Code should I update CLAUDE.md for this change?
```

### Debugging Help

```
@Claude Code why might this function be failing?
@Claude Code what could cause this error?
@Claude Code help me understand this stack trace
```

## Best Practices

### 1. Be Specific
❌ **Bad:** `@Claude Code review this`
✅ **Good:** `@Claude Code review the authentication logic in app.py lines 45-67`

### 2. One Question at a Time
❌ **Bad:** `@Claude Code review everything and also help me optimize and write tests`
✅ **Good:** First ask for review, then separately ask about optimization

### 3. Provide Context
✅ **Good:** `@Claude Code this function handles user queries. Can you suggest how to improve error handling?`

### 4. Review AI Suggestions
- Always review Claude's suggestions before implementing them
- Test changes locally before committing
- Ask follow-up questions if something is unclear

### 5. Use in Combination with CI
- Let GitHub Actions run first to catch basic issues
- Use @Claude Code for deeper analysis and suggestions
- Address CI failures before asking for review

## Examples

### Example 1: New Feature Review

**Scenario:** You added a new API endpoint

```markdown
## PR Description
Added `/api/search-history` endpoint to retrieve user's search history

@Claude Code please review this new endpoint for:
1. Security issues (especially session validation)
2. Error handling completeness
3. Adherence to project architecture patterns
4. Potential performance concerns
```

### Example 2: Bug Fix Validation

**Scenario:** You fixed a bug

```markdown
## PR Description
Fixed issue where empty queries crashed the backend

**Changes:**
- Added input validation in app.py
- Added error response for empty queries

@Claude Code can you verify that this fix properly handles all edge cases?
```

### Example 3: Refactoring Review

**Scenario:** You refactored code for maintainability

```markdown
## PR Description
Refactored vector_store.py to improve readability

@Claude Code please review this refactoring to ensure:
1. Functionality remains the same
2. Code is now more maintainable
3. No performance regressions introduced
4. Follows project coding standards from CLAUDE.md
```

### Example 4: Getting Unstuck

**Scenario:** You're not sure how to implement something

```markdown
I'm trying to add pagination to the search results but I'm not sure the best approach given our ChromaDB setup.

@Claude Code can you suggest how to implement pagination for vector search results in this codebase?
```

## Troubleshooting

### Claude Code Not Responding

**Check:**
1. Did you mention `@Claude Code` (with capital C)?
2. Is the GitHub integration still active for this repo?
3. Are you commenting on a pull request (not a direct commit)?

### Unexpected Suggestions

**Solutions:**
1. Check that `CLAUDE.md` is up to date with current project standards
2. Provide more context in your question
3. Be specific about what you want reviewed

### Review Doesn't Match Project Style

**Actions:**
1. Update `CLAUDE.md` with missing conventions
2. Point Claude to specific sections: `@Claude Code please follow the error handling pattern described in CLAUDE.md`

### Rate Limiting

If you're making many requests:
1. Combine related questions into one request
2. Wait a few minutes between requests
3. Be more specific to get targeted responses

## Additional Resources

- **Project Architecture:** See `CLAUDE.md`
- **Coding Standards:** See "Code Review Guidelines" section in `CLAUDE.md`
- **PR Template:** `.github/pull_request_template.md`
- **CI Workflows:** `.github/workflows/`

## Tips for Success

1. **Start small:** Try simple questions first to get familiar
2. **Iterate:** Use follow-up questions to refine suggestions
3. **Combine with manual review:** Claude Code assists, but human review is still important
4. **Learn patterns:** Notice what Claude suggests and incorporate good patterns into your code
5. **Update CLAUDE.md:** When you establish new conventions, add them to CLAUDE.md

---

**Need more help?** Check the main README.md or reach out to the repository maintainers.
