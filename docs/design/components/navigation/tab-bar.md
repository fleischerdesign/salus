# Tab Bar

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Horizontal row of tab triggers + Content area below (shows active tab content)

**States:** Active tab (primary text + 2px primary bottom-border) · Inactive tab (slate-600 text, transparent border) · Hover (slate-100 bg) · Disabled (opacity 0.5)

**Triggers:** label-md font, padding: 12px 16px, min-width: 90px. Icon optional (left of label). 2px bottom border for active indicator.

**Content:** Loaded via HTMX on tab click. Preserves active tab state in URL hash or query param.

**Responsive:** Overflow tabs scroll horizontally on mobile (with fade indicators at edges).

**Do:** Use for 3-8 related views · Preserve active tab in URL · Scroll overflow on mobile · Show clear active indicator

**Don't:** Use for >8 tabs · Use as primary navigation (use TopAppBar) · Omit URL state preservation

**Accessibility:**
- `role="tablist"` on container, `role="tab"` on each trigger, `role="tabpanel"` on each content panel
- Active tab: `aria-selected="true"`, `tabindex="0"`. Inactive: `aria-selected="false"`, `tabindex="-1"`
- Keyboard: Left/Right Arrow keys navigate between tabs, Home/End to first/last
- `aria-controls="panel-id"` on tab linking to `id` on tabpanel
- Content loaded via HTMX: `aria-live="polite"` on tabpanel

**Token Values:**
| Token | Value |
|-------|-------|
| --tab-font | `var(--font-label-md)` |
| --tab-padding | `12px 16px` |
| --tab-min-width | `90px` |
| --tab-active-border | `2px solid {colors.primary}` |
| --tab-active-text | `{colors.primary}` |
| --tab-hover-bg | `{colors.slate-100}` |

**Composition:** Tab triggers (row) + Tab panels (content area). Only one panel visible at a time.

**Related:** `tabbed-sidebar.md`, `top-app-bar.md`, `link.md`
