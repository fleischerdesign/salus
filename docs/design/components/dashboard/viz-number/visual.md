## Visual Design

### Sizes

| Size | Layout | Value Font | Unit | Delta |
|------|--------|-----------|------|-------|
| Small (compact) | Icon + Value + Unit inline | `--font-headline-md` (20px, 600) | `--font-body-sm` | Right of unit |
| Medium/Large | Value + Unit stacked, sub-label below | `--font-headline-lg` (28px, 700) | `--font-body-md` | Below or right |

### Delta

| Direction | Color | Icon | Font |
|-----------|-------|------|------|
| Positive | `--color-tertiary-600` | ↑ | `--font-label-sm` |
| Negative | `--color-error-600` | ↓ | `--font-label-sm` |
| Neutral | `--color-slate-500` | → | `--font-label-sm` |

### Formatting
- Steps: `8,432` (comma-separated)
- Weight: `78.2 kg` (1 decimal)
- Heart rate: `72 bpm` (integer)
- Sleep: `7h 32m`
- No data: `"--"` em dash, `--color-slate-400`

### Spacing
- Value↔Unit: 4px
- Value↔Delta: 8px (right) or 4px (below)
- Sub-label↔Value: 4px above
