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
