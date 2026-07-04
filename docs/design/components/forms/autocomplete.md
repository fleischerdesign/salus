# Autocomplete / Combobox

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Input field + Dropdown suggestion list that filters as user types

**States:** Idle · Typing (suggestions appear after 150ms debounce, min 2 chars) · Loading (spinner in input) · No results ("No matches found") · Selected (value filled, dropdown closed)

**Suggestions list:** Max 8 visible items, scroll for more. Hover: slate-50 bg. Active: primary-50 bg. Highlight matched text in bold.

**Input:** Same as standard input. Clear button (×) when text present. Arrow keys navigate suggestions. Enter selects. Escape closes.

**Accessibility:** `role="combobox"`, `aria-expanded`, `aria-activedescendant`. `aria-autocomplete="list"`.

**Do:** Debounce input · Highlight matching text · Support keyboard navigation · Show no-results state

**Don't:** Search on every keystroke · Show >8 suggestions without scroll · Omit keyboard support
