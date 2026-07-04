# Comparison Card

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Side-by-side or stacked comparison of two time periods. Each side: period label + value + delta

**Layout:**
- Horizontal: Left (previous) | arrow → | Right (current). Gap: 8px, arrow in center.
- Vertical: Top (current, larger) → Bottom (previous, smaller, muted).

**Period labels:** "This Week" vs "Last Week" · "July 2026" vs "July 2025" · "Today" vs "Yesterday".

**Delta:** Colored percentage/absolute change. Positive (good): tertiary-600, ↑. Negative (bad): error-600, ↓. Neutral: slate-500, →.

**Example:** Steps this week: 52,340 (↑12% vs last week). Weight today: 78.2 kg (↓1.3 kg vs last month).

**Do:** Show both periods clearly · Color-code delta direction · Use concise period labels

**Don't:** Show delta without direction · Use ambiguous period labels · Compare unrelated metrics

**Accessibility:**
- Each period value: labeled clearly (e.g., "This week: 52,340 steps")
- Delta: `aria-label` describing direction + magnitude + comparison (e.g., "Up 12% from last week")
- Arrow icon: `aria-hidden="true"`

**Related:** `card.md`, `stat.md`, `key-value.md`
