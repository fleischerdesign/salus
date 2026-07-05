# Search Input

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Search icon (left) + Input field + Clear button (appears when text present, X icon) + Optional filter dropdown

**States:** Empty · Typing (clear button visible) · Searching (spinner replaces search icon) · Results · No results

**Debounce:** 300ms before triggering search. Results load via HTMX.

**Clear button:** 20px X icon, slate-400, absolute positioned right. Click clears input and resets results.

**Do:** Use for filtering/searching data · Debounce input · Show clear button · Show "No results" when empty

**Don't:** Search on every keystroke (use debounce) · Hide clear button · Use placeholder as only label

**Accessibility:**
- `<input type="search">` (semantic HTML)
- Label: visible or `aria-label="Search"`
- Clear button: `aria-label="Clear search"`
- Results: `aria-live="polite"` announces count ("5 results found")
- No results: "No matches found" in live region

**Token Values:**
| Token | Value |
|-------|-------|
| --search-icon-size | 20px |
| --search-icon-color | `{colors.slate-400}` |
| --search-clear-btn-size | 20px |
| --search-debounce-ms | 300ms |
| --search-min-chars | 2 |

**Related:** `input.md`, `autocomplete.md`, `icon.md`, `btn.md`

## Visual Design

### Appearance
- **Input:** matches standard Input (44px, slate-50 bg, slate-300 border, rounded-md)
- **Search icon:** 20px, `--color-slate-400`, positioned 12px from left
- **Clear button:** 20px × icon, `--color-slate-400`, positioned 12px from right, appears when text present
- **No results message:** `--font-body-sm`, `--color-slate-400`, centered, padding 16px

### States

| State | Icon (left) | Right Element | Border |
|-------|------------|---------------|--------|
| Empty | Search icon | none | `--color-slate-300` |
| Typing | Search icon | Clear × button | `--color-slate-300` |
| Searching | Spinner 16px replaces icon | Clear × | `--color-slate-300` |
| Focus | Search icon | Clear × (if text) | `--color-primary-500` + ring |
| No results | Search icon | Clear × | `--color-slate-300` |

### Search icon ↔ spinner transition
- When searching: search icon fades out → spinner fades in (150ms)
- When results load: spinner fades out → search icon fades in (150ms)

### Spacing
- Left padding: 38px (icon space: 12px + 20px + 6px)
- Right padding: 38px (clear button space)
- Input padding (no icon zone): 10px top/bottom
