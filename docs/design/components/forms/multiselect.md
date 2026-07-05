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

## Visual Design

### Appearance
- **Trigger area:** matches input (44px min-height, auto height per chips), slate-50 bg, slate-300 border
- **Placeholder:** `--color-slate-400`, `--font-body-md`, when no chips selected
- **Dropdown:** `#ffffff` bg, `--shadow-lg`, `--radius-md`, max-height 280px scrollable, 4px gap
- **Overflow:** "+N more" chip (neutral variant) when chips exceed visible width

### States

| State | Trigger | Dropdown |
|-------|---------|----------|
| Closed (empty) | Placeholder text | Hidden |
| Closed (selected) | Chips visible | Hidden |
| Open | Border: `--color-primary-500` | Visible |
| Open (filtering) | Filter input focused inside dropdown | Filtered options |

### Selected Chips
- Removable chips inside trigger: neutral variant with × dismiss button
- Chip gap: 4px. Wrap to next line when full width.
- Chip removal: instant, no confirmation
- All chip variants: see `chip.md`

### Dropdown
- Filter input at top (matches search-input.md)
- Select All / Deselect All ghost buttons above list
- Checkbox list: checkbox + label per option. Gap: 4px
- Option padding: 8px 12px. Hover: `--color-slate-50`

### Spacing
- Trigger padding: 6px 8px (compact for chips)
- Chips gap: 4px
- Filter↔List gap: 8px
- Dropdown↔Trigger gap: 4px
