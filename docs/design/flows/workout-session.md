# Workout Session Flow

## Goal
User browses training plans, starts a workout session, logs sets in real time (with autoregulation), and completes the session.

## Entry Points
- `/workouts/plans` — Browse plans, start session
- `/workouts/exercises` — Exercise catalog
- `/workouts/sessions/active` — Active session (only when one exists)

---

## Plan Browsing & Creation

**Route:** `GET /workouts/plans` · `GET /workouts/plans/new` → `POST /workouts/plans`
**Components:** `card` · `chip` · `plan-card` · `modal` · `input` · `select` · `stepper` · `btn`

### Plans Page

| State | UI |
|-------|----|
| Has plans | List of `plan-card` components. Each: name + autoreg chip + exercise list + Start/Delete |
| No plans | `empty-state`: "No training plans yet" + "Create Plan" CTA |
| Active session exists | Banner at top: "Active session in progress" + "Continue Session" primary button |

### Create Plan Form

| Field | Component | Notes |
|-------|-----------|-------|
| Plan Name | `input` | Required |
| Description | `textarea` | Optional |
| Autoreg Mode | `select` (Disabled/Advisory/Guided) | Default: Advisory |
| Exercise 1-5 | `select` (from catalog) | Each: exercise + `stepper` (sets, reps, RPE) + lock checkbox |

| State | UI |
|-------|----|
| Open | Modal form, up to 5 exercise rows |
| Submit | `loading-button` |
| Success | Redirect to `/workouts/plans`. New plan card appears at top. |
| No exercises in catalog yet | "Create exercises first" link to `/workouts/exercises` |

---

## Exercise Catalog

**Route:** `GET /workouts/exercises` · `GET /workouts/exercises/new` → `POST /workouts/exercises`
**Components:** `exercise-item` · `chip` · `modal` · `input` · `select` · `btn`

### Exercise Item

| Element | Spec |
|---------|------|
| Name | `--font-body-md`, 600 weight |
| Equipment | `chip` (neutral) with icon |
| Muscles | `--font-body-sm`, `--color-slate-500` |
| Video link | `link` (action variant) with play icon |
| Delete | Icon button (× 20px), visible on hover, requires `confirm` |

| State | UI |
|-------|----|
| Has exercises | List of `exercise-item` components |
| No exercises | `empty-state`: "No exercises yet" + "Create Exercise" CTA |

---

## Active Session (Core Workout Flow)

**Route:** `GET /workouts/sessions/active` · `POST /api/v1/workouts/sessions/log` · `POST /workouts/sessions/complete`
**Components:** `active-session` · `autoregulation-set` · `stepper` · `input` · `btn` · `chip` · `progress-bar`

### Session Start

| Step | Route | UI |
|------|-------|----|
| Click "Start Session" on plan | `POST /workouts/sessions/start?plan_id=X` | — |
| Redirect | → `/workouts/sessions/active` | Session page loads |
| Free-form (no plan) | `POST /workouts/sessions/start` (no plan_id) | Session with empty exercise list |

### Session Page Layout

```
┌─────────────────────────────────────────────────┐
│ TOP-APP-BAR                                     │
├─────────────────────────────────────────────────┤
│ Plan: Upper/Lower Split   [Advisory]            │  ← Autoreg chip
│ Recovery: 85% ● Normal                         │  ← Recovery score
├─────────────────────────────────────────────────┤
│ EXERCISES                                       │
│ ┌───────────────────────────────────────────────┐│
│ │ Barbell Squat                    3×8 @ RPE 7 ││
│ │ Est. 1RM: 95kg                                ││
│ │ ┌───────────────────────────────────────────┐ ││
│ │ │ Set 1  [80kg] [8 reps] [☑ Log]           │ ││  ← Autoreg set
│ │ │ Set 2  [80kg] [7 reps] [☑ Log]           │ ││
│ │ │ Set 3  [82kg] [8 reps] [✓ Logged]        │ ││  ← Logged: 0.75 opacity
│ │ └───────────────────────────────────────────┘ ││
│ └───────────────────────────────────────────────┘│
│ ┌───────────────────────────────────────────────┐│
│ │ Bench Press                      3×10 @ RPE 6││
│ │ ...                                          ││
│ └───────────────────────────────────────────────┘│
├─────────────────────────────────────────────────┤
│ NOTES                                           │
│ ┌───────────────────────────────────────────────┐│
│ │ [Felt good today. Left knee a bit tight.]     ││
│ └───────────────────────────────────────────────┘│
├─────────────────────────────────────────────────┤
│                      [Complete Session]          │
└─────────────────────────────────────────────────┘
```

### Set Logging

**Route:** `POST /api/v1/workouts/sessions/log` (JSON body)
**Components:** `autoregulation-set` · `stepper` · `btn`

| State | UI |
|-------|----|
| Pending | Shows target (weight × reps @ RPE). Inputs pre-filled with autoreg target. Log button active. |
| Logging | Button becomes spinner. Inputs disabled. |
| Logged | Row dims to 0.75 opacity. Button → ✓ checkmark. Values shown as text. 1RM updates. |
| Disabled (max sets reached) | All inputs disabled. Log button hidden. "All sets completed" chip. |
| Error | `toast` (error): "Could not log set — Retry". Row stays in pending state. |

### Autoregulation Display
- **Advisory:** Shows calculated target (based on previous session RPE). User can override.
- **Guided:** Same but changes are highlighted with "Suggested: X" chip.
- **Disabled:** Shows original plan target only. No calculated 1RM.

### Complete Session

| State | UI |
|-------|----|
| Click "Complete" | `confirm` dialog: "Complete this workout?" + "All {N} sets logged" + Cancel + Complete |
| Completing | Complete button loading. Form disabled. |
| Success | Redirect to `/workouts/plans`. `toast` (success): "Workout completed! 3,200kg total volume". |
| Error | `toast` (error): "Could not complete session — please try again." |

---

## HTMX Events

| Trigger | Route | Target | Method |
|---------|-------|--------|--------|
| Start session | `POST /workouts/sessions/start?plan_id=X` | — | Redirect |
| Active page load | `GET /workouts/sessions/active` | body | Full page |
| Log set | `POST /api/v1/workouts/sessions/log` | — | JSON (client updates DOM) |
| Complete session | `POST /workouts/sessions/complete` | — | Redirect |
| Auto-refresh 1RM | `GET /api/v1/workouts/plans/{id}/targets` | 1RM display | innerHTML (after each logged set) |

## Edge Cases

| Case | Behavior |
|------|----------|
| No active session | `/workouts/sessions/active` redirects to `/workouts/plans` |
| Log set beyond target | Allowed (user can do extra). Target shows exceeded count: "4/3 sets". |
| RPE input out of range | Client-side validation: min 1, max 10. `stepper` enforces bounds. |
| Session timeout (browser closed mid-workout) | Session persists server-side. Re-opening browser → active session still exists. |
| Plan with 0 exercises | Session starts with empty list + "Add exercises" CTA. |
| User deletes plan mid-session | Session remains active. Plan name changes to "Custom Session". |
| Complete with zero logged sets | Allowed (empty workout). Marks session complete with 0 volume. |
