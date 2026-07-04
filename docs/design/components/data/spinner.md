# Spinner

**Anatomy:** Rotating ring indicator, centered.

**Sizes:** Small (16px, inline) · Medium (24px, button) · Large (40px, page/container)

**Animation:** 0.8s linear infinite rotation. Primary color, 2-3px border with transparent gap.

**Usage:**
- Inline: replaces icon or label text during HTMX load
- Container: centered in parent when content loading
- Button: replaces label, see loading-button.md

**Accessibility:** `aria-busy="true"` on parent. `role="status"` or `aria-label="Loading"` on spinner.

**Do:** Match spinner size to context · Use aria-busy on loading container · Show in HTMX indicators

**Don't:** Forget to remove when loaded · Use tiny spinner for full-page load · Omit accessible label
