# Timeline

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Vertical line (left) + Event dots + Event cards (right). Chronological, newest first or oldest first.

**Line:** 2px width, slate-200. Full height of timeline container. 16px left padding.

**Event dot:** 12px circle, filled (primary-500). Connected to line. First event: larger dot (16px). Active/selected: 4px primary ring.

**Event card:** Connected to dot via horizontal connector line (16px). Card content: timestamp (caption, muted) + title (body-md, semi-bold) + description (body-sm) + optional icon (colored, left of title).

**Variants:**
- Activity timeline (workouts, meals, symptoms — time-of-day, one day)
- History timeline (lab results, diagnoses — date, months/years span)
- Log timeline (system events, access log — timestamp, compact)

**Connector lines:** Dashed for ongoing events, solid for completed events.

**Do:** Use consistent spacing · Show clear time progression · Vary dot size for significance · Color-code by event type

**Don't:** Mix chronological directions · Omit timestamps · Use for >50 events without pagination

**Accessibility:**
- Use `<ol>` (ordered list) for chronological timeline
- Each event: `<li>`, with `<time>` element for timestamp
- Event dot: `aria-hidden="true"` (purely decorative)
- Connector line: `aria-hidden="true"`
- Grouped by date: use heading for each date group

**Token Values:**
| Token | Value |
|-------|-------|
| --timeline-line-width | 2px |
| --timeline-line-color | `{colors.slate-200}` |
| --timeline-dot-size | 12px |
| --timeline-dot-active-size | 16px |
| --timeline-dot-color | `{colors.primary-500}` |
| --timeline-dot-active-ring | `4px {colors.primary-200}` |
| --timeline-connector-length | 16px |

**Responsive:** Event cards take full width on mobile (line moves to minimal left margin).

**Related:** `list-item.md`, `card.md`, `chip.md`, `status-dot.md`
