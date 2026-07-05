## Visual Design

### Appearance
- **Background:** `--color-slate-200`
- **Text:** `--color-slate-600`, 600 weight, uppercased, centered
- **Radius:** `--radius-full`
- **Image avatar:** `<img>` with `object-fit: cover`

### Sizes
| Size | Diameter | Font |
|------|----------|------|
| SM | 36px | `--font-label-md` (13px, 600) |
| MD | 40px | `--font-body-md` (16px, 600) |
| LG | 48px | `--font-headline-md` (20px, 600) |

### States
| State | Visual | Duration |
|-------|--------|----------|
| Default | Slate-200 bg, slate-600 text | — |
| Hover (interactive) | Opacity 0.85, cursor pointer | 150ms |
| Active/Selected | `--color-primary-100` bg, `--color-primary-700` text | — |
| With status dot | 8px dot bottom-right, 2px white ring | — |

### Spacing
- Avatar↔Text (in user menu): 12px
- Status dot: 0px from bottom/right edge
