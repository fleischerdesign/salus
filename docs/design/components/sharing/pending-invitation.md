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

**Related:** `card.md`, `chip.md`, `icon.md`, `button.md`, `peer-card.md`, `invite-modal.md`
