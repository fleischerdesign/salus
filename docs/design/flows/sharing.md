# Sharing & Federation Flow

## Goal
User connects with peers, shares selected health metrics, sees peer activity in feed, participates in leaderboard challenges.

## Entry Points
- `/sharing/feed` — Activity feed of connected peers (default sharing page)
- `/sharing/connections` — Manage peer connections
- `/sharing/leaderboard` — Challenge groups
- `/sharing/access-log` — GDPR audit trail

---

## Connection Management

### View Connections

**Route:** `GET /sharing/connections`
**Components:** `peer-card` · `avatar` · `chip` · `badge` · `federation-status` · `btn`

| State | UI |
|-------|----|
| Has connections | Grid of `peer-card` components. Each: avatar + handle + relationship badge + metric list. |
| Has pending invitations | `pending-invitation` section at top of page |
| No connections | `empty-state`: "No connections yet" + "Invite a Peer" CTA |
| Remote peer | `federation-status` component shows sync state (synced/syncing/failed/never) |

### Invite a Peer

**Route:** `GET /sharing/connections/invite-modal` → `POST /sharing`
**Components:** `invite-modal` · `input` · `multiselect` · `btn` · `copy-to-clipboard` · `qr-code`

| State | UI |
|-------|----|
| Click "Invite" | `modal` opens: QR code (200×200px) + copyable URL + "Your handle: @username" |
| User copies link | `copy-to-clipboard`: → "Copied!" (2s) |
| Close modal | User shares link out-of-band (messenger, email) |
| Grantee visits link | `GET /sharing/connections?connect_to=@username` → pre-fills grantee handle |

### Send Sharing Request

| State | UI |
|-------|----|
| Form open | Grantee handle input + metric checkboxes (with aggregation level per metric) + optional expiration days + "Share" button |
| Select metrics | `multiselect`: metric checkboxes with per-metric aggregation (Summary/Raw) |
| Submit | `loading-button` |
| Success (local peer) | Redirect to `/sharing/connections`. New pending relationship appears in grantee's list. |
| Success (remote peer) | Page re-renders with `new_tokens` displayed. Raw tokens shown with `copy-to-clipboard`. |
| Error | `alert` (error): "User not found" or "Already sharing this metric" |

### Respond to Invitation

**Route:** `POST /sharing/{id}/accept` · `POST /sharing/{id}/decline`
**Components:** `pending-invitation` · `btn` · `toast`

| State | UI |
|-------|----|
| Pending invitation visible | Card section at top of connections page. Each: peer name + metric + Accept/Decline buttons |
| Accept | Button → `loading-button` → page refreshes (HX-Refresh). `toast` (success): "Now sharing with @peer" |
| Decline | Button → `loading-button` → invitation row fades out |
| Error on accept | `toast` (error): "Could not accept — try again" |

### Revoke / Delete

**Route:** `DELETE /sharing/{id}`
**Components:** `confirm` · `btn` · `toast`

| State | UI |
|-------|----|
| Click revoke (× on metric row or "Revoke All") | `confirm` dialog: "Stop sharing {metric} with @peer?" + Cancel + Revoke |
| Confirm | `loading-button` |
| Success | Page refreshes (HX-Refresh: true). `toast` (success): "Sharing revoked" |
| Error | `toast` (error): "Could not revoke — try again" |

---

## Activity Feed

**Route:** `GET /sharing/feed`
**Components:** `card` · `list-item` · `stat` · `chip` · `federation-status`

| State | UI |
|-------|----|
| Has activity | Chronological feed of peer updates: "Alice completed Upper/Lower workout (3,200kg)" · "Bob logged 8,432 steps" |
| Includes remote peers | `federation-status` on each remote peer's activity: "Synced 2m ago" |
| No activity | `empty-state`: "No recent activity from your peers" |
| Only local activity | Feed shows only your own updates + "Invite peers to see their activity" CTA |

---

## Leaderboard

**Route:** `GET /sharing/leaderboard` · `POST /sharing/leaderboard/create` · `POST /sharing/leaderboard/join`
**Components:** `card` · `table` · `stat` · `badge` · `input` · `btn` · `modal`

| State | UI |
|-------|----|
| Has groups | List of `card` per group: name + metric + time frame + your rank + your score |
| Create group | Modal: name + metric (steps/workouts/sleep/water) + time frame + "Create" button |
| Join by code | Input: invite code + "Join" button |
| Group detail | `table` with rankings: avatar + handle + score. Your row highlighted. |
| No groups | `empty-state`: "No challenges yet" + "Create" + "Join" buttons |

**Leaderboard Detail Page** (`/sharing/leaderboard/{group_id}`):

| State | UI |
|-------|----|
| Active challenge | Rankings table: Rank column + Avatar + Handle + Score |
| Challenge ended | "Challenge ended" badge + final rankings (locked) |
| You're #1 | Your row with gold badge + "You're winning!" accent |

---

## Access Log (GDPR)

**Route:** `GET /sharing/access-log`
**Components:** `table` · `timeline` · `chip` · `empty-state`

| State | UI |
|-------|----|
| Has access records | `table`: Requester · Data Type · Date Accessed · Timestamp |
| No records | `empty-state`: "Nobody has accessed your data yet" |
| Recent access (<24h) | Row with subtle highlight + "New" chip |

---

## Federation (Background)

**Routes:** `GET /api/v1/federation/sharing` · `GET /.well-known/webfinger`
**Components:** `federation-status` · `spinner`

| State | User-Visible UI |
|-------|----------------|
| Remote peer added | `peer-card` shows `federation-status`: "Not synced yet" |
| First sync | Status dot: `--color-primary-500` pulsing. Label: "Syncing..." |
| Sync success | Status dot: `--color-tertiary-500`. Label: "Synced 2m ago" (updates on refresh) |
| Sync failed | Status dot: `--color-error-500`. Label: "Sync failed" + Retry button |
| Data arrives | Feed updates with remote peer activity |

---

## HTMX Events

| Trigger | Route | Target | Method |
|---------|-------|--------|--------|
| Feed load | `GET /sharing/feed` | body | Full page |
| Connections load | `GET /sharing/connections` | body | Full page |
| Invite modal | `GET /sharing/connections/invite-modal` | `#modal-container` | innerHTML |
| Send invite | `POST /sharing` | — | Redirect or re-render |
| Accept | `POST /sharing/{id}/accept` | — | Redirect + HX-Refresh |
| Decline | `POST /sharing/{id}/decline` | — | Redirect + HX-Refresh |
| Revoke | `DELETE /sharing/{id}` | — | 200 + HX-Refresh |
| Leaderboard list | `GET /sharing/leaderboard` | body | Full page |
| Create group | `POST /sharing/leaderboard/create` | — | Redirect |
| Join group | `POST /sharing/leaderboard/join` | — | Redirect |
| Group detail | `GET /sharing/leaderboard/{group_id}` | body | Full page |

## Edge Cases

| Case | Behavior |
|------|----------|
| Invite self | Prevented: "You cannot share with yourself" |
| Invite non-existent user | `alert` (error): "User @unknown not found" |
| Invite already connected peer | `alert` (error): "Already sharing with @peer" |
| Accept expired invitation | `alert` (error): "This invitation has expired" |
| Remote peer offline during sync | Automatic retry (3× exponential backoff). Status: "Sync failed — will retry" |
| Leaderboard with only you | Rankings: 1 entry (you). "Invite more peers to compete" CTA. |
| Federated peer changes handle | WebFinger resolves new handle. Old relationships may break (manual fix needed). |
| Access log empty (GDPR) | Reassuring: good state. "Your data has not been accessed by anyone." |
