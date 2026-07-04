# Skeleton Loader

**Anatomy:** Animated placeholder rectangles matching expected content shape.

**States:** Active (pulsing 1.8s animation) · Replaced (when content loads)

**Animation:** `skeleton-pulse` keyframe: opacity 0.4 → 0.75 → 0.4, 1.8s cubic-bezier.

**Variants:**
- Text line: 100% width, 14px height, rounded-sm
- Card: full card dimension, rounded-md
- Widget: widget-chrome + placeholder body
- Chart: rectangular area with subtle border

**Do:** Use during initial load · Match skeleton shape to expected content · Show skeleton in dashboards, feeds, tables

**Don't:** Show skeleton for <300ms loads (flash) · Use skeleton for error states · Mix skeleton and real content in same area
