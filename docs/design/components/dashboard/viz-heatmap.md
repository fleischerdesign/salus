# Heatmap / Activity Calendar

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Grid of colored cells (7 columns × N rows). Each cell = one day. Color intensity shows value magnitude. Like GitHub contributions graph.

**Color scale:** 5-level sequential. Empty (slate-100, no data) → L1 (primary-50, low) → L2 → L3 → L4 (primary-700, high).

**States:** No data (empty cell, slate-100) · Data (colored cell) · Today (border: 2px primary-500) · Hover (tooltip: date + value + unit)

**Row labels:** Month names on left. Column headers: M T W T F S S (or S M T W T F S).

**Do:** Use sequential color scale · Show tooltip on hover · Highlight today · Show month labels

**Don't:** Use >5 color steps · Omit legend · Show without date context · Use diverging scale
