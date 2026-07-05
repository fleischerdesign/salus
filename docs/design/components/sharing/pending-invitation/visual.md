## Visual Design

### Card Section
- Card with `--color-warning-50` subtle background tint, 24px padding
- Title: "Pending Invitations", `--font-label-md`, `--color-warning-800`
- Rows below title, gap 12px

### Invitation Row
- Colored icon (20px, metric color, left) + Owner handle (`--font-body-md`, 600) + "wants to share" + Metric name (`--font-body-sm`) + Aggregation chip (Summary/Raw, neutral) + Accept/Decline buttons (right)

### Buttons
| Button | Variant | Icon |
|--------|---------|------|
| Accept | Primary (compact, 32px) | `check` 16px |
| Decline | Ghost (compact, 32px) | `close` 16px |

### States
| State | Visual |
|-------|--------|
| Default | Row visible, buttons active |
| Accepting | Accept button loading (spinner), decline disabled |
| Declining | Decline button loading, accept disabled |
| Done | Row fades out (200ms), removed from DOM |

### Spacing
- Row padding: 8px 0
- Icon↔Handle: 8px
- Handle↔Metric: 4px
- Metric↔Aggregation: 8px
- Buttons: right-aligned, gap 8px
