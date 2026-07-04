# Radio Group

**Tokens:** Reuses `--btn-sm-*` tokens

**Anatomy:** Group label (label-sm) + Option list (horizontal or vertical button-group)

**States:** Default · Selected/Active (btn-sm.active: primary bg, white text, primary border) · Focus

**Implementation:** Hidden radio inputs with visible button labels. Wrapped in form with `onchange`, or HTMX-driven.

**Do:** Use for single-select from small set (2-5 options) · Style as button group for visual clarity · Provide group label

**Don't:** Use for >5 options (use Select) · Use without visible label · Mix horizontal and vertical
