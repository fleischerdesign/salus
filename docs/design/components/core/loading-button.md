# Loading Button

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Spinner (centered, replaces label) within button body.

**States:** Default · Loading (disabled, spinner visible, label hidden but preserves width) · Success (check icon, 2s display, returns to default) · Error (alert icon, reverts after 2s)

**Spinner:** 16px, border-based CSS animation, primary color. Centered within button.

**Implementation:** Button width preserved during loading (text visibility: hidden, not display: none) to prevent layout shift. `aria-busy="true"` while loading, `aria-live="polite"` for status changes.

**Do:** Preserve button width during loading · Show success briefly after completion · Disable during loading

**Don't:** Shrink button when spinner appears · Leave button in loading state indefinitely · Forget error feedback

**Accessibility:**
- `aria-busy="true"` during loading, removed on completion
- `aria-live="polite"` announces state transitions ("Saving...", "Saved!", "Error saving")
- Button is `disabled` during loading to prevent double-submission
- Success/Error icons: `aria-hidden="true"` (status communicated via live region text, not icon alone)

**Token Values:**
| Token | Value |
|-------|-------|
| --loading-btn-spinner-size | 16px |
| --loading-btn-success-color | `{colors.tertiary-600}` |
| --loading-btn-error-color | `{colors.error-600}` |
| --loading-btn-transition | `var(--duration-fast) var(--ease-default)` |

**Related:** `btn.md`, `spinner.md`, `toast.md`
