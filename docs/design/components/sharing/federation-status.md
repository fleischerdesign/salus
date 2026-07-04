# Federation Status Indicator

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Status dot (colored) + Label ("Synced 2m ago" / "Sync failed" / "Not synced yet") + Optional retry button

**States:** Synced recently (tertiary dot, "Synced Xm ago") · Syncing (primary dot, pulsing) · Sync failed (error dot, "Sync failed — Retry") · Never synced (slate-400 dot, "Not synced yet")

**Placement:** Below peer handle in peer-card, only visible for remote peers. Compact, 11px caption font.

**Dot:** 8px circle, rounded-full. Pulsing animation (1.8s) when syncing.

**Retry:** Small ghost button, appears only on failed state.

**Do:** Show for all remote peers · Distinguish syncing/synced/failed · Provide retry on failure

**Don't:** Show for local peers · Use ambiguous labels · Omit timestamp on last success
