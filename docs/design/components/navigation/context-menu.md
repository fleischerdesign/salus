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

## Visual Design

### Appearance
- **Background:** `#ffffff`
- **Shadow:** `--shadow-lg`
- **Radius:** `--radius-md` (8px)
- **Padding:** 4px (vertical)
- **Min-width:** 160px
- **Z-index:** `--z-tooltip` (500)

### Menu Items
- **Padding:** 8px 12px, `--font-body-sm`
- **Default:** transparent bg, `--color-on-surface`
- **Hover:** `--color-slate-50` bg
- **Destructive:** `--color-error-600` text (e.g., "Delete", "Revoke")
- **Disabled:** opacity 0.5, not clickable

### Separator
1px `--color-slate-200`, 4px vertical margin.

### Positioning
Auto-flip to stay in viewport. Preference: bottom-right of trigger → top-right → bottom-left → top-left. Offset: 4px from trigger.

### States
| State | Visual |
|-------|--------|
| Hidden | Not in DOM or `display: none` |
| Visible | Appears at position, shadow, no animation |
| Dismissed | Removed on click-outside or Escape |

### Spacing
- Item padding: 8px 12px
- Separator: 4px margin, 1px height
