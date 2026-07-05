## Visual Design

### Header
- Avatar (36px SM, left) + Handle (`--font-headline-md`, 600) + Badge (right)
- Remote peers: `globe` icon 16px + "[remote]" chip after handle

### Badges

| Badge | Background | Text | Meaning |
|-------|-----------|------|---------|
| Mutual | `--color-tertiary-50` | `--color-tertiary-700` | Bidirectional sharing |
| Sharing | `--color-primary-50` | `--color-primary-700` | Outgoing only |
| Reading | `--color-secondary-50` | `--color-secondary-700` | Incoming only |
| Pending | `--color-warning-50` | `--color-warning-700` | Not yet accepted |

### Metric List
- Each row: colored icon 20px + Metric name (`--font-body-sm`) + Aggregation chip (Summary/Raw) + Direction indicator (↗ You share / ↙ shares with you)
- Revoke button (× 20px, ghost, `--color-error-600`): visible on hover, right-aligned
- Gap between metric rows: 8px

### Footer
- Expiration: `--font-body-sm`, `--color-slate-500`, if set
- API token: truncated (`s3ns0r...2026`), with copy button for remote peers
- Revoke All: ghost danger button, right-aligned

### Spacing
- Card padding: 24px
- Header↔Metrics: 16px
- Metrics↔Footer: 16px
