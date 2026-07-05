## Visual Design

### Appearance
- **Offscreen (default):** `position: absolute; top: -100%; left: -100%` (completely hidden)
- **Focused:** `position: fixed; top: 8px; left: 50%; transform: translateX(-50%)`, `--color-slate-900` bg, `--color-slate-50` text, `--font-body-md`, padding 12px 24px, `--radius-md`, `--shadow-lg`, `--z-tooltip` (500)
- **Focus ring:** Standard focus ring on focus

### States
| State | Position | Visibility |
|-------|---------|------------|
| Hidden (default) | Offscreen | Not visible, not in visual flow |
| Focused (Tab) | Fixed top-center | Visible, slide-down animation 150ms ease-out |
| Activated (click/Enter) | Moves focus to `#main-content` | Hidden again |

### Animation
Appear on focus: slide-down 150ms ease-out (translateY -100% → 0) + fade-in.
Disappear on blur: instant.

### Spacing
- Padding: 12px 24px
- Top offset: 8px from viewport top
- Radius: `--radius-md` (8px)
