# Chip (Status Label)

**Tokens:** `--chip-radius`, `--chip-padding`, `--chip-font`, `--chip-success-bg`, `--chip-success-text`, `--chip-warning-bg`, `--chip-warning-text`, `--chip-error-bg`, `--chip-error-text`, `--chip-neutral-bg`, `--chip-neutral-text`

**Anatomy:** Optional icon + Label text

**Variants:**

| Type | Background | Text |
|------|-----------|------|
| Success | `{colors.tertiary-50}` | `{colors.tertiary-800}` |
| Warning | `{colors.warning-50}` | `{colors.warning-800}` |
| Error | `{colors.error-50}` | `{colors.error-800}` |
| Neutral | `{colors.slate-100}` | `{colors.slate-600}` |

**States:** Default only. Clickable variant (with hover state) for action chips.

**Sizes:** One size. Padding: 4px 12px.

**Do:** Use for status indicators, tags, categories · Keep labels short (1-2 words) · Use neutral for metadata, semantic for status

**Don't:** Use as buttons (unless clickable variant) · Overflow with long text · Mix semantic and neutral in same context

**Accessibility:**
- Status chip (non-interactive): `<span>` element, purely visual
- Action chip (clickable): `<button>` or `role="button"` + `tabindex="0"` + `aria-pressed` for toggle chips
- Removable chip: × button with `aria-label="Remove {label}"`

**Related:** `badge.md`, `chip-row.md`, `status-dot.md`, `diagnosis-tag.md`

## Visual Design

### Appearance
- **Shape:** `--radius-full` (pill), 24px height, 4px 12px padding
- **Font:** `--font-label-sm` (12px, 500)
- **Icon (optional):** 14px, left of label, gap 4px
- **Dismiss ×:** 14px, right, transparent → variant hover

### Variants

| Variant | Background | Text | Icon Color | Dismiss Hover |
|---------|-----------|------|------------|---------------|
| Success | `--color-tertiary-50` | `--color-tertiary-800` | `--color-tertiary-600` | `--color-tertiary-100` |
| Warning | `--color-warning-50` | `--color-warning-800` | `--color-warning-600` | `--color-warning-100` |
| Error | `--color-error-50` | `--color-error-800` | `--color-error-600` | `--color-error-100` |
| Neutral | `--color-slate-100` | `--color-slate-600` | `--color-slate-500` | `--color-slate-200` |

### Types
| Type | Default | Hover | Click |
|------|---------|-------|-------|
| Status | Variant default | No change | No action |
| Action | Variant default | Background darkens 1 shade | Executes action |
| Removable | Variant default | Dismiss × highlights | Removes chip |

### Spacing
- Icon↔Label: 4px. Chip↔Chip: 4px (row), 8px (wrap)
