# Toast / Notification

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Icon + Message + Optional action button + Close button

**Variants:** Success (tertiary) · Error (error) · Warning (warning) · Info (secondary)

**Placement:** Top-right of viewport. Stack vertically with 8px gap.

**Animation:** Slide-in from right (200ms ease-out), auto-dismiss after 5s (info/success) or persistent (error).

**States:** Entering · Visible · Dismissing (slide-out-right + fade, 200ms) · Dismissed

**Max visible:** 3 toasts at once. Older ones dismiss when new one arrives beyond limit.

**Accessibility:** `role="status"` for auto-dismiss, `role="alert"` for persistent errors. Focus should NOT move to toast.

**Do:** Use for transient feedback (save success, sync complete) · Include action for recoverable errors · Auto-dismiss non-critical toasts

**Don't:** Use for critical blocking errors (use Alert on page) · Stack more than 3 · Require user interaction for non-critical toasts

**Accessibility:**
- `role="status"` (auto-dismiss) or `role="alert"` (persistent). Use `aria-live="polite"` for info/success, `aria-live="assertive"` for errors.
- Focus does NOT move to toast
- Dismiss button: `aria-label="Dismiss notification"`
- Multiple toasts: each in its own live region for independent announcements

**Token Values:**
| Token | Value |
|-------|-------|
| --toast-max-width | 360px |
| --toast-shadow | `var(--shadow-lg)` |
| --toast-radius | `var(--radius-md)` |
| --toast-gap | `8px` |
| --toast-duration | 5s (auto-dismiss) |
| --toast-animation-in | slide-in-right 200ms ease-out |
| --toast-animation-out | slide-out-right 200ms ease-in |
| --toast-z-index | `var(--z-tooltip)` |
| --toast-max-visible | 3 |

**Composition:** Icon + Message + optional Action button + Close button. Positioned top-right viewport corner.

**Responsive:** Full-width on mobile with slight horizontal margin.

**Related:** `alert.md`, `btn.md`, `icon.md`

## Visual Design

### Variants

| Variant | Background | Text | Border | Icon | Icon Color |
|---------|-----------|------|--------|------|------------|
| Success | `--color-tertiary-50` | `--color-tertiary-800` | `1px solid --color-tertiary-200` | check_circle | `--color-tertiary-600` |
| Error | `--color-error-50` | `--color-error-800` | `1px solid --color-error-200` | error | `--color-error-600` |
| Warning | `--color-warning-50` | `--color-warning-800` | `1px solid --color-warning-200` | warning | `--color-warning-600` |
| Info | `--color-secondary-50` | `--color-secondary-800` | `1px solid --color-secondary-200` | info | `--color-secondary-600` |

### Anatomy
- Icon (20px, left) + Message (`--font-body-sm`, flexible center) + Action button (optional, ghost sm) + Close × (20px, right)
- Horizontal row layout, 12px inner padding (left/right), 10px vertical

### Appearance
- **Shadow:** `--shadow-lg`
- **Radius:** `--radius-md` (8px)
- **Max-width:** 360px
- **Position:** fixed, top-right, 16px from edge. Stack: 8px gap between toasts
- **Z-index:** `--z-tooltip` (500)

### Animation
| Phase | Animation | Duration |
|-------|-----------|----------|
| Enter | Slide-in from right (translateX 100%→0) + fade (0→1) | 200ms ease-out |
| Exit | Slide-out to right (translateX 0→100%) + fade (1→0) | 200ms ease-in |

### States
| State | Behavior |
|-------|----------|
| Visible | Start auto-dismiss timer (5s for success/info, ∞ for error) |
| Hover | Pause auto-dismiss timer |
| Dismissing | Play exit animation, remove from DOM after |
| Overflow (>3) | Oldest dismisses immediately as new one enters |

### Spacing
- Toast↔Toast stack gap: 8px
- Viewport edge margin: 16px top, 16px right
- Icon↔Message: 8px. Message↔Action: 8px
- Padding: 10px 12px

### Responsive
`< --bp-mobile`: Full-width, 16px horizontal margin, position: top (not top-right). Stack from top.
