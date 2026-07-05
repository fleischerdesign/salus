# Select / Dropdown

**Tokens:** `--select-bg`, `--select-border`, `--select-radius`, `--select-padding`, `--select-typography`, `--select-chevron-size`, `--select-chevron-color`, `--select-option-padding`, `--select-option-hover-bg`, `--select-option-selected-bg`, `--select-option-selected-text`, `--select-no-results-color`, `--select-z-index`

**Anatomy:** Label (above) + Select trigger (chevron right) + Dropdown list (absolutely positioned, card-overlay style)

**States:** Default · Open (chevron rotates 180°, dropdown visible) · Selected (option highlighted) · Focus · Disabled · Error

**Sizes:** One standard size. Height: 44px (matching input). Dropdown: max-height 280px, scrollable.

**Spacing:** Label↔Select: 4px · Trigger padding: 10px 12px · Option padding: 10px 12px · Select↔Hint/Error: 4px

**Do:** Use for 4+ options · Match height with text inputs · Show checkmark on selected option · Allow keyboard navigation (Arrow keys, Enter, Escape)

**Don't:** Use for 2-3 options (use Radio Group) · Forget search/filter for 15+ options · Omit label

**Accessibility:**
- Native `<select>` preferred; custom select needs `role="listbox"`, `aria-expanded`, `aria-activedescendant`
- Label via `<label>` with matching `for`/`id`
- Keyboard: Arrow keys navigate, Enter selects, Escape closes
- Selected value announced to screen readers

**Composition:** Label + Trigger (text + chevron icon) + Dropdown (list of options). Dropdown positioned below trigger with 4px gap.

**Responsive:** Full-width below `bp-mobile`. Dropdown width matches trigger width.

## Visual Design

### Appearance
- **Trigger:** matches Input: `--color-slate-50` bg, `1px --color-slate-300` border, `--radius-md`, 44px height
- **Chevron:** 20px, `--color-slate-400`, right side, 12px from right edge
- **Dropdown:** `#ffffff` bg, `--shadow-lg`, `--radius-md`, 4px gap from trigger, max-height 280px scrollable
- **Option:** 10px 12px padding, `--font-body-md`
- **Search (optional):** text input at top of dropdown for filtering 15+ options
- **No results:** `--font-body-sm`, `--color-slate-400`, centered, padding 16px

### States

| State | Trigger Border | Chevron | Dropdown |
|-------|---------------|---------|----------|
| Default | `--color-slate-300` | 0° | hidden |
| Hover | `--color-slate-400` | 0° | hidden |
| Focus | `--color-primary-500` + ring | 0° | hidden |
| Open | `--color-primary-500` | 180° rotated | visible |
| Error | `--color-error-400` | 0° | hidden |
| Disabled | `--color-slate-200` | `--color-slate-300` | hidden, opacity 0.5 |

Chevron rotation: 150ms ease-default.

### Options

| State | Background | Text |
|-------|-----------|------|
| Default | transparent | `--color-on-surface` |
| Hover | `--color-slate-100` | `--color-on-surface` |
| Selected | `--color-primary-50` | `--color-primary-700` |
| Active (keyboard) | `--color-slate-100` | `--color-on-surface` |

### Spacing
- Label↔Select: 4px
- Trigger padding: 10px 12px
- Option padding: 10px 12px
- Dropdown↔Trigger gap: 4px

### Responsive
Full-width below `--bp-mobile`. Dropdown always matches trigger width.

### Elevation
Dropdown: Level-2 overlay. `--shadow-lg`, `--z-dropdown` (100).

**Related:** `input.md`, `multiselect.md`, `search-input.md`, `autocomplete.md`, `checkbox.md`, `radio-group.md`, `form-layout.md`
