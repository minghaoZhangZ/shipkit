# Frontend UI/UX Quality Rules

These rules apply to frontend page, component, interaction, and browser-verification changes.

## Business UI First

- Management and operations systems should prioritize scanability, density with order, predictable navigation, and efficient repeated actions.
- Avoid marketing-page composition, decorative hero layouts, unrelated animations, and style-only changes unless the requirement explicitly asks for them.
- Reuse existing components, tokens, icons, layout utilities, route patterns, and state management before adding new abstractions.

## Required States

- Forms: visible labels, required markers, validation messages near fields, submit loading, disabled state, cancel/back behavior, and server-error recovery.
- Tables: pagination, empty state, loading state, filter reset, row actions, permission behavior, and overflow handling.
- Dangerous actions: confirmation dialog, clear consequence copy, and recovery/rollback note when possible.
- Permissions: hidden/disabled states must match existing authorization patterns and avoid leaking unauthorized actions.

## Accessibility And Responsive

- Interactive targets must be reachable by keyboard and have visible focus.
- Icon-only buttons need accessible labels or visible tooltips.
- Text contrast must remain readable in supported themes.
- Layout must avoid horizontal overflow at small widths.
- Fixed headers, footers, and sticky action bars must not cover content.

## Verification Evidence

- Frontend completion requires command evidence plus browser evidence when behavior changes.
- Browser evidence must include URL, viewport, operation, expected result, actual result, and console/runtime issues.
- If a path cannot be verified, record the exact reason in `<change-dir>/ai/09_验证结果.md`.
