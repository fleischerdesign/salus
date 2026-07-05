# Copy to Clipboard

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Target element (token/code/url) + Copy button (icon + "Copy" label)

**States:** Default · Copied (check icon, "Copied!" label, 2s, then reverts) · Error (alert icon, "Failed")

**Implementation:** `navigator.clipboard.writeText()` with fallback. Button triggers via HTMX or vanilla JS.

**Do:** Show visual confirmation after copy · Reset after 2s · Use for tokens, URLs, codes

**Don't:** Stay in "Copied" state permanently · Flash too fast to notice · Forget error handling

**Accessibility:**
- Button: `aria-label` describes target ("Copy token to clipboard")
- Clipboard API fallback: if `navigator.clipboard` unavailable, show error state
- Copied confirmation: use `aria-live="polite"` region for screen reader announcement
- Visual confirmation (check icon) must be accompanied by text for screen readers

**Token Values:**
| Token | Value |
|-------|-------|
| --copy-btn-icon-size | 16px |
| --copy-success-color | `{colors.tertiary-600}` |
| --copy-error-color | `{colors.error-600}` |
| --copy-transition | `var(--duration-fast) var(--ease-default)` |

**Related:** `btn.md`, `icon.md`, `code.md`, `inline-code.md`
