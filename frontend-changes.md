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
