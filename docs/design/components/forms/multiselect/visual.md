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
