# Context Menu

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Trigger element with right-click (or long-press) handler + Floating menu near cursor

**States:** Hidden · Visible (at cursor position, lg shadow, 8px radius, 4px padding) · Dismissed (click outside or Escape)

**Menu items:** 12px horizontal padding, 8px vertical, body-sm font. Hover: slate-50 bg. Separator: 1px slate-200, 4px vertical margin. Destructive items: error-600 text.

**Position:** Auto-flip to stay within viewport. Prefer bottom-right of cursor. Fall back to top-right, bottom-left, etc.

**Accessibility:** Escape closes. Arrow keys navigate items. Enter selects. Focus returns to trigger on close.

**Do:** Use for secondary actions on data rows · Auto-position within viewport · Support keyboard navigation

**Don't:** Show on every element · Use as primary action mechanism · Omit keyboard access

**Token Values:**
| Token | Value |
|-------|-------|
| --context-menu-bg | `#ffffff` |
| --context-menu-shadow | `var(--shadow-lg)` |
| --context-menu-radius | `var(--radius-md)` |
| --context-menu-item-padding | `8px 12px` |
| --context-menu-divider | `1px solid {colors.slate-200}` |
| --context-menu-danger-text | `{colors.error-600}` |
| --context-menu-z-index | `var(--z-tooltip)` |

**Related:** `nav-dropdown.md`, `table.md`, `list-item.md`
