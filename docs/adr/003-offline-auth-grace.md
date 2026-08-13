# 3. Offline auth grace: no hard logout on session expiry

- Status: Proposed
- Date: 2026-08-13

## Context

The JWT has a fixed lifetime (default 24h) and there is no refresh-token
endpoint. The previous behaviour on a `401` from any sync pull/push was an
immediate forced logout: `auth.clear()` plus a redirect to `/auth/login`. For a
local-first PWA this is hostile — a user whose token expired while the device
was offline is locked out of all locally cached health data even though the
data lives in IndexedDB and remains fully usable.

Two facts shape the design:

1. A `401` can only arrive over a working network path, so a literal
   "offline 401" does not exist. The real scenario is: token expires during an
   offline period → the device reconnects → the next sync push/pull returns
   `401` → the user is thrown out.
2. The outbox survives logout (it lives in Dexie), but nothing flushed it after
   re-login; the previous `runSync()` triggered only a pull, never a push.

## Decision

Treat session expiry as a **non-blocking, recoverable state** instead of a hard
lockout.

1. On `401`, do **not** clear the local session or redirect. Stop live sync
   (SSE) and surface a dismissible warning banner
   ("Sitzung abgelaufen – melde dich erneut an, um zu synchronisieren") with an
   explicit "Neu anmelden" action. Local reads and offline writes keep working.
2. Re-login re-runs the sync bootstrap: the `synced` guard now resets on
   logout, and `runSync()` performs a delta pull **and** flushes the stale
   outbox (`syncEngine.flush()`), so queued offline writes are pushed once a
   fresh token is present.
3. The banner is reactive to the combined `sessionExpired` state (pull-level
   `_sessionExpired` or push-level `syncEngine.sessionExpired`), so a mid-session
   background-push `401` is also surfaced without a page reload.

## Consequences

- **Security:** the user keeps access to *local* data only. Any server-required
  action still `401`s until they re-authenticate via the banner's action, so no
  privileged server operation is exposed behind an expired token.
- **Refresh token** remains an open follow-up (a `/auth/refresh` endpoint with a
  longer-lived refresh credential) to make re-authentication silent; this ADR
  only removes the hard lockout.
- **`navigator.onLine` is not used** to distinguish online/offline here, because
  a `401` already proves a network path existed at the moment of the response.

## Alternatives considered

- **Hard logout on online-401 only, grace on offline-401:** rejected — a `401`
  cannot arrive offline, so the branch would be dead code.
- **Silent refresh token:** deferred; requires a backend endpoint and new token
  lifecycle, out of scope for this change.
