## Visual Design

### Appearance
- **Layout:** Radio group (horizontal), gap 8px
- **Option:** 36×36px, `--radius-md`, ghost style. Icon: 20px. Selected: `--color-primary` bg, `--color-on-primary` text
- **Icons:** System: `brightness_auto`, Light: `light_mode`, Dark: `dark_mode`
- **Labels:** hidden (icon-only), tooltip on hover

### States
| State | Background | Icon Color |
|-------|-----------|------------|
| Default (unselected) | transparent | `--color-slate-500` |
| Hover (unselected) | `--color-slate-100` | `--color-slate-700` |
| Selected | `--color-primary` | `--color-on-primary` |
| Focus | Standard focus ring | — |

### Spacing
- Gap: 8px between options
- Option size: 36×36px, icon: 20px
- Group padding: 4px
