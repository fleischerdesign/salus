# Error States & Global Handling

## Goal
Define how every error, edge case, and empty state is handled across the entire application. Consistent UX regardless of which page or component triggers the error.

---

## HTTP Error Pages

### 404 — Not Found

**Trigger:** Invalid URL, deleted resource, unknown route.
**Detection:** `is_api_request()` check in exception handler.

| Client Type | Response | UI |
|------------|----------|----|
| Browser (HTML request) | Redirect (303) to `/` | Dashboard loads |
| HTMX request | Redirect (303, header `HX-Redirect`) to `/` | Dashboard loads |
| API request (`/api/*`) | `JSONResponse(404)` | `{"error": "Not Found"}` |

**Why redirect not error page:** Better UX than a dead-end 404 page. User lands on dashboard and can navigate from there.

### 500 — Internal Server Error

**Trigger:** Unhandled exception anywhere in the app.

| Client Type | Response | UI |
|------------|----------|----|
| Browser (HTML request) | `HTMLResponse(500)` with generic error page | `<h1>500 — Internal Server Error</h1>` + "Something went wrong." |
| HTMX request | Same HTML, swapped into target | Error message appears in the HTMX target area |
| API request | `JSONResponse(500)` | `{"error": "Internal Server Error"}` |

---

## Auth Errors

### 401 — Unauthorized (Not logged in)

**Trigger:** `AuthenticationError` raised when accessing protected route without valid session.
**Components:** `toast` · Login page

| State | Behavior |
|-------|----------|
| Full page request | Redirect (303) to `/auth/login`. After login, redirect back to original URL. |
| HTMX request | `HX-Redirect` header to `/auth/login`. Login page loads. User logs in, returns. |
| API request | `JSONResponse(401)` with `{"error": "Authentication required"}` |

### 403 — Forbidden (Insufficient permissions)

**Trigger:** `ForbiddenError` when user lacks required role (e.g., non-admin visits `/admin`).

| State | Behavior |
|-------|----------|
| Full page request | Redirect (303) to `/`. `toast` (error): "Access denied — insufficient permissions." |
| HTMX request | `HX-Redirect` header to `/`. Toast queued via `HX-Trigger`. |
| API request | `JSONResponse(403)` with `{"error": "Forbidden"}` |

---

## Application-Level Errors

### Form Validation Errors

**Trigger:** User submits invalid form data.
**Components:** `alert` · `input` (error state)

| Error Type | UI |
|-----------|----|
| Required field empty | Field border: `--color-error-400`. Label: `--color-error-600`. Error text below: "This field is required." |
| Invalid format | Same as above. Hint: "Enter a valid number" / "Must be a valid date." |
| Multiple errors | `alert` (error) at top of form listing all issues + each field individually highlighted |

### Conflict Errors (409)

**Trigger:** `ConflictError` — duplicate resource, constraint violation.

| Client Type | Response |
|------------|----------|
| Browser | `HTMLResponse(409)` with error message |
| API | `JSONResponse(409)` with `{"error": "message"}` |

Examples: Creating a metric type with duplicate name. Sharing a metric that's already shared.

### Resource Not Found (Application)

**Trigger:** `NotFoundError` — entity not in database.
**Components:** `empty-state` · `alert`

| Context | UI |
|---------|----|
| Edit page (deleted resource) | `alert` (error): "This {resource} no longer exists." + link to list page |
| API request | `JSONResponse(404)` with `{"error": "Not found"}` |

---

## Network & Connectivity

### Offline State

**Trigger:** `navigator.onLine === false` or `offline` event.
**Components:** `offline-indicator`

| State | UI |
|-------|----|
| Go offline | `offline-indicator` appears: fixed top, below top-app-bar, `--color-warning-100` bg. "You are offline. Changes will sync when connection is restored." |
| Reconnecting | Same banner. Icon → `sync` spinning. Text: "Reconnecting..." |
| Back online | Banner: `--color-tertiary-50` bg, checkmark. "Back online" → auto-hides after 2s. |

**Important:** The UI should NOT be blocked when offline. HTMX calls will fail but the cached page remains usable.

### Network Request Failures

**Trigger:** `fetch` / `hx-get` / `hx-post` fails (network error, not HTTP error).
**Components:** `toast`

| Context | UI |
|---------|----|
| HTMX form submission fails | `toast` (error): "Could not save — check your connection." Form stays filled. |
| HTMX content load fails | Target area shows `empty-state` with error icon + "Could not load" + Retry button |
| Multiple failures in short time | Only show one toast. Deduplicate by context. |

### Server Unreachable (non-HTTP error)

**Components:** `empty-state`

| Context | UI |
|---------|----|
| HTMX load fails | Target shows `empty-state`: "Server unreachable" + "Retry" button. Auto-retries after 10s. |
| Page load fails | Browser error page (standard). Nothing we can do. |

---

## Session & Timeout

### Session Timeout Warning

**Trigger:** JWT approaching expiry (2 minutes before).
**Components:** `timeout` · `modal` · `btn`

| State | UI |
|-------|----|
| 120s before expiry | `modal`: "Session Expiring" + countdown timer (MM:SS) + "Extend Session" + "Log Out" |
| 30s before expiry | Timer turns red (`--color-error-500`), pulses. `aria-live="assertive"`. |
| Extend clicked | `POST` to refresh JWT. Modal closes. `toast` (success): "Session extended". |
| Timer reaches 0 | Redirect to `/auth/login?reason=timeout`. Login page shows: "Your session expired due to inactivity." |
| Escape key | Ignored (must make explicit choice) |

---

## Empty States

Global rules for all empty-data scenarios.
**Components:** `empty-state`

### Empty State Variants by Context

| Context | Message Pattern | CTA |
|---------|----------------|-----|
| List (no items) | "No {items} yet" | "Create {item}" primary button |
| Dashboard (no widgets) | "Your dashboard is empty" | "Add Widget" primary button |
| Search (no results) | "No results for '{query}'" | "Clear search" link |
| Feed (no activity) | "No recent activity" | "Connect with peers" CTA |
| History (no records) | "No {records} yet" | Link to create/start |
| Filtered list (no matches) | "No {items} match your filter" | "Clear filters" button |

### Empty State Rules
- Always include an action if the user can resolve the empty state
- Never leave user stranded with "No data" and no next step
- Icon is always muted (opacity 0.4, `--color-slate-400`)
- Don't confuse empty state (valid, no data) with error state (failed to load)

---

## Loading States

Global rules for all loading scenarios.
**Components:** `skeleton` · `spinner`

### Loading Patterns

| Load Type | UI Pattern | Min Duration |
|-----------|-----------|-------------|
| Full page load | Shell renders immediately. Content areas show `skeleton` until data arrives. | 300ms |
| HTMX swap (small) | `spinner` (16px) inline replaces content temporarily | 150ms |
| HTMX swap (card) | `skeleton` card (matching dimensions) | 200ms |
| Button action | `loading-button` (spinner replaces label, button disabled) | — |
| Initial app load | Logo + spinner (40px, centered) until HTML arrives | — |

### Skeleton Shimmer Duration
1.8s pulse animation (opacity 0.4 → 0.75 → 0.4).

### Spinner Duration
0.8s per revolution, linear infinite.

---

## Success Feedback

Global rules for confirming successful actions.
**Components:** `toast` · `loading-button`

### Success Patterns

| Action | Feedback | Duration |
|--------|----------|----------|
| CRUD create/update | `toast` (success): "{Item} saved" | 5s auto-dismiss |
| CRUD delete | `toast` (success): "{Item} deleted" | 5s auto-dismiss |
| Export | Browser download starts. `toast`: "Export complete" | 5s |
| Token created (one-time) | Inline success: token displayed. Warning: "Copy now — you won't see this again." | Persistent |
| Session extended | `toast` (success): "Session extended" | 3s |
| Theme/locale changed | Immediate visual change. No toast needed. | — |

---

## Visual Hierarchy of Errors

From most intrusive to least:

| Level | Component | Use For |
|-------|-----------|---------|
| 1 (Blocking) | `modal` (timeout, confirm delete) | Must respond before continuing |
| 2 (Page-level) | `alert` (banner, top of page) | Form-wide errors, critical updates |
| 3 (Field-level) | `input` error state + error text | Single field validation |
| 4 (Transient) | `toast` (auto-dismiss) | Save success, sync complete |
| 5 (Ambient) | `offline-indicator`, `federation-status` | Background state, no action needed |

---

## HTMX Error Handling Pattern

```html
<!-- FORM -->
<form hx-post="/submit" hx-target="#result">
  <!-- fields -->
</form>

<!-- On success: server returns HTML/redirect -->
<!-- On HTTP error: HTMX fires htmx:responseError event -->
<!-- Client-side handler: -->
<script>
  document.body.addEventListener('htmx:responseError', function(evt) {
    var toast = document.createElement('div');
    toast.className = 'toast toast--error';
    toast.textContent = 'Could not save — try again.';
    document.getElementById('toast-container').appendChild(toast);
  });
</script>
```

This ensures consistent error handling regardless of which form or component triggered the error.

---

## Edge Cases Summary

| Case | Behavior |
|------|----------|
| Double-submit form | Button disabled on first click (`loading-button`). Server ignores duplicate POST. |
| Browser back after POST | Redirect-after-POST prevents re-submission. Back button shows GET result. |
| Very long error message | Truncated with "..." + tooltip showing full text. |
| Concurrent edits | Last-write-wins (no locking for solo health app). |
| JS disabled | Native `<form>` + HTML validation fallback works without HTMX. |
| `prefers-reduced-motion` | All animations disabled. Spinner static. Skeleton static. Slide transitions instant. |
| Screen reader during error | `aria-live="assertive"` for critical errors. `aria-live="polite"` for success/info. |
