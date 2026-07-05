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

## Visual Design

### States

| State | Label | Icon/Spinner | Button State |
|-------|-------|-------------|-------------|
| Default | Visible | None | Active |
| Loading | Hidden (text preserved for width) | Spinner 16px, centered | Disabled, `aria-busy="true"` |
| Success | "Saved!" (2s) | ✓ check 16px, `--color-tertiary-600` | Normal |
| Error | "Failed" (2s) | ✕ 16px, `--color-error-600` | Normal |

### Width Preservation
Text set to `visibility: hidden` (not `display: none`) to prevent layout shift. Spinner absolutely centered.

### Transitions
- Default→Loading: 150ms text fade out + spinner fade in
- Loading→Success: 150ms spinner fade out + check fade in
- Success→Default: 2s delay, then 150ms revert
