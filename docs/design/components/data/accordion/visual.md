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
