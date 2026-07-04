# Donut / Ring Chart

> Status: **Design spec only — not yet implemented.**

**Anatomy:** SVG ring showing proportion of parts to whole. Center: total value or label.

**Segments:** Stroke-dasharray based on proportions. Colors from color family tokens. 3-6 segments max.

**Center text:** Large total value (headline-md, bold) + Label (caption, muted). Or: primary metric + unit.

**Legend:** Below chart, matching segment colors. Dots (8px) + label + value + percentage. Can be hidden on small widgets.

**Animation:** Stroke-dasharray transition 800ms ease-out on load.

**Do:** Use for 3-6 segment proportions · Show legend · Animate on load · Put key number in center

**Don't:** Use for >6 segments · Use for time series · Omit labels/legend
