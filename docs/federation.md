# Federation Architecture

Status: **Phase 1 complete — Foundation laid, end-to-end flows not yet wired.**

---

## Overview

Salus supports peer-to-peer health data sharing across independent server instances.
This document describes the federation subsystem: its data model, protocol, current
implementation state, and the remaining work for full cross-server interoperability.

```
┌──────────────┐         ┌──────────────┐
│  Server A    │  HTTPS  │  Server B    │
│  (alice)     │◄───────►│  (bob)       │
│              │         │              │
│  /api/v1/    │         │  /api/v1/    │
│  federation/ │         │  federation/ │
│    sharing   │         │    sharing   │
│    accept    │         │    accept    │
└──────────────┘         └──────────────┘
```

---

## Data Model

### SharingRelationship

```
┌──────────────────────────────────────────────────┐
│ SharingRelationship                              │
│                                                  │
│ owner_id      FK → user.id  (data owner)         │
│ grantee_handle str          (recipient identity) │
│ metric_type_id FK → metric_type.id               │
│ aggregation_level str       ("daily_summary"/"raw")│
│ expiration_date datetime | None                  │
│ status        str           (ConnectionStatus enum)│
│ api_token_hash str | None   (40-char hex token)  │
│ created_at    datetime                            │
│ updated_at    datetime                            │
└──────────────────────────────────────────────────┘
```

**Handle format:**
- `@username` — local user
- `@username:domain` — remote/federated user

**ConnectionStatus enum:**
- `pending` — invitation sent, awaiting acceptance
- `active` — both parties confirmed
- `declined` — grantee rejected
- `revoked` — owner cancelled

---

## Handle Resolution

| Pattern | Example | Resolution |
|---|---|---|
| No `:` | `@alice` | Query local `User` table by username |
| Contains `:` | `@bob:remote.example.com` | No local user lookup; treat as remote federated peer |

The `@` prefix is always normalised by `SharingService._normalise_handle()`.

---

## API Endpoints

### Provider Side (Owner's Server)

#### `GET /api/v1/federation/sharing`

Serves shared data to a remote grantee.

| Parameter | Source | Description |
|---|---|---|
| `owner_username` | Query | Username of the data owner |
| `data_type` | Query | Metric source data type (e.g. `"steps"`) |
| `date` | Query | Date string `YYYY-MM-DD` |
| `Authorization: Bearer <token>` | Header | Bearer token matching `api_token_hash` |

**Response (200):**
```json
{
  "status": "ok",
  "data": [
    {
      "data_type": "steps",
      "value_numeric": 9500.0,
      "start_time": "2026-07-02",
      "source": "summary",
      "external_id": "summary-owner-steps-2026-07-02"
    }
  ]
}
```

**Errors:** 401 (invalid/missing token), 404 (user not found).

#### `POST /api/v1/federation/accept`

Called by the grantee's server to notify the owner that an invitation was accepted.

**Request body:**
```json
{
  "token": "abc123...",
  "owner_handle": "@alice"
}
```

**Response (200):**
```json
{"status": "ok"}
```

**Behaviour:** Looks up `SharingRelationship` by `api_token_hash` and `status=pending`, sets `status=active`.

### Consumer Side (Grantee's Server)

There is no dedicated consumer endpoint. The grantee queries the owner's server
via `SharingService._fetch_remote()`:

```
grantee-server → GET https://remote.example.com/api/v1/federation/sharing
                  ?owner_username=bob
                  &data_type=steps
                  &date=2026-07-02
                  Authorization: Bearer <token>
```

---

## Authentication Flow

```
1. Alice (owner) creates relationship with @bob:remote.com
   → SharingRelationship created with status=pending
   → api_token_hash = secrets.token_hex(20)  (40-char hex)

2. Bob (grantee) somehow receives the token + Alice's server URL
   (out-of-band: QR code, email, copy-paste)

3. Bob's server stores the token and calls:
   POST https://alice.example.com/api/v1/federation/accept
   Body: {"token": "abc123...", "owner_handle": "@alice"}

4. Alice's server sets status=active

5. Bob can now call GET /api/v1/federation/sharing with the token
   to read Alice's shared data
```

---

## What Works (Phase 1)

| Component | Implementation | File |
|---|---|---|
| Token generation | `secrets.token_hex(20)` stored in `api_token_hash` | `services/sharing.py:88` |
| Remote handle detection | `":" in handle` check | `services/sharing.py:34` |
| `/api/v1/federation/sharing` | Bearer-token auth, aggregation, expiration | `routers/sharing.py:479-535` |
| `/api/v1/federation/accept` | Token lookup, status update | `routers/sharing.py:554-567` |
| `_fetch_remote()` | httpx GET to remote `/api/v1/federation/sharing` | `services/sharing.py:351-390` |
| `_notify_federation_accept()` | httpx POST to remote `/api/v1/federation/accept` | `services/sharing.py:396-411` |
| `process_federation_accept()` | Processes incoming federation accept notification | `services/sharing.py:413-424` |

---

## What Is Missing (Phase 2)

### 1. `resolve_and_fetch()` is Dead Code

`SharingService.resolve_and_fetch()` correctly dispatches between local
(`_resolve_local`) and remote (`_fetch_remote`) resolution, but **no route
handler calls it**. The feed and leaderboard query the local database directly.

**Fix:** Refactor `sharing_feed_page()` and `LeaderboardService.get_group_rankings()`
to use `resolve_and_fetch()` as the single data-access path.

### 2. No Federation Invite Delivery

When Alice creates a relationship with `@bob:remote.com`:

- A token is generated ✓
- The token is stored in `api_token_hash` ✓
- Bob never learns about the invitation ✗

A standard delivery mechanism is needed:

**Option A — Invite URL:** Embed the token in an invite URL:
```
https://alice.example.com/sharing/invite?token=abc123&from=@alice
```
Bob clicks → Bob's server registers the incoming relationship.

**Option B — Federation Webhook:** Alice's server calls a well-known endpoint
on Bob's server to deliver the invitation.

**Recommendation:** Option A for MVP (simple, works with existing QR code).

### 3. No Server Discovery

Remote URLs are constructed as `https://{domain}/api/v1/federation/...`.
This assumes:
- The domain in the handle is a valid HTTPS host
- The federation endpoints are at the default paths
- HTTPS is available and the certificate is trusted

**Missing:**
- `.well-known/salus-federation` discovery endpoint
- Capability negotiation (supported metric types, API version)
- Configurable protocol (HTTP for local dev, HTTPS for production)

### 4. Token Stored as Plaintext

`api_token_hash` stores the raw hex token, not a hash. The comment in the
original code says "In production, hash it."

**Fix:** Hash with `bcrypt` or `hashlib.sha256` before storage. Verify with
the hash, not a plaintext comparison.

### 5. Leaderboard with Remote Peers

`LeaderboardService.get_group_rankings()` has a federation stub at line 207-208:
```python
# Remote members (handle has ":"): returns score = 0.0
```
No `_fetch_remote()` call is made. Remote leaderboard members always score
zero regardless of their actual data.

**Fix:** For remote members, call `resolve_and_fetch()` or `_fetch_remote()`
to retrieve their data, same as local members.

### 6. No Signature / Trust Chain

The current authentication relies solely on a Bearer token. There is no:
- JWT-based token with expiration and claims
- mTLS for server identity verification
- Domain ownership verification (DNS TXT record, ACME challenge)
- Token rotation mechanism

### 7. No Connection Status Sync

When a relationship is revoked on the owner's server, the grantee's server
is not notified. The grantee continues to believe they have access.

**Fix:** Add a `/api/v1/federation/revoke` endpoint and call it from
`deactivate_relationship()` for remote grantees.

---

## Implementation Plan (Phase 2)

### Step 1: Wire `resolve_and_fetch()` into Feed

Replace the direct DB queries in `sharing_feed_page()` with calls to
`SharingService.resolve_and_fetch()`. This automatically enables remote
data fetching in the community feed.

### Step 2: Invite URL Protocol

- Add `GET /sharing/invite?token=X&from=@handle` route
- When Bob visits this URL (on Alice's server), show a confirmation page
- Bob confirms → Alice's server sets `status=active`
- Alternatively: Bob clicks invite link on his own server, which calls
  `POST /api/v1/federation/accept` on Alice's server

### Step 3: Token Hashing

- Hash `api_token_hash` with `hashlib.sha256` before storage
- Compare hashes during authentication (no plaintext comparison)
- The raw token is shown to the user once at creation time

### Step 4: Leaderboard Remote Scoring

- In `LeaderboardService.get_group_rankings()`, for members with `:` in
  their handle, call `SharingService.resolve_and_fetch()` or
  `_fetch_remote()` to compute their actual score

### Step 5: Security Hardening

- JWT-based federation tokens with embedded claims (user, metric, expiration)
- Server identity verification via mTLS or shared secret
- Well-known discovery endpoint: `GET /.well-known/salus-federation`

### Step 6: Connection Status Sync

- `POST /api/v1/federation/revoke` endpoint
- Called by `deactivate_relationship()` for remote grantees
- Grantee's server updates local status

---

## Sequence Diagram: Full Federation Flow (Target State)

```
Alice (Server A)                    Bob (Server B)
─────────────────                   ─────────────────

1. Alice invites @bob:server-b.com
   → status=pending
   → api_token=T

2. Alice gets invite URL:
   https://server-a.com/s/invite?token=T&from=@alice

3. Alice sends URL to Bob (QR, email, etc.)
                                    ─────────────────

                                    4. Bob opens invite URL
                                    → Bob validates token
                                    → Bob sees "@alice wants to share Steps, HR"

                                    5. Bob accepts
                                    → POST /api/v1/federation/accept
                                      {token: T, owner_handle: "@alice"}
                                       │
6. Server A receives accept ─────────┘
   → status=active

                                    7. Bob's feed queries Server A:
                                    → GET /api/v1/federation/sharing
                                      ?owner_username=bob
                                      &data_type=steps
                                      &date=2026-07-02
                                      Authorization: Bearer T
                                       │
8. Server A returns data ────────────┘
   → Aggregation applied
   → Permission verified (status=active, not expired)
```
