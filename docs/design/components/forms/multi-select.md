# Multi-Select

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Input area (shows selected chips) + Dropdown (checkbox list with filter)

**States:** Closed (shows selected chips) · Open (dropdown visible) · Empty (placeholder text) · Searching (filter input active)

**Selected items:** Removable chips (× button). Compact chip-row inside input area. Overflow: "+N more" chip.

**Dropdown:** Checkbox list with filter input at top. Select all / Deselect all actions. Apply button to confirm (optional — can auto-apply).

**Do:** Show selected items as chips · Allow removal via × · Support Select All · Provide filter for long lists

**Don't:** Force linear scrolling through 50+ items · Omit chip removal · Require Apply button for simple selections

**Accessibility:**
- `role="listbox"` with `aria-multiselectable="true"`
- Each option: `role="option"` with `aria-selected="true/false"`
- Selected chips: each has `aria-label="Remove {option}"` on × button
- Keyboard: Arrow keys navigate, Space toggles selection, Enter closes and applies
- Filter input: same as search-input accessibility

**Token Values:**
| Token | Value |
|-------|-------|
| --multiselect-chip-gap | `4px` |
| --multiselect-filter-debounce | 150ms |
| --multiselect-z-index | `var(--z-dropdown)` |

**Related:** `chip.md`, `chip-row.md`, `checkbox.md`, `search-input.md`, `autocomplete.md`
