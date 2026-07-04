# KPI Card

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Compact card (icon + value + label + delta) with colored accent border

**States:** Default · Positive trend (tertiary accent) · Negative trend (error accent) · Neutral

**Sizes:** Compact (inline, 3-4 per row) · Standard (card, 2 per row)

**Accent border:** 4px top border, color varies by trend direction and metric type.

**Content:** Metric icon (24px, colored) + Large value (headline-md) + Label (body-sm, muted) + Delta percentage (label-sm, colored arrow).

**Do:** Use for dashboard metric summaries · Show trend direction · Keep compact · Color-code by metric

**Don't:** Use for detailed data (use viz charts) · Overload with info beyond value+label+delta · Mix with unrelated metrics in same row
