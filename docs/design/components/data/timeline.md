# Timeline

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Vertical line (left) + Event dots + Event cards (right). Chronological, newest first or oldest first.

**States:** Default · Active/Selected (dot larger, primary ring) · Ongoing (dashed connector) · Completed (solid connector)

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

## Visual Design

### Appearance
- **Line:** 2px width, `--color-slate-200`, full height, 16px left margin
- **Dot:** 12px circle, `--color-primary-500`, filled. Centered on line
- **Active/latest dot:** 16px circle, `--color-primary-500` fill + `4px --color-primary-200` ring
- **Connector:** horizontal line 16px from dot to card, `--color-slate-200`
- **Card:** no shadow, no border. Padding: 8px 0

### Card Content
- Timestamp: `--font-caption` (11px), `--color-slate-500`, above
- Title: `--font-body-md` (16px, 600), `--color-on-surface`
- Description: `--font-body-sm` (14px), `--color-slate-600`, 2px below title
- Optional icon: 20px, left of title, colored by event type

### Connector States
| State | Line Style |
|-------|-----------|
| Completed | Solid `--color-slate-200` |
| Ongoing / In progress | Dashed `--color-slate-200` (2px dashes, 4px gaps) |
| Future / Pending | `--color-slate-300`, lighter |

### Spacing
- Line left: 16px
- Dot centered on line
- Connector: 16px from dot to card
- Card↔Card vertical gap: 0 (items touch). Padding within card: 8px top, 16px bottom

### Variants
| Variant | Dot Color | Line Color |
|---------|-----------|------------|
| Default (generic) | `--color-primary-500` | `--color-slate-200` |
| Success (completed) | `--color-tertiary-500` | `--color-tertiary-200` |
| Warning | `--color-warning-500` | `--color-warning-200` |
| Error | `--color-error-500` | `--color-error-200` |

### Responsive
- Mobile: cards full-width, line at minimal 8px left margin
- Connector: 8px on mobile
