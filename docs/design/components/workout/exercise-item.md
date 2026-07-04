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

**Related:** `chip.md`, `link.md`, `button.md`, `icon.md`, `list-item.md`, `plan-card.md`
