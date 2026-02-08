# Frontend Code Quality Tools

## Overview

Added essential code quality tools to the frontend development workflow, including Prettier for code formatting and ESLint for JavaScript linting.

## Files Added

### `frontend/package.json`
- Created npm project configuration with dev dependencies:
  - **Prettier** (`^3.4.0`) - Code formatter (the JavaScript/CSS/HTML equivalent of Black for Python)
  - **ESLint** (`^9.15.0`) - JavaScript linter for catching bugs and enforcing code style
  - **@eslint/js** (`^9.15.0`) - ESLint's recommended rule set
  - **globals** (`^15.12.0`) - Browser global variable definitions for ESLint
- Development scripts:
  - `npm run format` - Format all frontend files with Prettier
  - `npm run format:check` - Check formatting without modifying files (useful for CI)
  - `npm run lint` - Run ESLint on all JavaScript files
  - `npm run lint:fix` - Auto-fix ESLint issues where possible
  - `npm run quality` - Run both format check and lint (CI-friendly)
  - `npm run quality:fix` - Auto-fix both formatting and lint issues

### `frontend/.prettierrc`
- Prettier configuration matching existing code conventions:
  - Single quotes, semicolons, 4-space indentation, 100-char line width
  - No trailing commas, LF line endings

### `frontend/eslint.config.js`
- ESLint flat config (v9) with:
  - ESLint recommended rules as the base
  - Browser globals + `marked` library declared as readonly
  - `eqeqeq` enforced, `no-var` enforced, `prefer-const` as warning
  - Console logging allowed (appropriate for this application)

## Files Modified

### `frontend/index.html`, `frontend/script.js`, `frontend/style.css`
- Formatted with Prettier to establish a consistent baseline (minor whitespace changes only)

### `.gitignore`
- Added `node_modules/` entry

## How to Use

```bash
# From the frontend/ directory:

# Install dependencies (first time only)
npm install

# Format all files
npm run format

# Check formatting (CI)
npm run format:check

# Lint JavaScript
npm run lint

# Fix all quality issues at once
npm run quality:fix
```
