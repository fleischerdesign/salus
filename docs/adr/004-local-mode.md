# 4. Local mode: server-optional identity and derived data

- Status: Proposed
- Date: 2026-08-13

## Context

Salus is offline-first but not server-less: the SPA gates on a JWT obtained from
a server (LocalAuth/LDAP/OIDC), and reference data (`metric_definition`,
`achievement_definition`, …) reaches the client only through sync. The data
layer is already Dexie-first for reads and outbox-based for writes, with a
`SELF_USER_ID='self'` sentinel already used in 12 frontend files for optimistic
writes.

Two concerns motivate this decision:

1. Users should be able to use Salus as a full tracker without ever deploying
   or connecting a server. The server becomes optional (sync, sharing,
   coaching), not a prerequisite for daily tracking.
2. Achievements — and, by extension, any derived state — must not be
   client-authoritative. Today `user_achievement` is `strategy="user_scoped"`
   (`entity_meta.py`) and therefore client-writable via `/api/v1/sync/push`: a
   latent integrity hole where a client can fabricate unlocks.

## Decision

Introduce an **additive Local Mode**, not a server-less rewrite. The
server-connected flow stays untouched; local mode is a parallel identity path
that can later be promoted to a server account.

1. **Identity** — a device profile (display name, no password) using the
   existing `SELF_USER_ID='self'` sentinel. A synthetic local session satisfies
   the SPA auth gate without a server token; the optional biometric/PIN lock
   (already implemented) is a screen lock, not a login.
2. **Reference data bundling** — code-defined, finite, immutable reference data
   (`metric_definition`, `metric_group`, `achievement_definition`, `mood_tag`,
   plus `exercise` system defaults) gets a single shared, versioned source
   consumed by BOTH the backend (to seed/validate) and the frontend (bundled and
   seeded into Dexie when empty). Runtime-managed `system_config` stays
   server-only.
3. **Derived-data principle** — only source data is synced; derived state is
   re-derived. `user_achievement` becomes server-computed and read-only (not
   client-writable). Locally, achievement progress is computed from Dexie for
   display only and never persisted as syncable rows.
4. **Migration** — "Connect server" pushes source data through the existing
   outbox; the server re-derives achievements and re-owns rows (`_inject_user_id`
   already overwrites `self` → the real uid). Local achievement state is not
   migrated.
5. **Server-only features hidden in local mode** — sharing/federation,
   community/leaderboard, coach insights (LLM), admin.
6. **Durability** — JSON export/import of the Dexie store in v1, plus a
   volatility warning at profile creation.

Platforms: Android + Web/PWA.

## Consequences

- `user_achievement` must leave the client-writable set (a read-only
  `user_scoped` variant, or removal from the sync write set with the dedicated
  `/api/v1/achievements` endpoint as the read model). The server evaluates on
  sync and returns authoritative unlocks.
- Reference data: the backend still seeds the DB (FK integrity on
  `measurement.metric_code`), but the frontend no longer depends on the first
  full sync to render the metric structure.
- Sync must distinguish "no server configured" from "offline" to avoid spurious
  error toasts (complements ADR-003).
- Local Mode is opt-in and additive; existing instances and the federation/E2EE
  sharing/coaching vision are unaffected.

## Alternatives considered

- **Server-less as the primary mode** — rejected: removes the server as source
  of truth and conflicts with federation, E2EE sharing, and LLM coaching.
- **Bundle reference data AND keep syncing it** — rejected: two distribution
  channels for the same static data invite version skew; the bundled copy is the
  bootstrap, sync remains the server's authoritative refresh.
