# Autocomplete / Combobox

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Input field + Dropdown suggestion list that filters as user types

**States:** Idle · Typing (suggestions appear after 150ms debounce, min 2 chars) · Loading (spinner in input) · No results ("No matches found") · Selected (value filled, dropdown closed)

**Suggestions list:** Max 8 visible items, scroll for more. Hover: slate-50 bg. Active: primary-50 bg. Highlight matched text in bold.

**Input:** Same as standard input. Clear button (×) when text present. Arrow keys navigate suggestions. Enter selects. Escape closes.

**Accessibility:** `role="combobox"`, `aria-expanded`, `aria-activedescendant`. `aria-autocomplete="list"`.

**Do:** Debounce input · Highlight matching text · Support keyboard navigation · Show no-results state

**Don't:** Search on every keystroke · Show >8 suggestions without scroll · Omit keyboard support

**Accessibility:**
- `role="combobox"` on input, `aria-expanded="true/false"`, `aria-autocomplete="list"`
- `aria-activedescendant` tracking the currently highlighted suggestion
- `role="listbox"` on suggestions container, `role="option"` on each item
- Keyboard: Arrow Up/Down navigates, Enter selects, Escape closes
- No results: "No matches found" announced via `aria-live`

**Token Values:**
| Token | Value |
|-------|-------|
| --autocomplete-debounce | 150ms |
| --autocomplete-min-chars | 2 |
| --autocomplete-max-items | 8 |
| --autocomplete-item-padding | `8px 12px` |
| --autocomplete-match-highlight | `{colors.primary-600}` bold |
| --autocomplete-z-index | `var(--z-dropdown)` |

**Responsive:** Full-width on mobile. Dropdown constrained to viewport.

**Related:** `input.md`, `search-input.md`, `multiselect.md`, `select.md`

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
