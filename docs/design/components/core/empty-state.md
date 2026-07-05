# Empty State

**Anatomy:** Large icon (48px, muted) + Title + Description + Optional CTA button

**States:** Default only.

**Placement:** Centered within the container it replaces (card, grid, feed, table).

**Variants:**

| Container | Icon Size | Title Font |
|-----------|-----------|------------|
| Card | 48px | headline-md |
| Widget | 40px | body-sm |
| Feed | 64px | headline-lg |
| Table cell | 20px | body-sm |

**Do:** Use when data would be present but isn't · Provide actionable CTA ("Create your first...") if user can fix · Keep copy warm and helpful

**Don't:** Show empty state and leave user with no next step · Use technical jargon ("No entities returned") · Show loading skeleton and empty state simultaneously

**Accessibility:**
- Icon: `aria-hidden="true"` (purely decorative)
- Container: `role="status"` if dynamically inserted via HTMX
- CTA button: focusable, clear label
- Use semantic heading for title (`<h3>`)

**Composition:** Contains: Icon + Title + Description + optional Button. Placed inside parent container (Card, Table, Feed).

**Related:** `skeleton.md`, `spinner.md`, `card.md`, `table.md`

## Visual Design

### Appearance
Vertical stack, centered in parent. Icon → Title → Description → CTA button.

### Variants by Container

| Container | Icon Size | Icon Opacity | Title Font | Description Font | CTA |
|-----------|-----------|-------------|------------|-----------------|-----|
| Card | 48px | 0.4 | `--font-headline-md` | `--font-body-sm` | Optional |
| Widget | 40px | 0.4 | `--font-body-sm` (600) | `--font-caption` | Optional |
| Feed / Page | 64px | 0.4 | `--font-headline-lg` | `--font-body-md` | Yes |
| Table cell | 20px | 0.4 | `--font-label-sm` | None | None |
| Inline | 20px | 0.4 | `--font-body-sm` (600) | None | None |

### Colors
- Icon: `--color-slate-400`, opacity 0.4
- Title: `--color-slate-700`
- Description: `--color-slate-500`, max-width 360px

### Spacing
- Icon↔Title: 16px
- Title↔Description: 8px
- Description↔CTA: 24px
