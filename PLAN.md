# PLAN.md — salus

Health data tracking platform. This document defines the feature roadmap.
Phases are ordered by priority and dependency. Each phase builds on the previous.

---

## Phase 1: Foundation (COMPLETE)

- FastAPI + Jinja2 + HTMX skeleton
- Metric types CRUD (name, unit, data_type, color)
- Entry logging with timestamps, notes
- Dashboard with per-metric entry tables
- Samsung Health Connect webhook ingestion
  - Multi-format payload parser (Protocol-based)
  - Nutrition deduplication logic
  - Bearer token authentication
- Two-database architecture (salus.db SQLModel + health.db raw sqlite3)
- Nix flake dev environment (python313, uv, ruff, pyright)
- 32 passing tests

---

## Phase 2: Multi-User & Authentication

### User model
- `id`, `username`, `password_hash` (bcrypt/argon2), `email`, `display_name`, `created_at`
- `UserRepository`, `UserService`

### Authentication methods
- **Username/Password**: Register, login, logout
- **OIDC**: OpenID Connect provider integration (Google, GitHub), configurable per instance
- **OAuth 2.0**: Authorization code flow for external apps, token introspection
- **LDAP**: Bind authentication against directory server (Active Directory, OpenLDAP)
- JWT-based session tokens (cookie + Bearer)
- Auth middleware: `get_current_user` dependency
- Auth router: POST `/auth/register`, POST `/auth/login`, GET `/auth/callback`
- Token refresh, logout invalidation

### Multi-tenant scoping
- `user_id` foreign key on metric_type, entry, goal tables
- All existing CRUD endpoints become user-scoped via `get_current_user`
- Health webhook optionally accepts `X-User-ID` header for association

### Authorization
- Role system: admin, user (extensible)
- Admin panel: user management, system health

### Tech
- `python-jose` for JWT, `passlib[bcrypt]` for password hashing
- `authlib` for OAuth/OIDC client flows
- `ldap3` for LDAP bind
- Config per auth provider via `SALUS_AUTH_*` env vars

---

## Phase 3: Analytics & Dashboards

### Migrate health_query.py functionality into services
- **Steps trend**: Bar chart, N-day range, Samsung 22:00 day boundary
- **Sleep analysis**: Duration, stages (Wach/Leicht/Tief/REM), trends
- **Heart rate**: Resting, average, spikes, hourly breakdown
- **Weight trend**: Delta, timeline bar chart, min/max
- **SpO2 monitoring**: History with alerts for sustained low readings
- **Exercise history**: Type names (84 mapped), duration, distance, calories
- **Nutrition summary**: Calories per day, macro breakdown
- **TDEE calculator**: BMR (Cunningham formula), HRR→PAL calibration, energy balance
- **Status overview**: Database statistics (record counts by type, last sync)

### Chart integration
- Chart.js loaded via CDN
- Interactive time range selectors (7d, 30d, 90d, 1y, custom)
- Per-metric chart pages
- Dashboard widgets (user-configurable)
- Data export buttons (CSV, JSON)

### Architecture
- `AnalyticsService` reading from `HealthRecordRepository` (raw sqlite3)
- `ChartService` preparing Chart.js compatible datasets
- New templates in `templates/pages/analytics/`
- HTMX lazy-loads chart data to keep initial page load fast

---

## Phase 4: Goals & Tracking

### Goal model
- `id`, `user_id FK`, `metric_type_id FK`, `target_value`, `operator` (> , < , =)
- `frequency` (daily, weekly, monthly), `deadline`, `is_active`
- `GoalRepository`, `GoalService`

### Goal features
- Create/edit/delete goals per metric type
- Progress tracking: current streak, percentage to target
- Visual progress bars on dashboard
- Achieved goals archive
- Failed goals (with reason if available)

---

## Phase 5: Integrations & Export

### Additional health data sources
- **Apple Health**: Export XML / HealthKit webhook → new parser class
- **Google Fit**: REST API → new parser class
- **Fitbit**: Web API → new parser class
- **Oura Ring**: Cloud API → new parser class
- Each integration implements `RecordParser` Protocol, zero changes to existing parsers

### Data export
- CSV export: filtered by metric, date range, user
- JSON export: full structured data
- PDF report: summary dashboard (Jinja2 → WeasyPrint/pdfkit)
- Scheduled exports (email delivery)

### REST API
- JSON API for third-party tool access
- API key management (generate, revoke, scope)
- OpenAPI documentation at `/docs`
- Rate limiting per key

---

## Phase 6: Community & Social

### Data sharing
- Share metric dashboards with specific users or via public link
- Permission levels: view-only, view+comment, full
- Shared dashboard with comparison overlays (their data vs. yours)

### Challenges
- Steps challenges (joinable/leavable)
- Leaderboard per challenge (ranked, anonymized or named)
- Achievement badges ("30-day streak", "10k steps 100 days")

### Custom dashboards
- Widget-based dashboard builder
- Drag-and-drop layout (persisted)
- Widget types: chart, number, progress bar, table, text
- Shareable widget configurations

### Gamification
- XP system for consistency (daily logging, streaks, goal completion)
- Level progression
- Cosmetic rewards (themes, custom colors)

---

## Phase 7: Platform & Distribution

### Progressive Web App (PWA)
- Service worker for offline caching
- Manifest for homescreen installation
- Background sync for offline entry logging

### Notifications
- Push notifications via Web Push API
- Email notifications (SMTP, configurable)
- Webhook notifications (user-defined URL)
- Notification preferences per user
- Trigger types: goal reached, goal at risk, new data synced, weekly summary

### Mobile companion
- Responsive-first design (already mobile-friendly with HTMX)
- Potential React Native / Flutter app if native sensors needed
- Or: PWA as primary mobile experience

### Administration
- System health dashboard (CPU, memory, disk, DB size)
- Audit log (who did what when)
- Backup/restore (automatic SQLite backup, configurable schedule)
- Migration tools for schema changes

---

## Technology Stack Expansion

| Phase | New Dependencies |
|---|---|
| 2 | `python-jose`, `passlib[bcrypt]`, `authlib`, `ldap3` |
| 3 | `chart.js` (frontend CDN, no Python dep) |
| 5 | `weasyprint` or `pdfkit` (PDF export), `httpx` (external API clients) |
| 6 | — (no new Python deps, frontend JS for drag-and-drop) |
| 7 | `aiosmtplib` (email), `pywebpush` (push notifications) |

---

## Database Evolution

### Current
```
salus.db:  metric_type, entry
health.db: health_records
```

### Phase 2
```
salus.db:  user, metric_type (user_id FK), entry (user_id FK)
health.db: health_records (user_id nullable)
```

### Phase 4
```
salus.db:  + goal
```

### Phase 6
```
salus.db:  + challenge, challenge_participant, badge, user_badge, shared_dashboard
```

---

## Non-Functional Requirements (NFR)

| NFR | Target |
|---|---|
| Test coverage | ≥ 80% (currently at project start) |
| Lint/type | Zero ruff errors, zero pyright errors |
| Response time | < 200ms for dashboard page load (excluding charts) |
| Ingestion throughput | ≥ 100 records/second (health webhook) |
| Browser support | Modern browsers (last 2 versions), no IE |
| Accessibility | WCAG 2.1 AA (semantic HTML, ARIA labels, keyboard nav) |
| i18n | Prepared for i18n (extract strings), German first, English as fallback |
