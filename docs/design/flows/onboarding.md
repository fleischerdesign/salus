# Onboarding Flow

## Goal
New user sets up their account, creates an API token, logs first measurement, and sets first goal. After completion, sees a populated dashboard.

## Entry Points
- After registration → auto-login → redirect to `/`
- Dashboard loads, `onboarding_dismissed=False` → modal appears

## Preconditions
- User authenticated
- User has zero metric types (or sees existing ones in dropdown)
- `user.onboarding_dismissed == False`

---

## Steps

### Step 0: Connect a Data Source (API Token)

**Route:** `GET /onboarding/step/0/modal` → `POST /onboarding/token`
**Components:** `modal` · `wizard` · `step-indicator` · `input` · `btn` · `inline-code` · `copy-to-clipboard`

| State | Modal Content | User Action |
|-------|--------------|-------------|
| Default | Step 0 content: description text + token label input + "Generate Token" primary button | User enters label, clicks Generate |
| Generating | Button → `loading-button` (spinner, "Generating...") | Wait |
| Success | Token displayed: `inline-code` with bare token + `copy-to-clipboard` button + webhook URL | User copies token, shares with wearables app |
| Error | `alert` (error variant) above form, retry CTA | User clicks retry |

**Modal structure:**
- Backdrop + Card (max 440px)
- Step indicator: 3 dots, step 0 active (`--color-primary-500`)
- Body: swaps content via `hx-target="closest .onboarding-step-body"`
- Footer: Back (disabled on step 0) · Skip (ghost link, skips optional step)

---

### Step 1: Log Your First Entry

**Route:** `POST /onboarding/entry` (form: `metric_type_id`, `value`)
**Components:** `select` · `input` · `btn`

| State | Form | User Action |
|-------|------|-------------|
| Default | Metric dropdown (all user metrics) + value input + "Log Entry" button | User selects metric, enters value |
| Submitting | Button loading, form disabled | Wait |
| Success | Result card: ✓ icon (48px, `--color-tertiary`), "Entry logged!" + auto-advances to next step after 1.5s | None (auto) |
| Error | `alert` (error) below form, form remains interactive | Fix input, retry |
| Skip | No data sources yet? "Create a metric type first" link → navigates to `/metrics` | User creates metric, returns |

---

### Step 2: Set Your First Goal

**Route:** `POST /onboarding/goal` (form: `metric_type_id`, `target_value`, `direction`)
**Components:** `select` · `stepper` · `btn`

| State | Form | User Action |
|-------|------|-------------|
| Default | Metric dropdown + target value stepper + direction (increase/decrease) + "Set Goal" button | User selects, sets target, submits |
| Submitting | Button loading | Wait |
| Success | Result card: 🎯 icon (48px, `--color-primary`), "Daily goal set!" + "Finish" button | User clicks Finish or modal auto-dismisses |
| Error | `alert` (error) below form | Retry |

---

### Completion

When all 3 steps completed:
1. `POST /onboarding/dismiss` sets `onboarding_dismissed = True`
2. Modal closes (fade-out 200ms)
3. Dashboard appears behind modal
4. Dashboard widgets auto-populate: `widget_svc.ensure_defaults(user_id)` creates one widget per metric type

---

## Visual State Map

```
┌─────────────────────────────────────────────────────────┐
│ DASHBOARD (behind modal)                                 │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│ │ Steps   │ │ Widget  │ │ Widget  │ │ Widget  │ ...    │
│ │ Widget  │ │         │ │         │ │         │        │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘        │
│                                                         │
│ ┌───────────────────────────────────────────────────┐   │
│ │ ONBOARDING MODAL (on top)                          │   │
│ │ ● ○ ○  Step 0/3                                   │   │
│ │                                                    │   │
│ │  [sync icon 48px]                                  │   │
│ │  Connect a Data Source                             │   │
│ │  Generate an API token to connect wearables         │   │
│ │                                                    │   │
│ │  ┌─────────────────────────────────────────┐      │   │
│ │  │ Token Label: [____________________]      │      │   │
│ │  └─────────────────────────────────────────┘      │   │
│ │                                                    │   │
│ │  [Generate Token]    Skip                        │   │
│ └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## HTMX Events

| Trigger | Route | Target | Swap |
|---------|-------|--------|------|
| Modal open | `GET /onboarding/step/{n}/modal` | `#onboarding-modal-container` | innerHTML |
| Generate token | `POST /onboarding/token` | `.onboarding-step-body` | innerHTML |
| Log entry | `POST /onboarding/entry` | `.onboarding-step-body` | innerHTML |
| Set goal | `POST /onboarding/goal` | `.onboarding-step-body` | innerHTML |
| Dismiss | `POST /onboarding/dismiss` | — | — |
| Step advance (client) | JS: hide current, show next | Modal body | visibility toggle |

## Edge Cases

| Case | Behavior |
|------|----------|
| User has no metric types | Step 1 shows "Create your first metric" link → opens `/metrics` in new tab or modal |
| User already has metrics | Dropdown pre-populated, select shows all metrics |
| User closes browser mid-wizard | Resumes where left off on next login (steps are independent page loads, not persisted state) |
| Token generation fails | Error alert: "Could not generate token. Please try again." Retry button. |
| User skips token step | Steps 1 and 2 still functional. Token can be created later in Settings. |
| All 3 completed | Auto-dismiss. Modal fades out, dashboard visible. Widgets populated. |
| User clicks backdrop (not close button) | Does nothing (modal is persistent during onboarding) |
