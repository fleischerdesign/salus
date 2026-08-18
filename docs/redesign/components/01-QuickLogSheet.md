# Komponentenspezifikation: `QuickLogSheet.svelte`
**Pfad:** `frontend/src/lib/components/ui/QuickLogSheet.svelte`  
**Kategorie:** Organismus / Globaler Interaktions-Hub  
**Zweck:** Lückenlose, hürdenfreie Schnellerfassung aller täglichen Gesundheitsdaten (Wasser, Stimmung, Habits, Vitalwerte, Mahlzeiten) unter 2 Sekunden von jedem Screen aus.

---

## 1. Visuelle & Ergonomische Spezifikation

### 1.1 Responsive Verhaltensweisen
- **Mobile (PWA, < 1024px):**
  - Öffnet sich als **wischbares Bottom Sheet** von unten (`translate-y-full` → `translate-y-0`).
  - Unterstützt **Drag-to-Dismiss** (Herunterwischen schließt das Sheet flüssig).
  - Maximale Höhe: `85vh` mit internem Scrollbereich.
  - Safe-Area-Padding unten für iOS Home-Bar.
- **Desktop (≥ 1024px):**
  - Öffnet sich als **zentrierter Fokus-Dialog** mit sanftem Backdrop-Blur (`backdrop-blur-md bg-surface-900/40`).
  - Breite: `560px` fix, zentriert.
  - Schließt bei Klick auf den Backdrop oder Druck auf `Escape`.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  SCHNELLERFASSUNG                                                                    [×]│
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

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  open: boolean;
  onclose: () => void;
  defaultCategory?: 'water' | 'mood' | 'weight' | 'bp' | 'meal' | 'habit';
}
```

---

## 3. Interaktions-Logik & Datenfluss

### 3.1 1-Tap Wasser-Logging
```typescript
async function logWater(amountMl: number) {
  // Optimistisches Dexie-Schreiben über mutate()
  await mutate({
    kind: 'crud',
    action: 'create',
    entity: 'measurement',
    data: {
      metric_code: 'water',
      value_numeric: amountMl,
      unit: 'ml',
      start_time: new Date().toISOString()
    }
  });

  // Haptisches Feedback (auf unterstützten Mobilgeräten)
  if (navigator.vibrate) navigator.vibrate(20);

  // Kurze Erfolgs-Pille anzeigen & Sheet nach kurzer Pause schließen
  triggerSuccessFeedback(`+${amountMl} ml erfasst!`);
}
```

### 3.2 1-Tap Stimmungs-Logging
```typescript
async function logMood(score: number) {
  await mutate({
    kind: 'crud',
    action: 'create',
    entity: 'mood_entry',
    data: {
      mood_score: score,
      entry_date: todayString(),
      created_at: new Date().toISOString()
    }
  });
  if (navigator.vibrate) navigator.vibrate(25);
  onclose();
}
```

### 3.3 Vitalwerte (Gewicht & Blutdruck mit Ziffernblock)
- Inputs nutzen `inputmode="decimal"` und `pattern="[0-9]*"`, um auf Smartphones sofort die großen Zifferntasten einzublenden.
- Automatischer Fokus auf das Eingabefeld beim Öffnen des jeweiligen Tabs.

---

## 4. Barrierefreiheit & Tastatur-Steuerung

1. **Globaler Shortcut:** Taste `L` (außerhalb von Eingabefeldern) öffnet das Sheet.
2. **Focus Trap:** Der Tab-Fokus bleibt innerhalb des Sheets gefangen, solange es geöffnet ist.
3. **Schließen:** `Escape`-Taste schließt das Sheet und stellt den Fokus auf den auslösenden Button zurück.
4. **ARIA:** `role="dialog"`, `aria-modal="true"`, `aria-label="Schnellerfassung"`.
