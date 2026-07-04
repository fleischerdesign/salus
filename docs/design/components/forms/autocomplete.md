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

**Related:** `input.md`, `search-input.md`, `multi-select.md`, `select.md`
