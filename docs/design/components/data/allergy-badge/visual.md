## Visual Design

### Severity Levels

| Severity | Dot Color | Text Style | Background | Icon |
|----------|-----------|-----------|------------|------|
| Mild | `--color-warning-500` | `--font-body-sm`, normal | transparent | none |
| Moderate | `--color-warning-700` | `--font-body-sm`, 600 | transparent | none |
| Severe | `--color-error-600` | `--font-body-sm`, bold | transparent | `warning` 20px |
| Anaphylaxis | — | `--font-body-sm`, bold, white | `--color-error-700` | `emergency` 20px |

### Anatomy
- Icon (20px, left) + Allergen name + Severity dot (8px, right)
- Anaphylaxis: full-width pill (chip style, error-700 bg, white text), always first in list
- Layout: chip-row, gap 8px, sorted by severity (anaphylaxis → severe → moderate → mild)

### Spacing
- Icon↔Name: 4px
- Name↔Dot: 4px
- Chip gap: 8px
