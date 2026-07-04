# Pending Invitation

**Anatomy:** Card section + Invitation rows (colored icon + owner name + metric name + aggregation + Accept/Decline buttons)

**States:** Visible (when invitations exist) · Hidden (when none) · Accepting · Declining

**Interaction:** Accept: hx-post to `/sharing/{id}/accept`. Decline: hx-post to `/sharing/{id}/decline`. Row removed on success, HX-Refresh triggers full page update.

**Do:** Show at top of Connections page · Distinguish metric visually · Confirm before decline · Refresh peer list after accept

**Don't:** Omit aggregation type · Show without colored metric icon · Leave stale invitations
