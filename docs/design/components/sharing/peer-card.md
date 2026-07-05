# Peer Card

**Anatomy:** Avatar (first letter of handle) + Handle name (+ Remote chip) + Badge (Mutual/Sharing/Reading/Pending) + Metrics list + Footer (expiration, token, revoke)

**States:** Default · Hover (subtle shadow) · Pending (yellow-tinted badge) · Mutual (green-tinted badge)

**Badge variants:** Mutal (bi-directional sharing) · Sharing (outgoing only) · Reading (incoming only) · Pending (not yet accepted)

**Metrics list:** Each metric row shows: colored icon + name + aggregation chip (Summary/Raw) + direction indicator (↗ You share / ↙ shares with you). Outgoing rows show revoke button on hover.

**Remote peers:** Show "Remote" chip with globe icon. Show last sync timestamp if available. Show truncated API token with copy button.

**Footer:** Expiration date (if set) + Revoke All button (only for active outgoing relationships).

**Do:** Group metrics by peer · Show relationship direction · Distinguish remote vs local · Provide revoke per metric

**Don't:** Expose full API tokens · Show Revoke All for pending only · Omit remote sync status

**Responsive:** Cards in peer-grid flow 1-3 per row depending on container width. Single column on mobile. Metric rows stack vertically.

**Accessibility:**
- Card: `role="region"` with `aria-label="Connection with {handle}"`
- Badge (Mutual/Sharing/Reading/Pending): `aria-label` describing direction
- Metric rows: each with distinct revoke button, `aria-label="Stop sharing {metric} with {handle}"`
- Remote chip: `aria-label="Remote peer — {domain}"`
- Federation status: `aria-label` describing sync state

**Composition:** Card containing: Avatar + Handle + Badge + Metric list + Footer (expiration, token, revoke). Part of peer-grid in sharing_connections page.

**Related:** `card.md`, `avatar.md`, `chip.md`, `badge.md`, `icon.md`, `btn.md`, `federation-status.md`, `pending-invitation.md`

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
