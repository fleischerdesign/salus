# Komponentenspezifikation: `DatePicker.svelte`
**Pfad:** `frontend/src/lib/components/ui/DatePicker.svelte`  
**Kategorie:** Molekül / Kalender- & Datums-Wähler  
**Zweck:** Barrierefreier Kalender-Dialog für Einzeldaten und Zeiträume (z.B. für Laborberichte oder Trendanalysen) mit Schnell-Presets (*„Heute“*, *„Gestern“*, *„Letzte 7 Tage“*, *„Letzter Monat“*).

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  [ ◀ ]              AUGUST 2026                      [ ▶ ]  │
├─────────────────────────────────────────────────────────────┤
│  Mo    Di    Mi    Do    Fr    Sa    So                     │
│  27    28    29    30    31     1     2                     │
│   3     4     5     6     7     8     9                     │
│  10    11    12    13   [14]   15    16  (Heute: [14. Aug]) │
│  17    18    19    20    21    22    23                     │
│  24    25    26    27    28    29    30                     │
├─────────────────────────────────────────────────────────────┤
│ Schnellwahl: [ Heute ]  [ Gestern ]  [ Letzte 7T ]  [ 30T ] │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value: string; // "YYYY-MM-DD"
  rangeEnd?: string; // Optional für Date-Ranges
  mode?: 'single' | 'range';
  minDate?: string;
  maxDate?: string;
  onchange: (date: string, rangeEnd?: string) => void;
}
```
