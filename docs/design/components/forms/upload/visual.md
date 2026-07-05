## Visual Design

### Appearance
- **Drop zone:** `2px dashed --color-slate-200`, `--radius-md`, centered content, min-height 120px, cursor pointer
- **Icon:** 40px, `--color-slate-400`
- **Label:** `--font-label-md`, `--color-slate-600`, margin-top 8px
- **Hint:** `--font-body-sm`, `--color-slate-400`, margin-top 4px
- **File list/preview:** below drop zone, gap 8px

### States

| State | Border | Background | Icon Color |
|-------|--------|------------|------------|
| Idle | `2px dashed --color-slate-200` | transparent | `--color-slate-400` |
| Drag-over | `2px solid --color-primary` | `--color-primary-50` | `--color-primary` |
| File selected | `2px solid --color-slate-300` | `--color-slate-50` | `--color-slate-500` |
| Uploading | `2px solid --color-slate-300` | `--color-slate-50` | spinner 24px |
| Complete | `2px solid --color-tertiary-300` | `--color-tertiary-50` | `--color-tertiary-500` (checkmark) |
| Error | `2px solid --color-error-300` | `--color-error-50` | `--color-error-500` |

### Preview Items
- Image thumbnail: 48×48px, `--radius-sm`, `object-fit: cover`
- File icon: 48px generic file type icon
- Filename + size: `--font-body-sm`, to the right of preview
- Remove button: × 20px, `--color-slate-400`, top-right of preview. Hover: `--color-error-500`

### Progress Bar
- Below file list. Height: 4px. Color: `--color-primary`. See `progress-bar.md`.

### Sizes
| Size | Min Height | Icon | Context |
|------|-----------|------|---------|
| Standard | 120px | 40px | Modal, card |
| Inline | 44px | 20px | Compact forms |

### Responsive
- Standard: min-height 80px on mobile
- Inline: full-width
