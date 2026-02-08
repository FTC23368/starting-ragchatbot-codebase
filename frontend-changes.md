# Frontend Changes: Dark/Light Theme Toggle Button

## Overview
Added a theme toggle button that allows users to switch between dark and light modes. The button is positioned in the top-right corner with sun/moon icons and smooth transition animations.

## Files Modified

### `frontend/index.html`
- Added a `<button>` element with id `themeToggle` positioned before the main container
- Contains two inline SVG icons: a sun icon (visible in dark mode) and a moon icon (visible in light mode)
- Includes `aria-label` and `title` attributes for accessibility

### `frontend/style.css`
- **Light theme CSS variables**: Added a `[data-theme="light"]` selector with a complete set of light-friendly color variables (light backgrounds, dark text, softer shadows)
- **`--code-bg` variable**: Replaced hardcoded `rgba(0, 0, 0, 0.2)` for code block backgrounds with a CSS variable that adapts per theme
- **Toggle button styles**: Fixed position top-right, circular button with hover scale effect, focus ring for keyboard navigation
- **Icon transition**: Sun and moon icons crossfade with rotation animation (0.3s ease) when toggling
- **Body transition**: Added `transition: background-color 0.3s ease, color 0.3s ease` to body for smooth theme switching

### `frontend/script.js`
- **`initializeTheme()`**: Reads saved theme from `localStorage` on page load and applies it via `data-theme` attribute on `<html>`
- **`toggleTheme()`**: Toggles between `dark` and `light` themes, updates `data-theme` attribute, and persists choice to `localStorage`
- **Event listener**: Wired up the toggle button click to `toggleTheme()`

## Design Decisions
- **Icon approach**: Sun icon shown in dark mode (click to go light), moon icon in light mode (click to go dark) - follows common convention
- **CSS variables**: All theme colors flow through CSS custom properties, so the entire UI adapts with a single attribute change
- **localStorage persistence**: Theme preference survives page reloads and browser sessions
- **Accessibility**: Button has `aria-label`, is keyboard-focusable with visible focus ring, and responds to Enter/Space keys natively

---

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
