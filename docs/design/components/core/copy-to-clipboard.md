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

## Visual Design

### Appearance
- **Target:** monospace text (`--font-code-sm`), `--color-slate-100` bg, padding 8px 12px, `--radius-sm`, `1px solid --color-slate-200`
- **Copy button:** 28×28px ghost icon-only button, `content_copy` icon 16px, right of target, gap 8px
- **Success state:** icon → `check` (16px, `--color-tertiary-600`), tooltip "Copied!"
- **Error state:** icon → `error` (16px, `--color-error-600`), tooltip "Failed to copy"

### States
| State | Icon | Color | Duration |
|-------|------|-------|----------|
| Default | `content_copy` | `--color-slate-500` | — |
| Hover | `content_copy` | `--color-slate-700` | — |
| Copied | `check` | `--color-tertiary-600` | 2s, then reverts |
| Error | `error` | `--color-error-600` | Until dismissed |

Transition: 150ms ease-default icon switch.

### Spacing
- Target↔Button gap: 8px
- Target padding: 8px 12px
- Button: 28×28px, icon: 16px
