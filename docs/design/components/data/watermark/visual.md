## Visual Design

### Appearance
- **Text:** `--font-headline-xl` (36px, 800), `--color-slate-300`, opacity 0.15 (screen), 0.10 (print)
- **Rotation:** -45°
- **Position:** fixed, centered, `pointer-events: none`, `--z-debug` (9999)
- **Repeat:** single instance, centered. Not tiled.

### States
| Context | Opacity | Forced? |
|---------|--------|---------|
| Screen (medical record page) | 0.15 | optional |
| Print (`@media print`) | 0.10 | forced |

### CSS
`position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); pointer-events: none; z-index: 9999;`
