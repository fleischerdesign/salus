# Accordion

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Header bar (clickable) + Collapsible content panel

**States:** Collapsed (chevron right, content hidden) · Expanded (chevron down, content visible) · Disabled (cannot expand)

**Header:** Full-width, padding 12px 16px, body-md font, cursor pointer, slate-200 border-bottom. Chevron icon: 20px, slate-500, transition: 200ms rotate.

**Content:** Padding 16px. Slide-down animation (200ms ease-out). No border-bottom on last expanded item.

**Group:** Multiple accordion items stacked. Only one expanded at a time (default) or multiple (configurable).

**Do:** Use for progressive disclosure · Animate expand/collapse · Show chevron direction clearly
**Don't:** Use for single item (use card) · Omit animation (jarring) · Hide critical information (put in expanded by default)

**Responsive:** Full-width on all viewports. Item headers stack vertically; no horizontal layout adaption needed.

**Accessibility:**
- Header: `<button>` with `aria-expanded="true/false"`, `aria-controls="accordion-panel-{id}"`
- Panel: `role="region"`, `aria-labelledby` referencing header button
- Icon/chevron: `aria-hidden="true"` (state communicated by aria-expanded)
- Keyboard: Enter/Space toggles expansion

**Token Values:**
| Token | Value |
|-------|-------|
| --accordion-header-padding | `12px 16px` |
| --accordion-header-font | `var(--font-body-md)` |
| --accordion-content-padding | `16px` |
| --accordion-border-color | `{colors.slate-200}` |
| --accordion-chevron-size | 20px |
| --accordion-transition | `var(--duration-normal) var(--ease-out)` |

**Composition:** Multiple sections, each with: Header (Button + Chevron) + Panel (content). Only one open at a time (configurable).

**Related:** `card.md`, `icon.md`, `btn.md`

## Visual Design

### Appearance
- **Header:** full-width, padding 12px 16px, `--font-body-md`, `--color-on-surface`, cursor pointer, `1px solid --color-slate-200` bottom border
- **Chevron:** 20px, `--color-slate-500`, right side. Rotates 180° on expand
- **Content:** padding 16px, no border-top, slide-down animation 200ms ease-out
- **Last item:** no bottom border when expanded

### States

| State | Chevron | Content | Border |
|-------|---------|---------|--------|
| Collapsed | → (right) | Hidden, height 0 | Bottom border visible |
| Collapsed hover | → right, `--color-slate-700` | Hidden | Bottom border visible |
| Expanded | ↓ (down) | Visible | Bottom border visible |
| Disabled | → right, `--color-slate-300` | Hidden | Bottom border, opacity 0.5 |

Chevron transition: 200ms rotate ease-out.

### Group
- Multiple accordion items stacked
- Gap: 0 (items touch via shared borders)
- Configurable: single-expand (one open) or multi-expand

### Spacing
- Header padding: 12px 16px
- Content padding: 16px
- Chevron size: 20px, right-aligned, 16px from right
