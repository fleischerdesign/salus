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
