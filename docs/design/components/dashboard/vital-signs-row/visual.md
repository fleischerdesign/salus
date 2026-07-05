## Visual Design

### Each Vital Card

| Element | Spec |
|---------|------|
| Icon | 24px, colored per vital type |
| Value | `--font-headline-md` (20px, 600), `--color-on-surface` |
| Unit | `--font-body-sm` (14px), `--color-slate-500`, after value |
| Label | `--font-label-sm` (12px), `--color-slate-500`, below value |
| Trend arrow (optional) | 16px, right of value |

### Status Indicators

| Status | Chip Variant | Dot Color |
|--------|-------------|-----------|
| Normal | Success (tertiary) | `--color-tertiary-500` |
| Borderline | Warning (amber) | `--color-warning-500` |
| Abnormal | Error (red) | `--color-error-500` |
| No data | "--" in `--color-slate-400` | — |

Status chip shown below value (4px gap), `--font-label-sm`.

### Layout
- Flex row, gap 16px
- Each card: flex-1, min-width 140px, padding 12px
- Wrap on mobile

### Spacing
- Card↔Card gap: 16px
- Min card width: 140px
- Icon↔Content gap: 8px

### Responsive
Desktop: all 5 in row. Tablet: 2-3 per row. Mobile: 1 per row, full-width.
