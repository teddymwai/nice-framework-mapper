---
name: ui-unslop-and-apple-hig
description: UI design standards, quiet chrome architecture, Apple HIG component foundation, zero emoji mandate, and select element sanitization.
trigger: always_on
---

# UI Unslop Architecture & Apple HIG Component Guidelines

Whenever building, modifying, or styling user interfaces, dashboards, or web reports:

## 1. Zero "AI-Slop" & Emojis
- **Strictly No Emojis**: Never use emojis (no 🚀, ✨, 🔥, 🤖, ✅, ❌) as UI buttons, indicators, table badges, or headings.
- Use clean, professional vector iconography (e.g. Google Fonts Material Symbols or SVG icons).
- Tint icons with muted or secondary text colors to avoid visual distraction.

## 2. Quiet Chrome Architecture
- Understated, quiet navigation panels and structural chrome.
- Establish a strict 4px grid rhythm for all padding, margins, spacing, and sizing.
- Single bright focal point: Only the primary metric, action, or status gauge should claim high visual prominence.
- Ban neon glows, rainbow borders, and vibrating gradients.

## 3. Apple HIG Component Foundation
- **Shapes**:
  - Capsule geometry (`border-radius: 9999px`) for standalone pill buttons, filter chips, and toolbar actions.
  - Rounded Rectangles (`border-radius: 8px`–`12px`) for content cards, modals, and container surfaces.
- **Hit Targets**: Minimum **44x44px** hit target area on all interactive controls.
- **Tactile Response**: Add instant tactile feedback on click/press (`transform: scale(0.97)` on `:active`).
- **Prominence Hierarchy**: Scale visual importance by styling (Prominent, Tinted, Gray, Plain) rather than inconsistent physical sizes.
- **Skill Reference**: Full component schemas and button tokens live in `.agents/skills/apple-hig-components/`; the 9-pass redline lives in `.agents/skills/unslop-ui/`.

## 4. Form Controls & Select Sanitization
- Cross-browser select reset: `appearance: none; -webkit-appearance: none;`.
- Dedicated chevron right padding: `padding-right: 38px` to `42px`.
- Text truncation: `text-overflow: ellipsis; white-space: nowrap; overflow: hidden;`.
- Absolute or right-calculated positioning for dropdown SVG chevrons to eliminate collision with long text.

## 5. Self-Owned Design System: No External Attribution
- The UI Mantra (unslop methodology, Apple HIG adaptation, palette, iconography) is an internal CYBER RANGES standard.
- Never add external author handles, personal sites, third-party repository links, or `legacy/` vendored paths to docs, rules, READMEs, UI footers, or templates. Cite internal paths only (e.g. `docs/ui-mantra/03-ui-unslop-methodology.md`).
- Permitted: functional namespace URIs (`http://www.w3.org/2000/svg`, JSON Schema `$schema`) and runtime asset imports (Google Fonts Material Symbols stylesheet).
- Third-party code retained under its own license (e.g. CC BY 4.0) keeps its license notice in place; never propagate that notice into internal docs. Prefer rewriting as an original internal artifact over vendoring.

## 6. Composite Canvas Theming (`img001.jpg` Studio Curve Standard)
- **Dual-Layer Composite Canvas**: Dashboards and HTML reports never apply background textures bare. Ground the viewport in:
  1. **Fixed Parallax Backplane**: `background-attachment: fixed; background-size: cover; background-position: center top;` using the canonical **Studio Curve (`img001.jpg`)** texture (`/backgrounds/img001.jpg`).
  2. **Deep Obsidian Gradient Overlay**: `linear-gradient(180deg, rgba(9, 13, 11, 0.86) 0%, rgba(9, 13, 11, 0.94) 100%)` preserving WCAG AAA text contrast.
  3. **Frosted Glass Elevated Containers**: `background: rgba(21, 31, 26, 0.88); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08);`.
- **Zero Theme-Selector Clutter**: Standardize strictly on Studio Curve (`img001.jpg`); omit redundant theme dropdowns from top navigation bars to preserve quiet chrome.
- **Dual-Protocol Asset Resolution**: Local tool servers must stream `GET /backgrounds/<file>` with `file://` relative path fallback so dashboards render identically when opened offline from disk.

## 7. Position-Aware Floating Tooltips (`TooltipManager`) & Header Ergonomics
- **Floating Guidance (`TooltipManager`)**: Interactive buttons, filter pills, and safety toggles must provide position-aware tooltips (`data-tooltip="..."`, optional `data-shortcut="..."`) complying with WCAG 2.1 AA / 1.4.13:
  - Dismissible via `<kbd>Escape</kbd>`, hoverable without disappearing, initialized off-screen (`top: -9999px; left: -9999px`), and clamped to viewport edges with automatic top/bottom flip.
- **Header Layout Invariant**:
  - **Far Left**: Brand vector icon aligned horizontally inline with the tool title (never stacked awkwardly above it).
  - **Far Right**: Active deployment badge, loopback bind pill (`127.0.0.1:<port>`), and live session status indicator.
