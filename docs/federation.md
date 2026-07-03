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

## What Is Missing — Comprehensive Gap Analysis (20 items)

### Security (Critical)

#### G1. Token stored as plaintext
`api_token_hash` stores the raw hex token, not a hash. The field name says `_hash`
but the implementation is plaintext. Anyone with DB access can extract all
federation bearer tokens.
**Fix:** Hash with `hashlib.sha256(token + pepper)` before storage. Verify via
hash comparison. Show raw token to user once at creation, never again.
**Files:** `services/sharing.py:88-97`, `models/sharing.py:28`.

#### G2. No timing-safe token comparison
Raw token compared via standard SQL `WHERE api_token_hash == :token`. No
`secrets.compare_digest()` or constant-time semantics used anywhere.
**Fix:** Pre-hash the token, then compare hashes (timing-safe by design since
hashing normalises input size).
**Files:** `routers/sharing.py:483`, `services/sharing.py:416`.

#### G3. Federation accept endpoint has zero authentication
`POST /api/v1/federation/accept` accepts any HTTP POST with a JSON body
containing `token` and `owner_handle`. No Bearer auth, no origin check,
no HMAC, no rate limiting. Any actor who discovers a pending relationship's
token can activate it by sending a POST to the endpoint.
**Fix:** Require `Authorization: Bearer <token>` header on `/accept` (same
auth as `/sharing`), OR require the request to originate from the domain
specified in the relationship's `grantee_handle`.
**Files:** `services/sharing.py:400-409`, `routers/sharing.py:542-567`.

#### G4. Token exposed in HTML template
The raw `api_token_hash` is rendered in a `<code>` tag in `relationship_list.html`.
Anyone with DOM access (XSS, browser extension, screen-sharing) can extract
the federation bearer token.
**Fix:** Never render full token in HTML. Show a truncated version with a
"Copy" button that fetches the full token via an authenticated API call.
**Files:** `templates/components/sharing/relationship_list.html:35`.

#### G5. No request signing or replay protection
Federation requests use only a static Bearer token. No:
- HMAC signature to prove request origin
- Nonce or timestamp to prevent replay attacks
- JWT with embedded claims (subject, audience, expiration, issued-at)
- Server identity verification (mTLS, certificate pinning)
**Fix (Phase 2):** Sign requests with HMAC-SHA256 using a derived key.
Add `X-Salus-Nonce` and `X-Salus-Timestamp` headers. Phase 3: mTLS.

### Data Flow & Integration (High)

#### G6. `resolve_and_fetch()` / `_fetch_remote()` are dead code
`SharingService.resolve_and_fetch()` correctly dispatches between local
(`_resolve_local`) and remote (`_fetch_remote`) resolution, but **zero route
handlers call it**. The feed and leaderboard query the local DB directly.
**Fix:** Refactor `sharing_feed_page()` and `LeaderboardService.get_group_rankings()`
to use `resolve_and_fetch()` as the single data-access path.
**Files:** `services/sharing.py:255-390`, `routers/sharing.py:30-130`,
`services/leaderboard.py:177-208`.

#### G7. No federation invite delivery mechanism
When Alice creates a relationship with `@bob:remote.com`, a token is generated
but Bob never learns about it. No standard protocol exists for delivering the
invitation.
**Fix:** Option A — Embed token in invite URL:
`https://alice.example.com/sharing/invite?token=abc123&from=@alice`.
Bob clicks → his server registers the incoming relationship. This integrates
with the existing QR code feature.
**Files:** `services/sharing.py:41-101`.

#### G8. Leaderboard remote members always score zero
`LeaderboardService.get_group_rankings()` has an explicit stub:
`score = 0.0  # Remote User query (federation stub / simulation)`.
No `_fetch_remote()` or `resolve_and_fetch()` call exists.
**Fix:** Call `SharingService.resolve_and_fetch()` for remote members.
Requires `SharingService` to be injected into `LeaderboardService`.
**Files:** `services/leaderboard.py:206-208`.

#### G9. Feed has zero federation support
`sharing_feed_page()` queries `SharingRelationship` where `grantee_handle == f"@{username}"`
— this matches only local users. Remote federation relationships have grantee
handles like `@user:domain`, which never match. All data queries are local-only
DB queries against `user_id`.
**Fix:** Refactor to use `resolve_and_fetch()` which transparently handles
local and remote data sources.
**Files:** `routers/sharing.py:30-130`.

#### G10. No server discovery protocol
Remote URLs are built as `https://{domain}/api/v1/federation/...` — hardcoded,
blind trust. No:
- `.well-known/salus-federation` discovery endpoint
- Capability negotiation (supported API version, metric types)
- Protocol fallback (HTTP for local dev, HTTPS for production)
**Fix:** Add `GET /.well-known/salus-federation` returning JSON with API
version, supported endpoints, and server capabilities.
**Files:** `services/sharing.py:359-360`.

### Error Handling & Resilience (High)

#### G11. Bare `except Exception` in 8 locations
Eight places catch all exceptions indiscriminately, conflating `NotFoundError`,
`PermissionError`, `ValueError`, `AttributeError`, and `OperationalError` into
the same handler. This silently swallows bugs and makes debugging impossible.
**Files:** `routers/sharing.py:160,202,244,258,283,297,548`,
`services/sharing.py:388`.

#### G12. Zero federation logging in routers
The federation route handlers (`federated_shared_data`, `federated_accept`)
have **zero** log statements. Impossible to audit who accessed what, when,
or why access was denied.
**Fix:** Log every federation request with: requester identity (token prefix),
requested resource (owner, data_type, date), outcome (granted/denied), and
latency.
**Files:** `routers/sharing.py:462-567`.

#### G13. `_fetch_remote()` has no retry logic
A single transient network error (DNS, timeout, connection refused) causes
data to be silently dropped (`return []`). No retry, no backoff, no circuit
breaker.
**Fix:** Add exponential backoff with 3 retries. Log all failure details
(URL, status code, duration). Distinguish permanent failures (404, 401)
from transient ones (timeout, 500, 503).
**Files:** `services/sharing.py:374-390`.

#### G14. `federated_accept()` has no exception handling for service layer
`process_federation_accept()` is called without a try/except wrapper.
Any service-layer exception (DB error, session issue) becomes an
unhandled 500.
**Fix:** Wrap in try/except, log the error, return `{"status": "error"}`.
**Files:** `routers/sharing.py:555`.

### Architecture Violations (Medium)

#### G15. Router bypasses service layer for feed queries
`sharing_feed_page()` opens `with sharing_svc.uow:` and runs raw SQLModel
queries directly — N+1 pattern (one query per friend per metric type).
Violates AGENTS.md rule #3 (Routers are THIN) and #2 (no raw DB access).
**Fix:** Move data fetching into `SharingService` via `resolve_and_fetch()`.
**Files:** `routers/sharing.py:39-116`.

#### G16. `_fetch_remote()` uses wrong token for multi-metric peers
`active_rels[0].api_token_hash` blindly takes the first active relationship's
token. If Alice shares Steps AND Heart Rate with Bob (two separate
relationships, possibly different tokens), the code uses the Steps token
to request Heart Rate data.
**Fix:** Query by `metric_type_id` matching the requested `data_type`. Index
the `api_token_hash` column for performance.
**Files:** `services/sharing.py:369`, `models/sharing.py:28`.

### Code Quality (Medium)

#### G17. `api_token_hash` column has no database index
Every federation request performs a full table scan on `sharing_relationship`
to find the matching token. With thousands of relationships, this becomes a
performance bottleneck.
**Fix:** Add `index=True` to the `api_token_hash` Field in the model, or
create a separate migration.
**Files:** `models/sharing.py:28`.

#### G18. Nested `with self.uow:` in dead code path
`resolve_and_fetch()` opens `with self.uow:`, then calls `_resolve_local()`
which opens another `with self.uow:`. The inner `__exit__` commits, then the
outer `__exit__` commits again (no-op but semantically incorrect). While
harmless, it indicates an architectural misunderstanding about UoW scoping.
**Fix:** Remove the outer `with self.uow:` — it's a read-only user lookup
that doesn't need a commit boundary.
**Files:** `services/sharing.py:264-273,279`.

#### G19. Date parse failure silently maps to today
Invalid date strings silently fall back to `datetime.now(timezone.utc).date()`
with no log, no warning, no user-facing indication. A typo in the date
parameter (`"2026-07-32"`) returns today's data instead of an error.
**Fix:** Log the fallback. Consider returning 400 for unparseable dates.
**Files:** `routers/sharing.py:498-499`.

### Testing (Medium)

#### G20. Zero HTTP-layer federation tests
No `httpx` mocking exists anywhere in the test suite. `_fetch_remote()` and
`_notify_federation_accept()` are never tested against realistic HTTP scenarios.
Missing test cases: remote 404, remote 500, malformed JSON, timeout, DNS
failure, multiple tokens for same peer, expired token, invalid token, missing
token, invalid JSON body on `/accept`.
**Fix:** Add `pytest-httpx` or `responses` fixtures. Test all error paths.
**Files:** `tests/test_sharing.py`.

---

## Security Threat Model

| Threat | Vector | Current Mitigation | Gap |
|---|---|---|---|
| Token exfiltration from DB | DB access (SQL injection, backup theft) | None — plaintext storage | G1 |
| Token exfiltration from DOM | XSS, browser extension, screen sharing | None — token rendered in HTML | G4 |
| Token reuse after revocation | Replay of bearer token | None — token never invalidated | G3, G5 |
| Unauthorised accept | POST to `/accept` without auth | None — endpoint has zero auth | G3 |
| Man-in-the-middle | HTTP (not HTTPS) between servers | None — HTTP allowed | G10 |
| Replay attack | Capture and replay of valid requests | None — no nonce/timestamp | G5 |
| Server impersonation | DNS spoofing, fake domain | None — no certificate pinning | G10 |

---

## Implementation Plan (Phase 2)

### Priority 1 — Critical Security
1. **Hash tokens** (G1) — `hashlib.sha256(token + pepper)` before storage
2. **Secure `/accept` endpoint** (G3) — add Bearer auth or origin check
3. **Remove token from HTML** (G4) — truncate display, fetch full token via API

### Priority 2 — Wire Federation Into Production Paths
4. **Wire `resolve_and_fetch()` into feed** (G6) — replace raw DB queries
5. **Wire federation into leaderboard** (G8) — inject `SharingService` into `LeaderboardService`
6. **Add invite URL protocol** (G7) — `GET /sharing/invite?token=...`
7. **Fix `_fetch_remote()` token selection** (G16) — query by `data_type`, index column (G17)

### Priority 3 — Error Handling & Observability
8. **Replace bare `except Exception`** (G11) — specific exception types
9. **Add federation logging** (G12) — request audit trail
10. **Add retry logic** (G13) — exponential backoff, circuit breaker
11. **Add error handling in `/accept`** (G14) — try/except around service call
12. **Log date parse fallback** (G19) — warn on invalid dates

### Priority 4 — Code Architecture
13. **Fix UoW scoping** (G18) — remove nested `with self.uow:`
14. **Refactor feed to service layer** (G15) — move queries out of router

### Priority 5 — Testing
15. **Add httpx-mocked federation tests** (G20) — full HTTP-layer test coverage

### Priority 6 — Hardening (Phase 3)
16. **Server discovery** (G10) — `.well-known/salus-federation`
17. **Request signing** (G5) — HMAC + nonce + timestamp
18. **mTLS** (G5) — certificate pinning for production
19. **Token rotation** (G5) — periodic re-issuance of federation tokens

---

## Sequence Diagram: Phase 1 Flow (Current Implementation)

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

---

## Federation Protocol Specification (Phase 3 Target)

This section defines the target state federation protocol — the design that Phase 2
and Phase 3 should converge towards. It replaces the current Bearer-token / out-of-band
invite flow with formal, standards-aligned mechanisms.

### Identity & Discovery

User identities follow the `@username:domain` format (similar to Matrix `@user:server`
or Mastodon's WebFinger-based identity resolution).

#### WebFinger (RFC 7033)

Federation identities must be resolvable via WebFinger:

```
GET https://salus.example.com/.well-known/webfinger
    ?resource=acct:alice@salus.example.com

→ 200 {
  "subject": "acct:alice@salus.example.com",
  "links": [
    {
      "rel": "http://salus/federation",
      "href": "https://salus.example.com/api/v1/federation",
      "type": "application/json"
    }
  ]
}
```

This eliminates the blind `https://{domain}/...` string construction. The server's
actual federation URL is explicitly declared.

#### Well-Known Federation Metadata

```
GET https://salus.example.com/.well-known/salus-federation

→ 200 {
  "version": "1.0",
  "api_versions": ["v1", "v2"],
  "public_key": "ed25519:Mb+4tGOWvUM...",
  "key_type": "ed25519",
  "supported_metrics": ["steps", "sleep", "heart_rate", "weight", "water", "nutrition"],
  "supported_aggregations": ["daily_summary", "raw"],
  "endpoints": {
    "sharing": "/api/v1/federation/sharing",
    "intent": "/api/v1/federation/intent",
    "intent_response": "/api/v1/federation/intent-response",
    "accept": "/api/v1/federation/accept",
    "revoke": "/api/v1/federation/revoke",
    "access_log": "/api/v1/federation/access-log"
  },
  "admin_contact": "admin@salus.example.com"
}
```

---

### Request Authentication — HTTP Message Signatures

Phase 3 replaces static Bearer tokens with cryptographic request signing.
The design follows **HTTP Message Signatures (RFC 9421)** using Ed25519 keypairs.

**Why:** Shared Bearer tokens are stateful, require synchronization, and
anyone with a leaked token has indefinite access. Ed25519 signatures provide
origin authentication, content integrity, and replay protection without
shared secrets.

#### Key Management

Each Salus server generates an Ed25519 keypair on first startup:

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

private_key = Ed25519PrivateKey.generate()
public_key_bytes = private_key.public_key().public_bytes(
    encoding=Raw, format=Raw
)
# Store private_key securely (encrypted on disk)
# Publish public_key in .well-known/salus-federation
```

#### Signed Request Example

```
Signature-Input: sig1=("@method" "@path" "@authority" "content-digest" "x-salus-nonce" "x-salus-timestamp"); keyid="alice@salus.example.com"; created=1715971200; nonce="abc123"; alg="ed25519"
Signature: sig1=:BASE64URL_NO_PAD(signature):
Content-Digest: sha-256=:BASE64(hash(body)):
X-Salus-Nonce: abc123
X-Salus-Timestamp: 1715971200
```

**Replay Protection:**
- `X-Salus-Nonce`: unique per request, server rejects duplicates within a time window
- `X-Salus-Timestamp`: server rejects requests older than 30 seconds
- `created` in signature params: embedded in signature itself, cannot be tampered

**Content Integrity:**
- `Content-Digest`: SHA-256 of the request body
- Included in the signed components → modification of body invalidates signature

#### Verification

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def verify_federation_request(request, remote_public_key):
    # 1. Parse Signature-Input header
    # 2. Reconstruct signing string from covered components
    # 3. Verify Ed25519 signature against public_key
    # 4. Verify nonce not reused (check cache)
    # 5. Verify timestamp within 30s tolerance
    # 6. Verify Content-Digest matches actual body
    pass
```

---

### Connection Intent Protocol (3-Way Handshake)

Replaces the out-of-band token delivery with a formal server-to-server protocol.

```
Alice (Server A)              Bob (Server B)
──────────────                 ──────────────

1. POST https://bob.com/api/v1/federation/intent
   Signature: ed25519(alice-private-key)
   Body: {
     "intent_id": "uuid-v4",
     "from": "@alice:alice.com",
     "to": "@bob:bob.com",
     "metrics": [
       {"type": "steps", "aggregation": "daily_summary"},
       {"type": "heart_rate", "aggregation": "raw"}
     ],
     "message": "Hi Bob, let's connect on Salus!",
     "callback_url": "https://alice.com/api/v1/federation/intent-response",
     "expires_at": "2026-07-10T10:00:00Z"
   }
   → 202 { "status": "pending", "intent_id": "uuid-v4" }

2. Bob's server processes intent:
   → Stores as pending invitation in local DB
   → Creates SharingRelationship(state=pending, token=intent_id)
   → Notifies Bob via UI: "@alice wants to share Steps, Heart Rate"

3. Bob accepts or declines in his UI
   │
   → POST https://alice.com/api/v1/federation/intent-response
     Signature: ed25519(bob-private-key)
     Body: {
       "intent_id": "uuid-v4",
       "status": "accepted",
       "grantee": "@bob:bob.com",
       "grantee_public_key": "ed25519:..."
     }

4. Alice's server processes response:
   → Validates ed25519 signature from Bob's public key
     (fetched from https://bob.com/.well-known/salus-federation)
   → Sets SharingRelationship.status = ACTIVE
   → Stores Bob's public key for future request verification
```

**Benefits over Phase 1:**
- Bob learns about the invitation immediately (no out-of-band token passing)
- Both servers have a local record of the connection
- Ed25519 key exchange during handshake enables signed data requests
- UUID-based intent IDs replace ad-hoc hex tokens
- Full audit trail on both sides

---

### Capability-Based Access Control

Instead of one token per relationship, signed Capability Tokens describe
exactly what the grantee can access — statelessly verifiable.

```json
{
  "capability": {
    "owner": "@alice:alice.com",
    "grantee": "@bob:bob.com",
    "permissions": [
      {
        "metric": "steps",
        "aggregation": "daily_summary",
        "window_days": 90
      },
      {
        "metric": "heart_rate",
        "aggregation": "raw",
        "window_days": 30
      }
    ],
    "allowed_contexts": ["feed", "leaderboard"],
    "issued_at": "2026-07-03T10:00:00Z",
    "expires_at": "2026-10-03T10:00:00Z"
  },
  "signature": "ed25519:BASE64(sign(private_key, canonical_json(capability)))"
}
```

**Verification:** The data-serving server only needs to verify the signature
against the owner's public key (fetched once via WebFinger). No DB lookup,
no session, no shared state. The capability IS the authorization.

---

### Graceful Degradation

When remote servers are unreachable, the system must degrade gracefully,
not silently return zero/empty:

| Context | Degraded Behavior |
|---|---|
| **Feed** | Show placeholder card: "Data from @bob:remote.com temporarily unavailable. Last sync: 2h ago." — not an empty feed |
| **Leaderboard** | Show score as "—" with tooltip "Server unreachable" — not `0.0` |
| **Analytics** | Show last known value with "Data as of: 3h ago" annotation |
| **UI Peer Cards** | Connection status indicator (● green / ◐ amber / ○ red) next to peer name |
| **Dashboard Widget** | Greyed-out widget with "Remote data unavailable" banner |
| **Retry** | Exponential backoff: 1s → 2s → 4s → 8s (max 3 retries), then cache for 5 minutes |

Error categories must be distinguishable:

```python
class FederationError(Exception):
    pass

class FederationPermanentError(FederationError):
    """404, 401 — do not retry."""
    pass

class FederationTransientError(FederationError):
    """Timeout, 500, 503 — retry with backoff."""
    pass
```

---

### Federation Health & Observability

#### Prometheus Metrics

```python
# Exposed at GET /metrics
federation_requests_total{endpoint="sharing", status="200"} 1423
federation_requests_total{endpoint="sharing", status="401"} 12
federation_request_duration_seconds{endpoint="sharing", quantile="0.95"} 0.32
federation_connections_active{peer="@bob:bob.com"} 1
federation_connections_pending 3
federation_data_transferred_bytes{peer="@bob:bob.com", direction="outgoing"} 1_245_000
```

#### Audit Log

Every federation data request creates an audit record:

```json
{
  "timestamp": "2026-07-03T10:00:00Z",
  "requester": "@bob:bob.com",
  "owner": "@alice:alice.com",
  "resource": {"metric": "steps", "date": "2026-07-02"},
  "context": "feed",
  "outcome": "granted",
  "duration_ms": 45
}
```

Users can access their audit log: `GET /api/v1/federation/access-log`

#### Health Dashboard (Admin UI)

```
┌──────────────────────────────────────────────┐
│ Federation Status                            │
│                                              │
│ Connected Peers: 3                           │
│ Pending Invitations: 2                       │
│                                              │
│ @bob:bob.com           ● Online             │
│   Last sync: 2 min ago                       │
│   Shared (outgoing): Steps, HR              │
│   Visible (incoming): Sleep                  │
│   Latency: 120ms    Error rate: 0.0%        │
│                                              │
│ @carol:carol.org       ◐ Degraded           │
│   Last sync: 3h ago                          │
│   Error: Connection timeout                  │
│   Latency: n/a       Error rate: 5.2%       │
└──────────────────────────────────────────────┘
```

---

### Schema Evolution & API Versioning

Federation endpoints are versioned via URL prefix:

| Version | Path | Status |
|---|---|---|
| v1 | `/api/v1/federation/*` | Current (Phase 1) |
| v2 | `/api/v2/federation/*` | Phase 2 (signed requests, formal handshake) |
| v3 | `/api/v3/federation/*` | Phase 3 (capabilities, full observability) |

Each server declares supported versions in its well-known metadata:

```json
{
  "api_versions": ["v1", "v2"],
  "deprecated_versions": [],
  "sunset_dates": {}
}
```

**Version negotiation:**
1. Client checks remote server's `.well-known/salus-federation`
2. Selects highest mutually-supported version
3. Uses corresponding URL prefix

**Backward compatibility rules:**
- Never remove a field from a response without version bump
- Never change a field's type or semantics
- Additive changes (new fields, new endpoints) don't require a version bump
- Deprecated versions must have a documented sunset date (minimum 6 months)

---

### Operational Runbook

#### Key Rotation

```
1. Generate new Ed25519 keypair
2. Publish new public_key in .well-known/salus-federation
   alongside old key (keyring = [old, new], 7-day overlap)
3. All new federation requests use new key
4. Accept incoming requests signed with either key during overlap
5. After 7 days, remove old key from well-known
6. Delete old private key from disk
```

#### Incident Response

```
1. SUSPECT: Key compromise suspected
   → Rotate keypair immediately
   → Revoke all active federation tokens
   → Notify connected peers via /api/v1/federation/revoke

2. CONFIRM: Data breach confirmed
   → Freeze federation (disable all /api/v1/federation/* endpoints)
   → Export audit log for forensic analysis
   → Notify affected users (GDPR Art. 34)

3. RECOVER: After incident resolved
   → Verify peer server integrity (re-fetch well-known)
   → Re-establish connections with new keypairs
   → Re-enable federation endpoints
```

#### Server Migration

When a user moves from `salus-a.com` to `salus-b.com`:

```
1. User exports data from old server (backup/export)
2. User imports data on new server
3. User's new identity: @user:salus-b.com
4. Old server publishes redirect in WebFinger:
   { "rel": "http://salus/migrated-to", "href": "acct:user@salus-b.com" }
5. Connected peers detect migration on next request
6. Peers update their SharingRelationship.grantee_handle
7. New Connection Intent protocol re-establishes trust
```

---

### Test Infrastructure

```
tests/federation/
├── conftest.py               # Fixtures: MockRemoteServer, KeyPairs, httpx mock
├── test_discovery.py          # WebFinger resolution, Well-Known parsing
├── test_webfinger.py          # Identity → URL resolution
├── test_handshake.py          # Intent → Accept → Data flow (e2e)
├── test_signing.py            # Ed25519 sign/verify, replay protection
├── test_capability.py         # Capability issuance, validation, expiration
├── test_errors.py             # 4xx/5xx responses, network failures
├── test_retry.py              # Exponential backoff, circuit breaker
├── test_degradation.py        # Graceful degradation in feed/leaderboard
├── test_leaderboard_remote.py # Remote member scoring
├── test_feed_remote.py        # Remote activity feed
├── test_audit.py              # Access log recording and retrieval
├── test_migration.py          # Schema evolution, version negotiation
├── test_rotation.py           # Key rotation, overlapping trust window
├── test_e2e.py                # docker-compose: 2 real Salus instances
└── test_security.py           # Penetration test scenarios
```

**Integration test setup (docker-compose):**

```yaml
# tests/federation/docker-compose.yml
services:
  alice:
    build: ../../.
    environment:
      - SALUS_DATABASE_URL=postgresql://alice:pass@db-alice/alice
      - SALUS_JWT_SECRET_KEY=test-key-alice
      - SALUS_HOST=alice.salus.test
    ports: ["8001:8000"]
  bob:
    build: ../../.
    environment:
      - SALUS_DATABASE_URL=postgresql://bob:pass@db-bob/bob
      - SALUS_JWT_SECRET_KEY=test-key-bob
      - SALUS_HOST=bob.salus.test
    ports: ["8002:8000"]
```

---

### Privacy & Compliance by Design

| GDPR Principle | Implementation |
|---|---|
| **Data Minimisation** | `daily_summary` is the default aggregation; raw data requires explicit opt-in per metric |
| **Purpose Limitation** | Capability tokens encode allowed contexts (`feed`, `leaderboard`); server verifies context before serving data |
| **Right of Access** | `GET /api/v1/federation/access-log` — every user can see who accessed their data, when, and for what purpose |
| **Right to Erasure** | `POST /api/v1/federation/forget-me?user=@bob` — owner can remove all data access for a specific grantee; grantee's server removes all cached copies |
| **Consent** | Explicit Accept flow (already implemented with ConnectionStatus enum); consent history is logged and immutable |
| **Data Portability** | Federation is native data portability; users can migrate between instances without data loss (see Server Migration) |
| **Privacy by Default** | All sharing starts as `pending`; no data accessible until grantee explicitly accepts |
| **Transparency** | Well-known metadata, public audit log format, open protocol specification |

---

## Target State Summary

| Dimension | Phase 1 (Current) | Phase 2 (Now) | Phase 3 (Target) |
|---|---|---|---|
| **Identity** | `@user:domain` string parse | WebFinger resolution | WebFinger + migration redirects |
| **Auth** | Plaintext Bearer token | Hashed token | Ed25519 HTTP Signatures (RFC 9421) |
| **Handshake** | Out-of-band token | Invite URL | Intent Protocol (3-way) |
| **Access Control** | DB lookup per request | Indexed lookup | Signed Capabilities (stateless) |
| **Observability** | Zero logs | Structured logs + audit | Prometheus + Audit Dashboard |
| **Error Handling** | `except Exception: pass` | Typed exceptions + logging | Graceful degradation + circuit breaker |
| **Testing** | 3 unit tests (no HTTP) | httpx-mocked integration | Docker-based e2e test suite |
| **Compliance** | None | Audit log | Full GDPR tooling |
| **Operations** | None | Runbook documented | Key rotation, incident response automated |
