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

**Related:** `toast.md`, `confirm.md`, `input.md`, `btn.md`, `icon.md`, `form-layout.md`
