# Alert / Banner

**Tokens:** `--alert-bg`, `--alert-text`, `--alert-border`, `--alert-radius`, `--alert-padding`, `--alert-icon-size`

**Anatomy:** Icon (20px) + Message text + Optional action button + Close button (×)

**Variants:** Success (tertiary) · Error (error) · Warning (warning) · Info (secondary)

**States:** Default · Dismissible (close button visible) · Persistent (no close button) · Dismissed

**Placement:** Inline within content (card body, form top, page top). Full-width of container.

**Animation:** Dismiss: fade out 200ms ease-in + slide up, content below slides into place.

**Do:** Use for feedback within page content · Include icon indicating severity · Make dismissible unless critical · Place above affected content

**Don't:** Use for transient toasts (use Toast) · Omit severity icon · Auto-dismiss critical alerts · Nest alerts

**Accessibility:**
- `role="alert"` for errors/warnings (immediate announcement). `role="status"` for success/info.
- Dismiss button: `aria-label="Dismiss notification"`
- Icon: `aria-hidden="true"` (accompanied by text)

**Responsive:** Full-width, stacked on mobile. Action button may wrap below text on narrow screens.

## Visual Design

### Variants

| Variant | Background | Text Color | Border | Icon Color |
|---------|-----------|-----------|--------|------------|
| Success | `--color-tertiary-50` | `--color-tertiary-800` | `1px solid --color-tertiary-300` | `--color-tertiary-600` |
| Error | `--color-error-50` | `--color-error-800` | `1px solid --color-error-300` | `--color-error-600` |
| Warning | `--color-warning-50` | `--color-warning-800` | `1px solid --color-warning-300` | `--color-warning-600` |
| Info | `--color-secondary-50` | `--color-secondary-800` | `1px solid --color-secondary-300` | `--color-secondary-600` |

### Anatomy
- Icon (20px, left) + Message (`--font-body-sm`) + Action button (right, optional) + Close × (right, optional)
- Layout: horizontal row, icon 12px from left edge, message flexible, buttons right

### States
| State | Close Button | Auto-Dismiss |
|-------|-------------|-------------|
| Dismissible | Visible (×) | No (manual) |
| Persistent | Hidden | No |
| Dismissing | × fades with alert | 200ms fade + slide |

### Sizes & Spacing
- Padding: 12px 16px
- Icon size: 20px, gap to text: 12px
- Action button: ghost sm (right), gap: 8px from text
- Radius: `--radius-md` (8px)

### Responsive
Full-width. On `< --bp-mobile`: action button may wrap below text. Icon stays top-aligned.

**Related:** `toast.md`, `confirm.md`, `input.md`, `btn.md`, `icon.md`, `form-layout.md`
