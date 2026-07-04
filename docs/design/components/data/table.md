# Table

**Tokens:** `--table-header-bg`, `--table-header-font`, `--table-header-color`, `--table-row-hover-bg`, `--table-cell-padding`, `--table-cell-font`, `--table-border`

**Anatomy:** Header row (slate-100 bg, all-caps label-sm) + Body rows (white bg, body-sm)

**States:** Default · Hover (slate-50 row bg) · Active/Selected · Empty ("No data" message in colspan cell)

**Sizes:** Row height: 48px. Cell padding: 12px 16px.

**Spacing:** Table↔Container: inherit from parent

**Responsive:** Full-width. Horizontal scroll on mobile with minimum column widths.

**Do:** Use label-sm ALL CAPS for headers · 48px row height · Add row-hover for dense data

**Don't:** Leave empty cells without placeholder · Omit column headers · Use for layout (use CSS grid)
