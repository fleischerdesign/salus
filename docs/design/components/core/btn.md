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

## Visual Design

### Variants

| Variant | Background | Text Color | Border | Icon Color | Hover Bg | Press Bg |
|---------|-----------|-----------|--------|------------|---------|----------|
| Primary | `--color-primary` | `--color-on-primary` | none | `--color-on-primary` | `--color-primary-600` | `--color-primary-700` |
| Secondary | transparent | `--color-primary` | `1px solid --color-primary` | `--color-primary` | `--color-primary-50` | `--color-primary-100` |
| Ghost | transparent | `--color-primary` | none | `--color-primary` | `--color-primary-50` | `--color-primary-100` |
| Danger | `--color-error-50` | `--color-error-700` | none | `--color-error-600` | `--color-error-100` | `--color-error-200` |
| Small | `--color-slate-100` | `--color-slate-700` | `1px solid --color-slate-200` | `--color-slate-500` | `--color-slate-200` | `--color-slate-300` |

### Sizes

| Size | Height | Padding | Font | Icon Size | Icon↔Label |
|------|--------|---------|------|-----------|------------|
| Standard | 44px | 10px 20px | `--font-label-md` | 20px | 8px |
| Compact | 32px | 6px 12px | `--font-label-sm` | 16px | 6px |
| Icon-only | 28×28px | 0 | — | 18px | — |

### States

| State | Visual | Duration |
|-------|--------|----------|
| Default | Variant defaults | — |
| Hover | Background transitions to hover color | 150ms ease-default |
| Focus | Standard focus ring (2px primary-500, 2px offset) | instant |
| Active/Press | Background darkens, scale 0.98 | instant |
| Disabled | Opacity 0.5, cursor not-allowed | — |
| Loading | Spinner (16px) replaces label, `aria-busy="true"` | — |
| Success flash | Background → tertiary-100, reverts after 600ms | 600ms |

### Spacing
- Icon↔Label: 8px (standard), 6px (compact)
- Button-group gap: 8px, vertical stack below `--bp-mobile`
- Full-width below `--bp-mobile`

### Radius & Elevation
- Standard/Ghost/Danger: `--radius-md` (8px)
- Small: `--radius-sm` (4px)
- Icon-only: `--radius-full`
- No shadow. Flat by default.

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
