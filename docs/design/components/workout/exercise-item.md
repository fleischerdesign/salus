# Exercise Item

**Anatomy:** Name + Equipment chip + Muscle targets + Video link (optional) + Delete button

**States:** Default · Hover (actions visible) · Deleting (row opacity 0.5 pending confirmation)

**Equipment variants:** Barbell, Dumbbell, Machine, Bodyweight, Kettlebell — each with distinct chip color.

**Delete:** Same pattern as plan-card. Should use targeted removal instead of page reload.

**Form:** Create via modal form (name, equipment dropdown, muscles text, video URL). Edit via same form pre-filled.

**Do:** Show equipment type · Link to video tutorial · Keep delete accessible

**Don't:** Use page reload for CRUD · Omit muscle target info · Show without equipment context

**Responsive:** Flex-wrap: equipment chips and muscle targets wrap below name on narrow screens.

**Accessibility:**
- Item: list item with `aria-label="Exercise: {name}, {equipment}"`
- Equipment chip: `aria-label="Equipment: {type}"`
- Muscle targets: `aria-label="Target muscles: {comma-separated list}"`
- Video link: `aria-label="Video tutorial for {name}"`
- Delete: `aria-label="Delete exercise: {name}"` with confirmation

**Related:** `chip.md`, `link.md`, `btn.md`, `icon.md`, `list-item.md`, `plan-card.md`

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
