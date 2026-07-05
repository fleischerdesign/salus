# Dashboard Flow

## Goal
User opens dashboard, sees health data for today, navigates dates, manages widgets.

## Entry Points
- `GET /` — main dashboard, loads today by default
- `GET /dashboard/grid?date=YYYY-MM-DD` — HTMX partial for date navigation
- Navigation link "Dashboard" in top-app-bar

---

## Page Load Sequence

### Initial Load (`GET /`)

| Stage | Duration | Visual | Components |
|-------|----------|--------|------------|
| HTML arrives | 0ms | Blank page | `top-app-bar` |
| Widget grid HTMX load | 100-500ms | `skeleton` cards (4-6 widgets) pulsing | `skeleton` · `card` |
| Data arrives | 500ms-2s | Widgets populate with data | `widget` · `viz-*` · `stat` |
| Empty metrics | instant | `empty-state` in widgets without data | `empty-state` |
| No widgets at all | instant | Full-page `empty-state` "Add your first widget" | `empty-state` · `btn` |

### Loading Hierarchy
1. Page shell renders immediately (top-app-bar, container)
2. Day navigator shows today's date
3. Widget grid loads via HTMX → skeleton cards
4. Each widget fetches its data → viz component renders
5. Empty widgets show `empty-state` component

---

## Day Navigation

**Route:** `GET /dashboard/grid?date=YYYY-MM-DD`
**Components:** `day-navigator` · `btn` · `icon`

| State | Day Navigator | Grid |
|-------|-------------|------|
| Today | "Today" button hidden. Date shows "Wed, Jul 5, 2026" | Today's widgets |
| Past date | "Today" button visible. Date shows past date. Next arrow active if date < today | Date's widgets |
| Earliest date | Prev arrow hidden | Earliest data |
| Next = today | Next arrow disabled | — |

**Interaction:**
- Click prev arrow → `hx-get /dashboard/grid?date=YYYY-MM-DD` → swaps `#dashboard-content`
- Click next arrow → same, next date
- Click date text → opens native `<input type="date">` → `hx-trigger="change"` → same
- Click "Today" → loads today

---

## Widget Management

### Add Widget

**Route:** `GET /dashboard/widgets/add-modal` → `POST /dashboard/widgets/add`
**Components:** `modal` · `select` · `btn`

| State | UI |
|-------|----|
| Click "Add Widget" | `modal` opens: Metric dropdown + Size (small/medium/large) + "Add" button |
| Submit | `loading-button` |
| Success | Widget HTML appended to grid via `hx-swap="beforeend"` + `HX-Trigger: widgetAdded` event |
| No metrics available | "Create a metric type first" link |
| Error | `alert` (error) in modal, form stays |

### Edit Widget Size

**Route:** `GET /dashboard/widgets/{id}/edit` → `PUT /dashboard/widgets/{id}`
**Components:** `modal` · `radio-group` · `btn`

| State | UI |
|-------|----|
| Click edit icon (pencil) | `modal` opens: Size selection (small/medium/large) |
| Submit | `loading-button` |
| Success | 204 + `HX-Trigger: widgetRefresh-{id}` → grid re-fetches widget |
| Cancel | Modal closes, no change |

### Reorder Widgets (Drag & Drop)

**Route:** `POST /dashboard/widgets/reorder` (form: `ids=1,2,3,...`)
**Components:** `drag-handle` · `widget`

| State | UI |
|-------|----|
| Edit mode OFF | Widgets static, no drag handles, no add button |
| Enter edit mode | "Edit Layout" button toggles on. Drag handles appear (left edge). Add button appears. |
| Dragging | SortableJS: drag ghost (dashed primary border, 0.4 opacity). Drop snaps to grid. |
| Drop | `POST /dashboard/widgets/reorder` → 204. New order saved. |
| Drag failure | Console error. Order reverts to last saved state (debounced). |
| Edit mode ON + mobile | Touch drag via SortableJS. Edit mode visible. "Done" button exits edit mode. |

### Delete Widget

**Route:** `DELETE /dashboard/widgets/{id}`
**Components:** `confirm` · `btn`

| State | UI |
|-------|----|
| Click delete icon (trash) | `confirm` dialog: "Remove {widget_name} widget?" + Cancel + Delete buttons |
| Confirm | `DELETE /dashboard/widgets/{id}` → 200 |
| Success | Widget row fades out (200ms), grid reflows |
| Last widget deleted | Empty state: "Add your first widget" CTA |

---

## Widget Data Display

### Widget States

| State | Trigger | Visual |
|-------|---------|--------|
| Loading (initial) | Widget just added or page just loaded | `skeleton` matching widget size |
| Data loaded | Data from service | `viz-*` component renders (bar, number, sparkline, etc.) |
| No data today | Metric has no entry for this date | `empty-state` (compact, inside widget) |
| Error | Service call failed | `empty-state` with error icon + "Could not load data" + retry button |
| Stale (cached) | Data hasn't refreshed in >5 min | Subtle indicator: dot in widget header, "Updated 12m ago" tooltip |

### Widget Refresh
- Each widget auto-refreshes via HTMX polling (`hx-trigger="every 60s"`)
- On refresh: `aria-live="polite"` on widget body
- Delta indicator updates (↑ / ↓ arrows) with anim-number transition

---

## Visual State Map

```
┌─────────────────────────────────────────────────────┐
│ TOP-APP-BAR                                         │
│ [salus]  Dashboard  Insights  Analytics  ...  [👤]  │
├─────────────────────────────────────────────────────┤
│ DAY NAVIGATOR                                       │
│ [←]  Wednesday, July 5, 2026  [→]        [Today]   │
├─────────────────────────────────────────────────────┤
│ WIDGET GRID (4 columns)              [Edit Layout]  │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│
│ │ 👣 Steps │ │ ❤️ HR    │ │ 😴 Sleep │ │ ⚖️ Weight ││
│ │  8,432   │ │  72 bpm  │ │  7h 32m  │ │  78.2 kg  ││
│ │  ↑ 12%   │ │  → 0%    │ │  ↑ 5%    │ │  ↓ 1.3kg  ││
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘│
│ ┌──────────┐ ┌──────────┐                           │
│ │ 🍎 Cals  │ │ + Add    │                           │
│ │  2,100   │ │ Widget   │                           │
│ │  ↓ 3%    │ │          │                           │
│ └──────────┘ └──────────┘                           │
└─────────────────────────────────────────────────────┘
```

## HTMX Events

| Trigger | Route | Target | Swap |
|---------|-------|--------|------|
| Page load | `GET /` | body | Full page |
| Prev/Next day | `GET /dashboard/grid?date=` | `#dashboard-content` | innerHTML |
| Date picker change | `GET /dashboard/grid?date=` | `#dashboard-content` | innerHTML |
| Add widget (open modal) | `GET /dashboard/widgets/add-modal` | `#modal-container` | innerHTML |
| Add widget (submit) | `POST /dashboard/widgets/add` | `#dashboard-grid` | beforeend |
| Edit widget (open) | `GET /dashboard/widgets/{id}/edit` | `#modal-container` | innerHTML |
| Edit widget (submit) | `PUT /dashboard/widgets/{id}` | — | 204 + trigger refresh |
| Delete widget | `DELETE /dashboard/widgets/{id}` | widget row | delete (outerHTML swap) |
| Reorder | `POST /dashboard/widgets/reorder` | — | 204 |
| Widget auto-refresh | `GET /dashboard/widgets/{id}` | `#widget-{id}` | innerHTML |

## Edge Cases

| Case | Behavior |
|------|----------|
| First visit, no widgets | `widget_svc.ensure_defaults()` creates one per metric. If still none, empty state CTA. |
| No data for today | Each widget shows `empty-state`. Day navigator still works — user can navigate to past dates with data. |
| All widgets deleted | Full-page empty state: "Your dashboard is empty" + "Add Widget" primary button. |
| Network error on load | Dashboard shell loads (cached HTML). Widget areas show `empty-state` with "Could not load — Retry" button. |
| Network error on widget add | `alert` (error) in modal: "Could not add widget." Form stays. |
| Network error on reorder | Widgets snap back to last saved order (client-side state preserved). `toast` (error): "Could not save order — Retry?" |
| User leaves edit mode on | Edit mode auto-disables after 5 min of inactivity. Tooltip: "Edit mode disabled due to inactivity." |
| Drag to same position | No API call. Drop detected as no-change. |
