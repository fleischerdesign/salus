# Chip Row / Tag Group

**Anatomy:** Horizontal row of chips, wrapping to next line

**States:** Default · Overflow ("+3 more" collapsed chip when >5 chips)

**Spacing:** 8px gap between chips. Row height auto-adjusts with wrap.

**Variants:**
- Read-only: static chip group (status indicators, tags)
- Interactive: removeable chips with close (×) button, for multi-select or filter pills
- Collapsible: show first 5 chips + "+N more" toggle

**Do:** Let chips wrap naturally · Use with chip component · Show overflow count

**Don't:** Force single row with scroll · Mix chip variants in same row · Omit spacing

**Accessibility:**
- Container: `<ul>` with `<li>` for each chip (semantic list)
- Overflow: "+N more" chip is focusable, reveals hidden chips on click
- Removable chips: × button in each chip with aria-label

**Related:** `chip.md`, `multiselect.md`, `badge.md`

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
