# Viz: Bar (Segmented)

**Anatomy:** Header (value + unit) + Segmented horizontal bar (8px height) + Legend

**States:** Default · Hover (tooltip per segment on medium+ widgets) · No-data ("--" placeholder)

**Sizes:** Medium/Large only. Legend hidden on small widgets.

**Bar:** Rounded-full segments. Segment colors: protein (metric-heart-rate), carbs (secondary-400), fat (warning-400). Bar width: proportional to macro distribution.

**Legend:** Color dots (8px) + label (label-sm, slate-500) + value. Two-row wrapped layout.

**Do:** Use for composition/distribution data · Show proportional segments · Hide legend on small

**Don't:** Use for time-series · Use without legend on medium+ widgets · Hardcode segment colors

**Accessibility:**
- Bar: `role="img"` with `aria-label` describing composition (e.g., "Macros: 45% protein, 30% carbs, 25% fat")
- Legend: same as viz-pills legend accessibility
- Segments: proportional width match percentages in aria-label

**Related:** `viz-donut.md`, `viz-pills.md`, `viz-number.md`
