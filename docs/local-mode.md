# Local Mode

Server-optional identity for Salus. Users can track without any instance;
connecting a server later promotes the local data.

See `docs/adr/004-local-mode.md` for the decision record.

## Goals

- Run Salus as a full tracker (entries, goals, habits, meals, medications,
  workouts, mood, journal, analytics, achievements) without a server.
- Keep the server-connected flow unchanged.
- Allow a local profile to be promoted to a server account without data loss.
- Prevent client-fabricated achievements (derived-data principle).

## Non-goals

- A server-less rewrite that removes federation/E2EE-sharing/coaching.
- Local accounts with passwords (device profile only; biometric/PIN is a lock).
- Seeding `system_config` (instance-managed, incl. secrets).

## Requirements

### R1 — Local identity
- The login screen offers a "Lokal starten" path that creates a device profile
  (display name only) and enters the app without a server.
- The session is persisted locally; subsequent launches enter local mode
  directly, bypassing the login gate.
- `SELF_USER_ID='self'` remains the local identity.

### R2 — Reference data bundling
- Code-defined reference data (`metric_definition`, `metric_group`,
  `achievement_definition`, `mood_tag`, `exercise` system defaults) has one
  shared, versioned source consumed by backend (seed) and frontend (bundle).
- On first launch with an empty store, the frontend seeds Dexie from the bundle.
- `system_config` is excluded.

### R3 — Sync: no-server state
- With no server configured, `syncAll()` is a no-op and `mutate()` persists
  locally without a network round-trip or an error toast.
- The outbox is retained so a later "Connect server" flushes it.

### R4 — Achievements
- Achievement progress is computed locally from Dexie for display.
- `user_achievement` is not client-writable (server re-derives on sync).

### R5 — Feature degradation
- In local mode, sharing/federation, community/leaderboard, coach insights, and
  admin are hidden.

### R6 — Migration
- "Connect server" (via the app settings) pushes source data through the outbox;
  the server re-owns rows (`self` → uid) and re-derives achievements.

### R7 — Durability
- JSON export/import of the Dexie store is available in v1.
- Profile creation warns that local data is device-only and can be lost.

### R8 — Platform
- Android + Web/PWA. Native-only capabilities (background sync, Health Connect,
  biometric) remain native-only; web uses service-worker precache and
  `navigator.onLine`/network provider.

## Acceptance criteria

### Local identity
- **Given** no token and no local profile, **when** the app opens, **then** the
  login screen shows both server login and "Lokal starten".
- **Given** a local profile exists, **when** the app opens (online or offline),
  **then** the dashboard renders from Dexie without contacting a server.
- **Given** a local profile, **when** the user opens a server-only route,
  **then** it is not reachable.

### Achievements
- **Given** local data satisfying an achievement condition, **when** the
  achievements page renders, **then** the achievement shows as unlocked
  (computed from Dexie).
- **Given** a client push containing `user_achievement`, **when** it reaches the
  sync pipeline, **then** it is rejected (server-authoritative).

### Migration
- **Given** a local profile with data, **when** the user connects a server and
  logs in, **then** the outbox flushes, rows are re-owned to the real uid, and
  achievements are re-derived server-side to the same unlocks.

### Durability
- **Given** a local profile, **when** the user exports and imports the JSON on a
  fresh device, **then** the store is restored.

## Workstreams

1. Reference data bundling (shared source → backend seed + frontend bundle/seed).
2. Local identity (device profile, synthetic session, login-gate bypass).
3. Sync no-server state (no-op sync, no error toasts, retain outbox).
4. Achievements: local evaluator + `user_achievement` read-only server-side.
5. Feature degradation (hide server-only routes).
6. Export/import (Dexie JSON) + volatility warning.
