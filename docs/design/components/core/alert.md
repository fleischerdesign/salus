# Alert

**Tokens:** `--alert-radius`, `--alert-padding`, `--alert-font`, `--alert-success-bg`, `--alert-success-border`, `--alert-success-text`, `--alert-error-bg`, `--alert-error-border`, `--alert-error-text`

**Anatomy:** Icon + Message text

**Variants:**

| Type | Background | Border | Text | Icon |
|------|-----------|--------|------|------|
| Success | `tertiary-50` | `tertiary-300` | `tertiary-800` | check_circle |
| Error | `error-50` | `error-300` | `error-800` | error |

**States:** Default · Dismissable (with close button) · Auto-dismiss (for toasts, see toast.md)

**Spacing:** Padding: 12px 16px · Icon↔Message: 8px

**Accessibility:** `role="alert"` so screen readers announce immediately.

**Do:** Use for page-level feedback · Include clear action if error is recoverable · Use role="alert"

**Don't:** Use for inline field validation (use error-text) · Stack multiple alerts · Leave ambiguous ("Something went wrong")

**Composition:** Contains: Icon + Text + optional close Button. Alert is always inline in page content, never inside modals or overlays.

**Responsive:** Full-width, padding reduces to 8px on mobile. Text may wrap.

**Related:** `toast.md`, `input.md`, `confirmation-dialog.md`, `form-layout.md`
