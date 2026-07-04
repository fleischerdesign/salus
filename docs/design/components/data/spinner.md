# Spinner

**Anatomy:** Rotating ring indicator, centered.

**States:** Hidden · Visible/Spinning · Stopped (content loaded)

**Sizes:** Small (16px, inline) · Medium (24px, button) · Large (40px, page/container)

**Animation:** 0.8s linear infinite rotation. Primary color, 2-3px border with transparent gap.

**Usage:**
- Inline: replaces icon or label text during HTMX load
- Container: centered in parent when content loading
- Button: replaces label, see loading-button.md

**Accessibility:** `aria-busy="true"` on parent. `role="status"` or `aria-label="Loading"` on spinner.

**Do:** Match spinner size to context · Use aria-busy on loading container · Show in HTMX indicators

**Don't:** Forget to remove when loaded · Use tiny spinner for full-page load · Omit accessible label

**Accessibility:**
- `role="status"` or `aria-label="Loading"` on spinner element
- Container: `aria-busy="true"` during load
- Inline spinners (buttons, inputs): `aria-busy` on the interactive element
- Spinner animation respects `prefers-reduced-motion`: stops spinning if user prefers reduced motion

**Token Values:**
| Token | Value |
|-------|-------|
| --spinner-sm | 16px |
| --spinner-md | 24px |
| --spinner-lg | 40px |
| --spinner-color | `{colors.primary}` |
| --spinner-duration | 0.8s |
| --spinner-easing | `linear` |

**Related:** `skeleton.md`, `loading-button.md`, `empty-state.md`
