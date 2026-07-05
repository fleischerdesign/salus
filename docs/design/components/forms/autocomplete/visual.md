## Visual Design

### Appearance
- **Input:** matches standard Input (44px, slate-50 bg, slate-300 border)
- **Clear button:** 20px ×, `--color-slate-400`, right side, when text present
- **Loading spinner:** 16px, replaces clear button while fetching
- **Dropdown:** `#ffffff` bg, `--shadow-lg`, `--radius-md`, max-height 280px scrollable, 4px gap from input

### Suggestion Items

| State | Background | Text |
|-------|-----------|------|
| Default | transparent | `--color-on-surface` |
| Hover | `--color-slate-50` | `--color-on-surface` |
| Active (keyboard) | `--color-primary-50` | `--color-primary-700` |

Item padding: 8px 12px. Matched text: `--color-primary-600`, bold weight. Max 8 visible items.

### States

| State | Input | Dropdown | Right Element |
|-------|-------|----------|---------------|
| Idle | Placeholder text | Hidden | None |
| Typing (<2 chars) | Text visible | Hidden | None |
| Typing (≥2 chars) | Text + debounce 150ms | Loading → suggestions | Clear × |
| Loading | Text, disabled | Spinner 16px | Spinner |
| Open with results | Text, focused | Suggestions visible | Clear × |
| No results | Text, focused | "No matches found" (slate-400, centered) | Clear × |
| Selected | Selected value | Closed | Clear × |

### Spacing
- Input: standard (44px, 10px 12px)
- Dropdown↔Input gap: 4px
- Item padding: 8px 12px
