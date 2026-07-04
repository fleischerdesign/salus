# Peer Card

**Anatomy:** Avatar (first letter of handle) + Handle name (+ Remote chip) + Badge (Mutual/Sharing/Reading/Pending) + Metrics list + Footer (expiration, token, revoke)

**States:** Default · Hover (subtle shadow) · Pending (yellow-tinted badge) · Mutual (green-tinted badge)

**Badge variants:** Mutal (bi-directional sharing) · Sharing (outgoing only) · Reading (incoming only) · Pending (not yet accepted)

**Metrics list:** Each metric row shows: colored icon + name + aggregation chip (Summary/Raw) + direction indicator (↗ You share / ↙ shares with you). Outgoing rows show revoke button on hover.

**Remote peers:** Show "Remote" chip with globe icon. Show last sync timestamp if available. Show truncated API token with copy button.

**Footer:** Expiration date (if set) + Revoke All button (only for active outgoing relationships).

**Do:** Group metrics by peer · Show relationship direction · Distinguish remote vs local · Provide revoke per metric

**Don't:** Expose full API tokens · Show Revoke All for pending only · Omit remote sync status
