## Visual Design

### Layout
- Flex row, wrap to next line
- Gap: 8px between chips
- Max 5 visible (read-only / default)

### Variants

| Variant | Overflow | Interaction |
|---------|----------|------------|
| Read-only | None (all visible, wraps) | None |
| Collapsible | "+N more" chip shows remaining count | Click toggles all chips visible |
| Interactive (removable) | None | Each chip has × dismiss button |

### "+N more" Chip
Neutral variant, `--font-label-sm`. Click toggles: expand (show all) / collapse (show first 5). Chevron rotates 180°.

### Spacing
- Chip↔Chip gap: 8px
- Row height: auto (wraps naturally)
- Top/bottom margin: 4px
