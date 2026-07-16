# Outgoing Webhooks

## Overview
Nutzer können eigene Webhooks konfigurieren, um Daten an externe Dienste zu senden.
Trigger-basiert: Bei neuen Einträgen, erreichten Zielen, etc.

**Abgrenzung zum existierenden Webhook-System:** Salus hat bereits einen POST /webhook Endpunkt für eingehende Daten. Dieses Feature ist der umgekehrte Weg — Salus sendet Daten raus.

## Data Model

### webhook_subscription
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| name | str | "IFTTT -> Google Sheet" |
| url | str | Ziel-URL |
| secret | str | HMAC-Secret für Signatur-Verifikation |
| is_active | bool | |
| triggers | json | `["measurement.created", "goal.achieved"]` |
| filters | json? | `{"metric_type_codes": ["weight", "steps"]}` |
| retry_on_failure | bool | |
| max_retries | int | Default 3 |
| last_triggered_at | datetime? | |
| last_status | enum? | success / failed / disabled |
| failure_count | int | 0 |
| created_at | datetime | |

### webhook_delivery
(Audit-Trail)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| subscription_id | UUID | FK → webhook_subscription |
| event_type | str | "measurement.created" |
| payload_json | json | Gesendete Payload |
| response_status | int? | HTTP Status (200, 500, etc.) |
| response_body | str? | |
| attempted_at | datetime | |
| duration_ms | int? | |
| success | bool | |

## Event Types (Trigger)

```
measurement.created     — Neuer Eintrag erstellt
measurement.updated     — Eintrag aktualisiert
measurement.deleted     — Eintrag gelöscht
goal.created            — Neues Ziel
goal.achieved           — Ziel erreicht
goal.progress           — Fortschritts-Update (könnte oft feuern!)
workout.session.completed — Workout abgeschlossen
workout.set.logged      — Satz geloggt
habit.checked           — Habit erledigt
mood.logged             — Stimmung geloggt
medication.taken        — Medikament eingenommen
medication.missed       — Einnahme verpasst
lab.panel.created       — Neues Labor-Panel
insight.generated       — Neue AI Insight
achievement.unlocked    — Achievement freigeschaltet
daily.summary           — Tägliche Zusammenfassung (scheduled, z.B. 21:00)
```

## Payload Format

```json
{
  "event": "measurement.created",
  "timestamp": "2026-07-16T14:30:00Z",
  "data": {
    "entity": "measurement",
    "id": "uuid",
    "metric_type_code": "weight",
    "value_numeric": 78.5,
    "start_time": "2026-07-16T08:00:00Z"
  },
  "user": {
    "id": "uuid",
    "display_name": "Philipp"
  }
}
```

## Security

- **HMAC-SHA256 Signatur** im `X-Salus-Signature` Header
- `sha256=HMAC(webhook.secret, payload_body)`
- Empfänger kann Signatur verifizieren mit shared secret
- Rate-Limiting: Max 1 delivery/sec pro Subscription (burst protection)
- Automatic Disable nach N aufeinanderfolgenden Fehlern

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/webhooks | List my subscriptions |
| POST | /api/v1/webhooks | Create subscription |
| GET | /api/v1/webhooks/{id} | Get subscription |
| PUT | /api/v1/webhooks/{id} | Update |
| DELETE | /api/v1/webhooks/{id} | Delete |
| POST | /api/v1/webhooks/{id}/test | Send test event |
| GET | /api/v1/webhooks/{id}/deliveries | Delivery history |
| POST | /api/v1/webhooks/{id}/retry | Retry last failed delivery |

## Frontend

- **WebhookList** — Alle Subscriptions mit Status-Indikator
- **WebhookForm** — URL, Events (Multi-Select), Filter, Secret (auto-generiert)
- **WebhookDeliveryLog** — Timeline der Deliveries mit Response-Codes
- **WebhookTestButton** — Sendet Test-Ping an Ziel-URL

## Integration Points
- **EventBus** → Existierendes SSE-System kann erweitert werden um Webhook-Dispatch
- **Write Pipeline** → Nach jedem Commit: Event an EventBus → Webhook-Dispatcher subscribed
- **Settings** → Neuer Settings-Bereich "Integrations" / "Webhooks"

## Open Questions
- Templating: Soll der User das Payload-Format anpassen können oder ist es fix?
- Built-in Integrationen: Soll es vorkonfigurierte Templates für IFTTT, Make, Zapier, Home Assistant geben?
- Daily Summary: Scheduled Trigger (Cron-ähnlich) oder nur Event-getriggert?
- Batch-Delivery: Mehrere Events zu einer Delivery bündeln?
- Soll es ein "Request Bin"-ähnliches Debug-Feature geben um Payload zu inspizieren?

## Ergänzungen von Philipp
Der User soll das Payload Format anpassen können
Ja, wir wollen vorkonfigurierte templates bereitstellen
Scheduled und Event triggered
Batch-Delivery: kann man machen
Ja, Request Bin Debug Feature klingt gut