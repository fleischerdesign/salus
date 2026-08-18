# Salus 2.0 — Der Universal Quick-Log Hub (Zero-Friction Capture)
**Dokument:** `03-quick-log-system.md`  
**Status:** Verbindlich

---

## 1. Philosophie: Erfassung unter 2 Sekunden

Ein Gesundheitstracker verliert seinen Nutzen, wenn die Datenerfassung im Alltag zu viel kognitive Last oder zu viele Klicks erfordert. 

Der **Quick-Log Hub** ist von überall in der App mit **einem einzigen Klick** (Desktop: `+ Loggen` oder Taste `L`; Mobile: Center-FAB in der Bottom Bar) erreichbar und öffnet sich als reaktives **Bottom Sheet (Mobile)** bzw. **zentriertes Fokus-Modal (Desktop)**.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  SCHNELLERFASSUNG (Quick Log)                                                        [×]│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  1-TAP SCHNELLAKTIONEN:                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────────────────┐ │
│  │ 💧 WASSER            │  │ 😊 STIMMUNG          │  │ 🔥 HABIT ABHAKEN               │ │
│  │ [+250ml] [+500ml]    │  │ [ 1 ][ 2 ][ 3 ][ 4 ] │  │ [✓] 3L Wasser getrunken        │ │
│  │ (+ Benutzerdefiniert)│  │ [ 5 - Fantastisch! ] │  │ [ ] 10.000 Schritte           │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  SCHNELLFORMULARE:                                                                      │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────────────────┐ │
│  │ ⚖️ KÖRPERGEWICHT     │  │ ❤️ BLUTDRUCK / PULS  │  │ 🥗 MAHLZEIT ERFASSEN           │ │
│  │ [ 82.4 ] kg          │  │ [ 120 ] / [ 80 ] mmHg│  │ [ 🔍 Zutat/Barcode tippen... ] │ │
│  │ [ Speichern ]        │  │ Puls: [ 64 ] bpm     │  │ [ + Aus Favoriten / Vorlagen ] │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  WEITERE DISZIPLINEN:                                                                   │
│  [ 🏃 Workout starten ]   [ ⏳ Fasten starten ]   [ 💊 Medikament loggen ]   [ ✍️ Notiz ]│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Die 1-Tap Schnellaktionen

### 2.1 Hydration (Wasser-Logging)
- Buttons: `+250ml` (Glas) und `+500ml` (Flasche).
- **Verhalten:** 
  - Ein Klick speichert sofort eine `Measurement`-Zeile für Wasser in Dexie.
  - Das Wasserglas im Hintergrund bzw. im Widget füllt sich sichtbar mit einer animierten Welle.
  - Haptisches Feedback auf Mobilgeräten.
  - Mehrfach-Klicks möglich (`+250` + `+250` = `+500ml`), Sheet schließt sanft nach 800ms Inaktivität.

### 2.2 Stimmung & Befinden (Mood Pick)
- 5 farblich abgestufte Stimmungs-Pills (von 1 = Sehr schlecht bis 5 = Exzellent).
- Ein Klick loggt den Wert sofort mit aktuellem Zeitstempel und schließt den Dialog.

### 2.3 Habit-Sofortabhaken
- Zeigt die 3 wichtigsten noch offenen Gewohnheiten des heutigen Tages an.
- Ein Klick auf den Check-Kreis löst den SVG-Lichtburst aus und markiert den `HabitLog` als erledigt.

---

## 3. Die Schnellformulare

### 3.1 Körpergewicht & Vitalwerte
- Große Ziffernfelder, die auf Mobilgeräten direkt den **numerischen Ziffernblock** öffnen (`inputmode="decimal"`).
- Vorbelegt mit dem zuletzt gemessenen Wert als Orientierung.
- Speichern via Enter-Taste oder `Speichern`-Button.

### 3.2 Mahlzeiten-Schnellsuche
- Inline-Suchfeld mit Sofort-Autovervollständigung aus der lokalen `food_item`-Tabelle.
- Barcode-Scan-Button zur direkten Kamera-Aktivierung.
- Auswahl der Portionsgröße und 1-Klick-Zuweisung zur aktuellen Mahlzeit (Frühstück, Mittag, Abend, Snack).

---

## 4. Technische Abwicklung & Outbox-Integration

Jede Aktion im Quick-Log Hub nutzt das universelle Schreib-Gateway:
```typescript
import { mutate } from '$lib/mutate';

// Beispiel: 1-Tap Wasser loggen
await mutate({
  kind: 'crud',
  action: 'create',
  entity: 'measurement',
  data: {
    metric_code: 'water',
    value_numeric: 250,
    unit: 'ml',
    start_time: new Date().toISOString()
  }
});
```
- **Latenz:** 0 Millisekunden wahrnehmbare Verzögerung (Optimistic Local Write).
- **Sicherheit:** Automatische Einreihung in die Dexie FIFO-Outbox und asynchroner Push an den Server.
