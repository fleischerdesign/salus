# Data Entry Flow

## Goal
User creates a metric type, then logs measurements. Data enters the system via manual entry or automated webhook ingestion.

## Entry Points
- `/metrics` — Metric type management (CRUD)
- `/entries` — Manual entry logging (CRUD)
- `/webhook` — Automated ingestion from wearables (background)
- Dashboard → click metric value → jumps to `/entries?metric_type_id=X`

---

## Metric Type Creation

**Route:** `GET /metrics/new` → `POST /metrics`
**Components:** `modal` · `input` · `select` · `color-picker` · `btn`

| State | UI |
|-------|----|
| Click "New Metric" | Modal: Name + Unit + Data Type (number/text/json) + Color picker + Icon name + Save |
| Fill form | All fields interactive. Color picker: `44×80px` native color input. |
| Submit | `loading-button` |
| Success | Redirect to `/metrics`. New metric appears in list. |
| Validation error | `alert` (error) in modal: "Name is required". Field highlighted (error border). |

---

## Manual Entry Logging

**Route:** `GET /entries/new` → `POST /entries`
**Components:** `modal` · `select` · `input` · `btn`

### Entry Form

| Field | Component | Required | Notes |
|-------|-----------|----------|-------|
| Metric Type | `select` | Yes | Pre-filled if `?metric_type_id=X` or editing |
| Value | `input` (text) | Yes | Format guidance in hint text |
| Timestamp | `input` (datetime-local) | No | Defaults to now |
| Notes | `input` (text) | No | Free text |

| State | UI |
|-------|----|
| Open form | Modal with 4 fields. Metric dropdown pre-selected if navigated from dashboard |
| Fill + Submit | `loading-button` "Save Entry" |
| Success | Redirect to `/entries?metric_type_id=X`. List shows new entry at top. |
| Success (sharing) | Background: `sharing_svc.notify_peers_of_update()` |
| Validation error | `alert` (error): "Value is required". Field highlighted. |

### Entry List

| State | UI |
|-------|----|
| Has entries | `table` with columns: Date/Time · Value · Notes · Actions (edit/delete) |
| Filter by metric | Quick-filter chips above table (one per metric type). Active chip: primary variant. |
| Empty (no entries for metric) | `empty-state` "No entries yet" + "Log your first entry" button |
| Empty (no metrics at all) | `empty-state` "Create a metric first" + link to `/metrics` |

---

## Webhook Ingestion (Background)

**Route:** `POST /webhook`
**Auth:** Bearer token or `X-API-Token` header

| State | Behavior |
|-------|----------|
| Payload arrives | `WebhookIngestionService.ingest(payload)` in background task |
| Parse | `FlexiblePayloadParser` auto-detects format (Health Connect, Apple Health, Flat Array, etc.) |
| Map | `MetricTypeMappingService` resolves source data types → user metric types |
| Upsert | `MeasurementRepository.upsert_all()` dedupes by `external_id` + `source` |
| Notify | `sharing_svc.notify_peers_of_update()` for any metrics with active sharing |
| Response | HTTP 202 Accepted immediately (processing continues) |

**Edge Cases:**
- Unknown data type → skipped, logged. No error to sender.
- Duplicate record (by external_id + source) → silently deduped.
- User has no matching metric type → record skipped. User sees nothing.
- Malformed payload → HTTP 400.

---

## Entry Edit / Delete

**Route:** `GET /entries/{id}/edit` → `PUT /entries/{id}` · `DELETE /entries/{id}`
**Components:** `modal` · `input` · `btn` · `confirm`

| Action | State | UI |
|--------|-------|----|
| Click edit (row, pencil icon) | Open | Modal: form pre-filled with current values |
| Submit edit | Loading | Button loading |
| Edit success | Done | Redirect to `/entries`. Row updated. |
| Edit error | Error | `alert` (error) in modal |
| Click delete (row, trash icon) | Open | `confirm` dialog: "Delete this entry?" + Cancel + Delete (danger) |
| Confirm delete | Loading | Delete button loading |
| Delete success | Done | Row fades out, removed from DOM |
| Delete error | Error | `toast` (error): "Could not delete — try again" |

---

## Visual State Map (Entry List)

```
┌─────────────────────────────────────────────────────┐
│ TOP-APP-BAR                                         │
│ [salus]  Dashboard  Entries  Goals  ...      [👤]   │
├─────────────────────────────────────────────────────┤
│ [Steps] [Heart Rate] [Sleep] [Weight] [+ New]      │  ← Quick-filter chips
├─────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────┐│
│ │ Date/Time         │ Value  │ Notes   │ Actions  ││
│ ├──────────────────────────────────────────────────┤│
│ │ Jul 5, 2026 08:15 │ 8,432  │ Morning │ ✎  ✕    ││
│ │ Jul 4, 2026 19:30 │ 7,102  │ —       │ ✎  ✕    ││
│ │ Jul 3, 2026 07:00 │ 6,891  │ —       │ ✎  ✕    ││
│ └──────────────────────────────────────────────────┘│
│                                          [Log Entry]│
└─────────────────────────────────────────────────────┘
```

## HTMX Events

| Trigger | Route | Target | Swap |
|---------|-------|--------|------|
| Page load | `GET /entries` | body | Full page |
| Filter chip click | `GET /entries?metric_type_id=X` | body | Full page |
| Open new entry modal | `GET /entries/new?metric_type_id=X` | `#modal-container` | innerHTML |
| Submit entry | `POST /entries` | — | Redirect |
| Edit entry | `GET /entries/{id}/edit` | `#modal-container` | innerHTML |
| Update entry | `PUT /entries/{id}` | — | Redirect |
| Delete entry | `DELETE /entries/{id}` | entry row | delete |
| Webhook ingestion | `POST /webhook` | — | 202 Accepted (async) |

## Edge Cases

| Case | Behavior |
|------|----------|
| Webhook sends unknown data type | Skipped silently. No user-facing error. |
| User edits entry that was just deleted | 404 → redirect, entry list re-renders without it |
| Timestamp in the future | Allowed (pre-logging). Dashboard shows it when that date arrives. |
| Very long notes | Notes column truncates with "..." + tooltip on hover showing full text |
| No metric types exist yet | Entries page shows empty-state: "Create a metric first" |
| Metric deleted that has entries | Entries remain but show "Deleted Metric" label, cannot add new entries to it |
