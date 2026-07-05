# AI Insights Flow

## Goal
User views AI-generated daily health insight based on their past 7 days of data. Can generate new insights or browse history.

## Entry Points
- `/insights` — Today's insight (or generate button if none exists)
- Navigation link "Insights" in top-app-bar

---

## Insight Page

**Route:** `GET /insights` · `POST /insights/generate`
**Components:** `card` · `btn` · `skeleton` · `spinner` · `empty-state` · `alert`

### Page States

| State | Condition | UI |
|-------|-----------|----|
| Loading | Page loading, checking for cached insight | `skeleton` card (pulsing, matching insight card shape) |
| Cached insight exists | Today's date matches cached insight | `card`: markdown-rendered insight content |
| No insight yet | User hasn't generated one today | `card` with `empty-state`: "No insight for today" + "Generate" primary button |
| Generating | User clicked Generate, LLM is working | `card`: `spinner` (24px, centered) + "Generating your health insight..." text |
| Generated | LLM returned content | `card` renders markdown. Button changes to "Regenerate". |
| Error | LLM call failed or not configured | `alert` (error): "Could not generate insight. {reason}" + retry |
| LLM not configured | No API key set in admin | `alert` (info): "AI Coach is not configured. Ask your admin to set up an LLM provider." |

### Insight Format
Markdown-rendered text with structured sections:
1. **Key Achievement** — Acknowledgment of a positive trend or milestone
2. **Recovery Analysis** — Sleep duration + stages vs. training volume, resting heart rate context
3. **Recommendations** — 2 actionable, science-based suggestions for the next day

### History

Below current insight: list of past insights (last 30 days).

| State | UI |
|-------|----|
| Has history | `list-item` per past insight: date + preview text (first 80 chars). Click expands to full insight. |
| Expanding | `accordion`: slide-down 200ms. Full insight content visible. |
| No history | `empty-state`: "No past insights yet. Your first insight will appear here after generation." |
| Loading history | `skeleton` rows (3-4 lines) |

### Generate / Regenerate

| State | Button | Behavior |
|-------|--------|----------|
| No insight today | "Generate Insight" primary button | `POST /insights/generate?date=today` → replaces card content |
| Insight exists | "Regenerate" ghost button (secondary) | Same POST, overwrites cached insight |
| Generating | Button becomes `loading-button` (spinner + "Generating...") | Form disabled, no double-submit |
| Success | Insight card fades in (300ms). Toast: "Insight ready!" (success) | — |
| Error | Error alert in card. Button returns to normal. | — |

---

## Locale Support
Insight respects `salus_locale` cookie. System prompt adapts to locale. Fallback message also localized (EN/DE).

---

## Visual State Map

```
┌─────────────────────────────────────────────────────┐
│ TOP-APP-BAR                                         │
│ [salus]  Dashboard  Insights  Analytics ...  [👤]   │
├─────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────┐ │
│ │ 🤖 AI Health Coach              July 5, 2026   │ │
│ │                                                 │ │
│ │ **Key Achievement**                             │ │
│ │ Your step count averaged 8,200 steps this week,  │ │
│ │ up 14% from last week. Consistent movement is    │ │
│ │ the foundation of metabolic health.             │ │
│ │                                                 │ │
│ │ **Recovery Analysis**                           │ │
│ │ Sleep duration averaged 7h 18m with 22% REM —    │ │
│ │ within optimal range. Resting heart rate stayed  │ │
│ │ at 62 bpm, indicating good recovery despite      │ │
│ │ increased training volume.                      │ │
│ │                                                 │ │
│ │ **Recommendations**                             │ │
│ │ 1. Maintain current training load — your body    │ │
│ │    is adapting well. Consider a deload week in   │ │
│ │    10-14 days.                                  │ │
│ │ 2. Your sleep onset time varies by ±45 min.      │ │
│ │    Try a consistent 10:30 PM bedtime to anchor   │ │
│ │    your circadian rhythm.                       │ │
│ │                                                 │ │
│ │                               [Regenerate]       │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ┌─ History ───────────────────────────────────────┐ │
│ │ Jul 4  ▶  Your step count averaged 7,900...     │ │
│ │ Jul 3  ▶  Sleep quality improved this week...   │ │
│ │ Jul 2  ▶  Training volume increased by 15%...   │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## HTMX Events

| Trigger | Route | Target | Swap |
|---------|-------|--------|------|
| Page load | `GET /insights` | body | Full page |
| Generate | `POST /insights/generate?date=YYYY-MM-DD` | `#insight-card-container` | innerHTML |
| History expand | HTMX swap only (no API) | `.history-item-body` | innerHTML |

## Edge Cases

| Case | Behavior |
|------|----------|
| LLM call times out (30s) | Error: "Insight generation timed out. Try again." Retry button. |
| No health data for 7 days | Insight says: "Not enough data yet — log some measurements first." No error. |
| Only 1-2 days of data | Insight: "Just getting started! Keep logging data to get meaningful insights." |
| LLM returns empty / bad response | Error: "Could not generate insight." Fallback message shown. |
| User spam-clicks Generate | Button disabled after first click. Spinner visible. |
| LLM provider changed in admin | Next generation uses new provider. Cached insight stays from old provider. |
| Multiple users, shared server | Each user's insight is independent. Cached by user_id + date. |
