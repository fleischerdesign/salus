# Settings & Admin Flow

## Goal
User manages their account, API tokens, theme, locale, and privacy settings. Admins manage users, config, plugins, and backups.

## Entry Points
- `/settings` — Account settings (default tab)
- `/settings/privacy` — Privacy + data export
- `/settings/shares` — Encrypted doctor shares
- `/admin` — Admin panel (requires `is_admin=True`)

---

## Account Settings (`/settings`)

**Components:** `tabbed-sidebar` · `input` · `btn` · `alert` · `theme-toggle` · `api-token-form`

### Tab Navigation
| State | UI |
|-------|----|
| Desktop | `tabbed-sidebar` (240px, left) + Content area. Three tabs: Account · Privacy · Shares |
| Tablet (< 900px) | Sidebar → horizontal scrollable tab row above content |
| Active tab | `--color-primary-50` bg, `--color-primary` text, `3px solid --color-primary` left border |

### Change Password

**Route:** `POST /settings/change-password`
**Components:** `input` · `btn` · `alert`

| State | UI |
|-------|----|
| Form | Current password + New password (×2, confirm) + "Change Password" button |
| Submit | `loading-button` |
| Success | `toast` (success): "Password changed". Form clears. |
| Wrong current password | `alert` (error) above form: "Current password is incorrect" |
| Passwords don't match | Client-side validation. Field error: "Passwords do not match" |

### API Token Management

**Route:** `GET /settings/api-tokens/new` → `POST /settings/api-tokens`
**Components:** `input` · `btn` · `inline-code` · `copy-to-clipboard` · `secret-reveal`

| State | UI |
|-------|----|
| Token list | List of existing tokens. Each: label + prefix (e.g., `s3ns0r...2026`) + copy button + revoke (×) |
| No tokens | `empty-state`: "No API tokens yet" + "Create Token" CTA |
| Create form | Modal: label input + scope checkboxes (ingest:write) + "Generate Token" |
| Token created | Modal shows `inline-code` with bare token + `copy-to-clipboard` button + warning: "Copy now — you won't see this again" |
| Revoke token | `confirm` dialog → `DELETE /settings/api-tokens/{id}` → token row fades out |
| Reveal token (for existing) | `secret-reveal`: masked (`************`) → click fetches via server → shows plaintext |

### Theme Toggle

**Route:** `POST /settings/theme`
**Components:** `radio-group` · `theme-toggle` · `icon`

| State | UI |
|-------|----|
| Three options | `radio-group`: System (auto) · Light · Dark. Each with iconic representation |
| Select | `POST /settings/theme` (form: `theme`) → redirect to `/settings` → `<html data-theme>` updates |
| System selected | CSS `prefers-color-scheme` media query handles auto-switching |

### Locale

**Route:** `POST /settings/locale`
**Components:** `select`

| State | UI |
|-------|----|
| Dropdown | `select`: EN (English) · DE (German) |
| Select | Cookie `salus_locale` set (1 year, httponly). Page reloads in new locale. |

---

## Privacy Settings (`/settings/privacy`)

**Components:** `btn` · `alert`

### Data Export

**Route:** `GET /export/download?format=csv|json&since=&until=`
**Components:** `select` · `date-picker` · `btn`

| State | UI |
|-------|----|
| Form | Format (CSV/JSON) + date range (since/until, optional) + "Export" button |
| Downloading | `loading-button` "Exporting..." |
| Success | Browser downloads file. `toast` (success): "Export complete" |
| Error | `alert` (error): "Could not export data" |

### Open Science

**Route:** `POST /api/v1/open-science/synthesize`

| State | UI |
|-------|----|
| Enable | Toggle + description text about privacy-preserving data donation |
| No data | Disabled toggle: "Log data first to contribute" |

---

## Shares (`/settings/shares`)

**Components:** `btn` · `input` · `table` · `chip` · `confirm`

### Doctor Share (Encrypted)

| State | UI |
|-------|----|
| Recipients list | `table`: Name + Public Key (truncated) + Actions (delete) |
| Create recipient | Modal: Name + RSA Public Key textarea + "Add" |
| Create share | Select recipient + select metrics + optional expiration + "Generate Share Link" |
| Share created | `card`: share URL + copy button + QR code + expiration date |
| Doctor views share | Public page `/share/doctor/{share_id}` with encrypted payload. Decryption client-side in browser. |

---

## Admin Panel (`/admin`)

**Auth:** `is_admin=True` required. Non-admin users get 403 redirect to `/`.

**Components:** `tabbed-sidebar` · `table` · `btn` · `modal` · `input` · `confirm` · `chip`

### General Tab (`/admin`)

| Section | Content |
|---------|---------|
| System Stats | Users: N · Measurements: N · Metric Types: N |
| Storage | Database size · Backup status · Disk usage |
| Config | Key-value table with inline edit. Secret values masked via `secret-reveal`. |

### Users Tab (`/admin/users`)

| State | UI |
|-------|----|
| User list | `table`: Username · Email · Metrics · Admin · Active · Actions |
| Toggle admin | `POST /admin/users/{id}/toggle-admin` → row updates via HTMX |
| Toggle active | `POST /admin/users/{id}/toggle-active` → soft-disable user |
| View detail | `GET /admin/users/{id}/detail` → modal with full user info |
| Delete user | `confirm` dialog → `DELETE /admin/users/{id}` → row removed |
| Delete self | Prevented: "You cannot delete your own account" |

### Plugins Tab (`/admin/plugins`)

| State | UI |
|-------|----|
| Plugin list | `table`: Name · Version · Status (enabled/disabled) · Actions |
| Upload | `upload` component (drag-and-drop .zip) |
| Toggle enable | `POST /admin/plugins/{id}/toggle?enable=true` |
| Uninstall | `confirm` → `DELETE /admin/plugins/{id}` |

### Backups

**Route:** `POST /admin/backups/run` · `DELETE /admin/backups/{filename}`
**Components:** `btn` · `loading-button` · `table`

| State | UI |
|-------|----|
| Backup list | `table`: Filename · Size · Date · Actions (download/delete) |
| Create backup | Button → `loading-button` "Running backup..." → row appears on complete |
| No password configured | Disabled button: "Backup password not set in config" |
| Delete backup | `confirm` → row removed |

---

## HTMX Events

| Trigger | Route | Target | Method |
|---------|-------|--------|------|
| Settings page | `GET /settings` | body | Full page |
| Tab switch | `GET /settings/{tab}` | `#settings-content` | innerHTML (or full page) |
| Change password | `POST /settings/change-password` | — | Redirect/render |
| Create token | `POST /settings/api-tokens` | modal body | innerHTML |
| Delete token | `DELETE /settings/api-tokens/{id}` | — | 200 |
| Theme change | `POST /settings/theme` | — | Redirect |
| Locale change | `POST /settings/locale` | — | Redirect |
| Export | `GET /export/download?format=&...` | — | Download (StreamingResponse) |
| Admin page | `GET /admin` | body | Full page (admin check) |
| Admin tab | `GET /admin/{tab}` | `#admin-content` | innerHTML |
| Toggle admin/active | `POST /admin/users/{id}/toggle-*` | user table | innerHTML |

## Edge Cases

| Case | Behavior |
|------|----------|
| Token shown once, user navigates away | Token is gone. Must create a new one. Warning text prominent. |
| Change password while LDAP user | Not available (LDAP users have no local password). Section hidden. |
| Admin deletes self | Prevented server-side. Button disabled with tooltip. |
| Backup without encryption password | Feature disabled. "Configure SALUS_BACKUP_PASSWORD to enable backups." |
| Export with no data | Empty CSV/JSON file (headers only). Not an error. |
| Large export (>100k records) | Streamed response. Browser shows download progress. No server timeout. |
| Non-admin visits /admin | 403 → redirect to `/`. Toast: "Access denied — admin only." |
