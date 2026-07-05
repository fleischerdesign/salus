# Radio Group

**Tokens:** Reuses `--btn-sm-*` tokens

**Anatomy:** Group label (label-sm) + Option list (horizontal or vertical button-group)

**States:** Default · Selected/Active (btn-sm.active: primary bg, white text, primary border) · Focus

**Implementation:** Hidden radio inputs with visible button labels. Wrapped in form with `onchange`, or HTMX-driven.

**Do:** Use for single-select from small set (2-5 options) · Style as button group for visual clarity · Provide group label

**Don't:** Use for >5 options (use Select) · Use without visible label · Mix horizontal and vertical

**Accessibility:**
- `<fieldset>` + `<legend>` wraps the group
- Each option: `<input type="radio">` + `<label>` with matching `for`/`id`
- Selected: `checked` attribute
- Keyboard: Tab to group, Arrow keys change selection within group

**Token Values:**
| Token | Value |
|-------|-------|
| --radio-group-gap | `8px` |
| --radio-group-item-padding | `6px 12px` |

**Related:** `checkbox.md`, `toggle.md`, `select.md`, `form-layout.md`

## Visual Design

### Appearance
- **Option (default):** `--color-slate-100` bg, `--color-slate-700` text, `1px solid --color-slate-200` border, `--radius-md`, padding 6px 12px
- **Option (selected):** `--color-primary` bg, `--color-on-primary` text, `1px solid --color-primary` border
- **Group label:** `--font-label-md`, `--color-on-surface`, margin-bottom 8px
- **Font:** `--font-label-md`
- **Cursor:** pointer

### States

| State | Background | Text | Border |
|-------|-----------|------|--------|
| Default | `--color-slate-100` | `--color-slate-700` | `--color-slate-200` |
| Hover | `--color-slate-200` | `--color-slate-700` | `--color-slate-300` |
| Selected | `--color-primary` | `--color-on-primary` | `--color-primary` |
| Selected hover | `--color-primary-600` | `--color-on-primary` | `--color-primary-600` |
| Focus | Standard focus ring | — | — |

Transition: background + border 150ms ease-default.

### Layout
| Direction | Gap | Use |
|-----------|-----|-----|
| Horizontal (default) | 8px | 2-5 options |
| Vertical | 8px | Narrow containers |

### Spacing
- Option padding: 6px 12px
- Group label↔Options gap: 8px
- Option↔Option gap: 8px

### Responsive
Horizontal → vertical below `--bp-mobile`.
