# Button (btn)

**Tokens:** `--btn-primary-bg`, `--btn-primary-text`, `--btn-primary-hover-bg`, `--btn-secondary-border`, `--btn-secondary-text`, `--btn-secondary-hover-bg`, `--btn-ghost-text`, `--btn-ghost-hover-bg`, `--btn-danger-bg`, `--btn-danger-text`, `--btn-danger-hover-bg`, `--btn-sm-bg`, `--btn-sm-border`, `--btn-sm-text`, `--btn-sm-hover-bg`, `--btn-icon-size`, `--btn-icon-hover-bg`, `--btn-radius`, `--btn-font`, `--btn-padding`, `--btn-padding-sm`

**Anatomy:** Icon (optional) + Label

| Variant | Background | Text | Border | Hover |
|---------|-----------|------|--------|-------|
| Primary | `{colors.primary}` | `{colors.on-primary}` | none | `{colors.primary-600}` |
| Secondary | transparent | `{colors.primary}` | `{colors.primary}` | `{colors.primary-50}` |
| Ghost | transparent | `{colors.primary}` | none | `{colors.primary-50}` |
| Danger | `{colors.error-50}` | `{colors.error-700}` | none | `{colors.error-100}` |
| Small | `{colors.slate-100}` | `{colors.slate-700}` | `{colors.slate-200}` | `{colors.slate-200}` |

**States:** Default · Hover (brightness or bg change) · Focus (2px outline offset) · Active · Disabled (opacity 0.5, `cursor: not-allowed`) · Loading (spinner replaces label, button disabled)

**Sizes:** Standard (h:44px, px:20px) · Small (h:32px, px:12px) · Icon (28×28px, rounded-full)

**Spacing:** Icon↔Label: 8px · Button-group gap: 8px · Full-width below `bp-mobile`

**Do:** Primary for main CTA · Secondary for secondary action · Ghost for Cancel · Danger for destructive · Icon button for icon-only actions

**Don't:** Two Primary buttons side-by-side · Disabled button as informational state · Icon without aria-label

**Accessibility:**
- Native `<button>` element preferred; `role="button"` + `tabindex="0"` + Enter/Space handlers if `<div>` used
- Icon-only buttons MUST have `aria-label` (e.g., `aria-label="Close"`)
- Loading state: `aria-busy="true"`, disable interaction
- Disabled: `disabled` attribute (not just CSS)
- Toggle buttons: `aria-pressed="true/false"`
- Focus: visible ring via `:focus-visible`

**Responsive:** Full-width on mobile (`<600px`). Button-group stacks vertically below `bp-mobile`.

**Related:** `loading-btn.md`, `icon.md`, `focus-ring.md`, `toggle.md`
