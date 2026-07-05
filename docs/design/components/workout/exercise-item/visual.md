## Visual Design

### Row Layout
- Name: `--font-body-md` (16px, 600), left
- Equipment chip: neutral chip with icon (e.g., `fitness_center` 14px), right of name, gap 8px
- Muscle targets: `--font-body-sm`, `--color-slate-500`, below name, 2px gap
- Video link: ghost link with `play_circle` icon 16px, right-aligned
- Delete button: × 20px ghost, right-aligned, only on hover

### Equipment Chip Colors

| Equipment | Chip Variant | Icon |
|-----------|------------|------|
| Barbell | Neutral (slate) | `fitness_center` |
| Dumbbell | Neutral (slate) | `fitness_center` |
| Machine | Neutral (slate) | `precision_manufacturing` |
| Bodyweight | Neutral (slate) | `accessibility_new` |
| Kettlebell | Neutral (slate) | `fitness_center` |

### States
| State | Row | Actions |
|-------|-----|---------|
| Default | Normal opacity, no actions | Hidden |
| Hover | `--color-slate-50` bg | Actions visible |
| Deleting | Opacity 0.5, pointer-events: none | Hidden |

### Spacing
- Row padding: 12px 16px
- Row gap: 2px (`1px --color-slate-100` divider)
- Name↔Chip: 8px
- Muscle↔Video: 16px
