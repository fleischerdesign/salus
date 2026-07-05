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

## Visual Design

### Appearance
- **Tab:** `--font-label-md`, padding 12px 16px, min-width 90px, text centered
- **Active tab:** `--color-primary` text, `2px solid --color-primary` bottom border
- **Inactive tab:** `--color-slate-600` text, transparent bottom border
- **Hover:** `--color-slate-100` bg
- **Icon (optional):** 20px, left of label, gap 8px

### Container
- Horizontal row, bottom border: `1px solid --color-slate-200` (full width)
- Active tab border overlaps container border (z-index +1)

### States

| State | Text | Bottom Border | Background |
|-------|------|--------------|------------|
| Inactive | `--color-slate-600` | transparent 2px | transparent |
| Inactive hover | `--color-slate-700` | transparent 2px | `--color-slate-100` |
| Active | `--color-primary` | `2px solid --color-primary` | transparent |
| Disabled | `--color-slate-300` | transparent 2px | transparent, opacity 0.5 |

### Variants
| Variant | Use |
|---------|-----|
| Standard | Top/bottom of content area |
| With icons | Icon + label per tab |
| Compact | Reduced padding (8px 12px), `--font-body-sm` |

### Spacing
- Tab padding: 12px 16px
- Min-width: 90px
- Icon↔Label: 8px
- Tab↔Tab: 0px (seamless)

### Mobile
Tabs overflow scroll horizontally. Fade indicators (gradient overlay) at left/right edges when content overflows.
