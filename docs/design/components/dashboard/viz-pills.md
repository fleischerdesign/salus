# Viz: Pills

**Anatomy:** Header (value + unit + delta) + SVG pill chart (110px height) + Color legend

**Sizes:** Medium/Large only. Not available in small.

**Chart:** SVG-rendered pill-shaped segments representing heart rate zones or sleep stages. Segments use ResizeObserver for responsive width. Zones/segments: Awake (warning-400), Light (secondary-400), Deep (primary-400), REM (metric-sleep).

**Legend:** Horizontal, centered below chart. Color dots (8px) + label (label-sm, slate-500).

**Do:** Use for zone/stage breakdowns · Show color legend · Make responsive

**Don't:** Use for trend data (use sparkline) · Omit legend · Hardcode segment colors
