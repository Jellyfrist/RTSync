# RTSync Frontend Architecture

The frontend is organized so that changes stay close to the responsibility they affect.

| Area | Location | Responsibility |
| --- | --- | --- |
| Route views | `src/views` | Page-level state, API orchestration, and feature flows. |
| Layout | `src/components/layout` | Shared application shell, header, and sidebar. |
| UI patterns | `src/components/ui` | Reusable presentation patterns with no feature API calls. |
| APIs | `src/api` | HTTP boundary and response shaping. |
| Composables | `src/composables` | Reusable reactive behavior. |
| Styles | `src/styles` | Tokens, base rules, layout, shared component styles, page styles, then responsive overrides. |

## Styling rules

- Use semantic CSS variables from `styles/tokens.css`; do not add page-specific colors to Vue templates.
- Put reusable pattern styles in `styles/components/`.
- Put feature-only layout styles in `styles/pages/`.
- Keep responsive overrides in `styles/responsive.css` so breakpoints remain discoverable.
- Keep API calls and business flow handlers in views or composables, never in UI components.
