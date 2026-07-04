# Viz: Progress

**Anatomy:** Target value + Current progress ring/bar + Percentage + Optional sub-label

**Sizes:**
- Small: SVG progress ring (90×90px), percentage centered. Ring color: primary. Track: slate-100.
- Medium/Large: Horizontal bar (22px height, rounded-full) with percentage overlay. Fill: primary, Track: slate-100. 4px sub-label text above.

**Animation:** Fill width transition 0.6s ease. Ring stroke-dasharray transition 0.8s ease.

**States:** Below target (primary fill) · At target (tertiary/success) · Over target (warning).

**Do:** Use for goal progress · Show both current and target · Animate transitions

**Don't:** Use for non-goal metrics · Omit target value · Hardcode fill colors (use status variants)

**Accessibility:**
- Ring/bar: `role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="{target}"`
- `aria-valuetext` with human-readable (e.g., "6,234 of 10,000 steps")
- Status color: accompanied by text (not color alone)
- Below target: aria-label includes "X% complete"
- At/above target: aria-label includes "Goal reached"

**Related:** `progress-bar.md`, `stat.md`, `goal-card.md`
