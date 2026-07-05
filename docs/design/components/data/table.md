# Table

**Tokens:** `--table-header-bg`, `--table-header-font`, `--table-header-color`, `--table-row-hover-bg`, `--table-cell-padding`, `--table-cell-font`, `--table-border`

**Anatomy:** Header row (slate-100 bg, all-caps label-sm) + Body rows (white bg, body-sm)

**States:** Default · Hover (slate-50 row bg) · Active/Selected · Empty ("No data" message in colspan cell)

**Sizes:** Row height: 48px. Cell padding: 12px 16px.

**Spacing:** Table↔Container: inherit from parent

**Responsive:** Full-width. Horizontal scroll on mobile with minimum column widths.

**Do:** Use label-sm ALL CAPS for headers · 48px row height · Add row-hover for dense data

**Don't:** Leave empty cells without placeholder · Omit column headers · Use for layout (use CSS grid)

**Accessibility:**
- `<table>` with `<thead>`, `<tbody>`, `<th>` (header cells with `scope="col"`)
- Caption: `<caption>` element for table title
- Sortable headers: `aria-sort="ascending/descending/none"`, `role="columnheader"`
- Row actions: each action button has distinct `aria-label` (e.g., "Edit user Alice", not just "Edit")
- Empty state: `<td colspan="100%">` with empty state component
- Hover row: `aria-describedby` if hover reveals additional info

**Composition:** Header row (th) + Body rows (td). Body cells may contain: Link, Button, Chip, Icon, Badge, KeyValue. Row actions on right.

**Responsive:** Horizontal scroll container on mobile. Minimum column widths prevent collapse.

**Related:** `empty-state.md`, `chip.md`, `badge.md`, `pagination.md`, `key-value.md`

## Visual Design

### Appearance
- **Border:** `1px solid --color-slate-200` (between rows and columns)
- **Header:** `--color-slate-100` bg, `--font-label-sm` (12px, 500), `--color-slate-700`, uppercase, padding 10px 16px
- **Row:** `#ffffff` bg (default), `--font-body-sm` (14px), padding 12px 16px, height 48px
- **Hover:** `--color-slate-50` bg on entire row

### States
| State | Row Background | Border |
|-------|---------------|--------|
| Default | `#ffffff` | `--color-slate-200` |
| Hover | `--color-slate-50` | `--color-slate-200` |
| Selected/Active | `--color-primary-50` | `--color-slate-200` |
| Empty | Empty state component in colspan cell | — |

### Compact Variant
- Row height: 36px, padding: 8px 12px
- Font: `--font-body-sm` (14px). Header: `--font-label-sm` (12px)

### Cell Content
Allowed: Link, Button, Chip, Badge, Icon, KeyValue, `--font-body-sm` text.
Actions: right-aligned, 4px gap between action buttons.

### Spacing
- Cell padding: 12px 16px (standard), 8px 12px (compact)
- Row height: 48px (standard), 36px (compact)

### Responsive
Full-width with horizontal scroll on mobile. Sticky first column optional. Min column width: 100px.
