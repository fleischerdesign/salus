# Gauge / Meter

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Half-circle arc with needle or fill indicating current value within a range

**Segments:** 3 qualitative zones on the arc: Low (warning-400, left), Normal (tertiary-500, center), High (error-400, right). Boundary values configurable.

**States:** Low value (needle in warning zone) · Normal (needle in tertiary zone) · High (needle in error zone)

**Center text:** Current value (headline-lg, bold) + Unit (body-sm, muted) + Optional label (caption, muted)

**Examples:** Heart rate (60–100 bpm normal range), SpO2 (95–100% normal), Temperature (36.1–37.2°C normal).

**Animation:** Needle rotates into position on load (600ms ease-out).

**Do:** Use for range-based vitals · Show 3 qualitative zones · Put value in center · Animate on load

**Don't:** Use for non-range metrics · Omit zone labels · Use for exact measurements (use stat)
