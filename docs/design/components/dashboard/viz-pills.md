# Viz: Pills

**Anatomy:** Header (value + unit + delta) + SVG pill chart (110px height) + Color legend

**States:** Default · Hover (per segment via chart-tooltip) · No-data (empty chart with placeholder)

**Sizes:** Medium/Large only. Not available in small.

**Chart:** SVG-rendered pill-shaped segments representing heart rate zones or sleep stages. Segments use ResizeObserver for responsive width. Zones/segments: Awake (warning-400), Light (secondary-400), Deep (primary-400), REM (metric-sleep).

**Legend:** Horizontal, centered below chart. Color dots (8px) + label (label-sm, slate-500).

**Do:** Use for zone/stage breakdowns · Show color legend · Make responsive

**Don't:** Use for trend data (use sparkline) · Omit legend · Hardcode segment colors

**Accessibility:**
- SVG: `role="img"` with `aria-label` describing distribution (e.g., "Sleep: 2h awake, 3h light, 1.5h deep, 2h REM")
- Legend items: list with color dots + text labels
- Color dots: `aria-hidden="true"` (label text describes the segment)

**Related:** `viz-bar.md`, `viz-donut.md`, `sleep-*` tokens
