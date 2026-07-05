# Pending Invitation

**Anatomy:** Card section + Invitation rows (colored icon + owner name + metric name + aggregation + Accept/Decline buttons)

**States:** Visible (when invitations exist) · Hidden (when none) · Accepting · Declining

**Interaction:** Accept: hx-post to `/sharing/{id}/accept`. Decline: hx-post to `/sharing/{id}/decline`. Row removed on success, HX-Refresh triggers full page update.

**Do:** Show at top of Connections page · Distinguish metric visually · Confirm before decline · Refresh peer list after accept

**Don't:** Omit aggregation type · Show without colored metric icon · Leave stale invitations

**Responsive:** Invitation rows stack vertically. Accept/Decline buttons stay inline on desktop, may wrap on mobile.

**Accessibility:**
- Card section: `role="region"` with `aria-label="Pending invitations"`
- Each invitation: list item with metric icon + owner + metric + aggregation
- Accept: `aria-label="Accept invitation from {owner} for {metric}"`
- Decline: `aria-label="Decline invitation from {owner} for {metric}"`
- Action feedback: `aria-live="polite"` announcing acceptance/decline

**Composition:** Card section containing invitation rows. Each row: colored icon + owner name + metric + aggregation + Accept/Decline buttons.

**Related:** `card.md`, `chip.md`, `icon.md`, `btn.md`, `peer-card.md`, `invite-modal.md`

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
