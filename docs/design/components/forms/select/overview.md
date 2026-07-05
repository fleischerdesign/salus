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

**Related:** `input.md`, `multiselect.md`, `search-input.md`, `autocomplete.md`, `checkbox.md`, `radio-group.md`, `form-layout.md`
