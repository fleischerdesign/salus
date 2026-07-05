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
