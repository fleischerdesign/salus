# Date Picker

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Input field (shows selected date) + Calendar icon + Dropdown calendar panel

**Calendar panel:** Month/year header with prev/next arrows + Day grid (7 columns, Su-Sa headers) + Today indicator

**States:** Closed · Open · Date selected · Range selected (start/end/in-range) · Disabled dates

**Interaction:** Click input opens panel. Click date selects and closes. Arrow keys navigate within open panel. Escape closes.

**Format:** Display: locale-aware (e.g. "Jul 4, 2026"). Value: ISO 8601 (YYYY-MM-DD).

**Do:** Support keyboard navigation · Show today indicator · Allow typing date directly · Respect locale

**Don't:** Reinvent native picker on mobile (use `<input type="date">`) · Omit month/year quick navigation · Break with keyboard

**Accessibility:**
- Input: `<input type="date">` with `<label>` association
- Calendar button: `aria-label="Open date picker"`, `aria-expanded` on toggle
- Calendar panel: `role="dialog"` or `role="application"` with live region
- Days: `role="grid"`, each cell `role="gridcell"` with `aria-selected` and `aria-label`
- Keyboard: Arrow keys navigate days, Page Up/Down changes months, Enter selects, Escape closes
- Today: `aria-current="date"`

**Token Values:**
| Token | Value |
|-------|-------|
| --date-picker-input-width | `200px` |
| --date-picker-calendar-width | `280px` |
| --date-picker-cell-size | `36px` |
| --date-picker-today-border | `2px solid {colors.primary}` |
| --date-picker-selected-bg | `{colors.primary}` |
| --date-picker-header-font | `var(--font-label-md)` |
| --date-picker-z-index | `var(--z-dropdown)` |

**Related:** `input.md`, `day-navigator.md`, `modal.md`

## Visual Design

### Appearance
- **Input:** matches standard Input (44px), 200px width
- **Calendar icon:** 20px, `--color-slate-400`, right side 12px
- **Calendar panel:** `#ffffff` bg, `--shadow-lg`, `--radius-md`, 280px width, `--z-dropdown`
- **Header:** `--font-label-md`, month/year centered, prev/next arrow buttons (28×28px ghost)
- **Day grid:** 7 columns (Su-Sa), `--font-label-sm` headers, `--color-slate-400` headers
- **Day cell:** 36×36px, `--font-body-sm`, rounded-sm

### States

| Element | Default | Hover | Selected | Today | Disabled |
|---------|---------|-------|----------|-------|----------|
| Day cell | transparent | `--color-slate-100` | `--color-primary` bg, white text | `2px solid --color-primary` border | `--color-slate-300` text |
| Input trigger | slate-300 border | slate-400 border | — | — | opacity 0.5 |

### Calendar navigation
- Month/year header: prev/next chevron buttons (20px). Click changes month.
- Today button below grid: ghost button, `--font-label-sm`, jumps to today's date.

### Spacing
- Cell size: 36×36px, 2px gap
- Panel padding: 12px
- Header↔Grid gap: 8px

### Responsive
Desktop: calendar panel attached to input. Mobile: use native `<input type="date">`.
