# Salus 2.0 — Push-Benachrichtigungen & Background Sync
**Dokument:** `23-push-notifications-and-background-sync.md`  
**Status:** Verbindlich  
**Zweck:** Web Push API (VAPID), lokales Zirkadian-Scheduling, Service Worker Push Handler und Offline-Background-Sync.

---

## 1. Benachrichtigungs-Kategorien & Zirkadianes Scheduling

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ KATEGORIE             │ ZEITPUNKT / AUSLÖSER  │ INHALT DER MITTEILUNG                   │
├───────────────────────┼───────────────────────┼─────────────────────────────────────────┤
│ **Zirkadian-Koffein** │ 14:30 Uhr (Dynamisch) │ "☕ Koffein-Cutoff erreicht: Jetzt auf   │
│                       │                       │ Wasser wechseln für optimalen Tiefschlaf│
├───────────────────────┼───────────────────────┼─────────────────────────────────────────┤
│ **Fasten-Abschluss**  │ Nach 16h / Zielzeit   │ "⏳ Fastenziel erreicht (16h Autophagie)│
│                       │                       │ Erstes Essen kann vorbereitet werden."  │
├───────────────────────┼───────────────────────┼─────────────────────────────────────────┤
│ **Medikamenten-Dosis**│ Feste Uhrzeit (z.B. 8)│ "💊 Morgendosis fällig: 1x L-Thyroxin   │
│                       │                       │ [ 1-Tap Abhaken ]"                      │
├───────────────────────┼───────────────────────┼─────────────────────────────────────────┤
│ **Hydration-Reminder**│ Inaktivität > 3h      │ "💧 Ziel bisher 40%: Jetzt 250ml trinken│
│                       │                       │ [ +250ml eintragen ]"                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Service Worker Push- & Action-Handler (`service-worker.js`)

Benachrichtigungen erlauben direkte Aktionen ohne Öffnen der App:

```javascript
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'log_water_250') {
    event.waitUntil(
      // Schreibt direkt in die IndexedDB Outbox
      addWaterOutboxOp(250)
    );
  } else if (event.action === 'check_med') {
    event.waitUntil(
      checkMedicationOutboxOp(event.notification.data.medicationId)
    );
  } else {
    // Standard: App öffnen
    event.waitUntil(clients.openWindow('/'));
  }
});
```
