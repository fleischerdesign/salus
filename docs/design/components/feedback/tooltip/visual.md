## Visual Design

### Appearance
- **Background:** `--color-slate-800`
- **Text:** `--color-slate-50`, `--font-body-sm`
- **Padding:** 8px
- **Radius:** 6px
- **Arrow:** 4px, matching bg color, pointing to trigger
- **Max-width:** 280px, text wraps
- **Border:** `1px rgba(255,255,255,0.15)` (subtle edge on dark bg)
- **Z-index:** `--z-tooltip` (500)

### Placement
Auto-positioned, 8px gap from trigger. Preference order: top → bottom → left → right.

### States
| State | Trigger | Visual |
|-------|---------|--------|
| Hidden | — | Not rendered |
| Visible | Hover or Focus | Appears with 150ms delay |
| Dismissed | Mouseleave or Blur | Instant removal |
| Touch | Long-press ≥500ms | Appears, dismisses on tap elsewhere |

### Animation
- Appear: none (instant after delay — avoids motion sickness)
- Dismiss: instant
