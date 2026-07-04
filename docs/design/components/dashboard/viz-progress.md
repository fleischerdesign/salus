# Viz: Progress

**Anatomy:** Target value + Current progress ring/bar + Percentage + Optional sub-label

**Sizes:**
- Small: SVG progress ring (90×90px), percentage centered. Ring color: primary. Track: slate-100.
- Medium/Large: Horizontal bar (22px height, rounded-full) with percentage overlay. Fill: primary, Track: slate-100. 4px sub-label text above.

**Animation:** Fill width transition 0.6s ease. Ring stroke-dasharray transition 0.8s ease.

**States:** Below target (primary fill) · At target (tertiary/success) · Over target (warning).

**Do:** Use for goal progress · Show both current and target · Animate transitions

**Don't:** Use for non-goal metrics · Omit target value · Hardcode fill colors (use status variants)
