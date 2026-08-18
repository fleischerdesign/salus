# Komponentenspezifikation: `TimePicker.svelte`
**Pfad:** `frontend/src/lib/components/ui/TimePicker.svelte`  
**Kategorie:** Molekül / Präzisions-Uhrzeit-Wähler  
**Zweck:** 24h-Uhrzeitwähler für zirkadiane Aufwach-/Schlafenszeiten, Medikamenten-Einnahmezeiten und Mahlzeiten-Zeitstempel mit Ziffern-Rollern oder Direkt-Eingabe.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  UHRZEIT WÄHLEN:                                            │
│                                                             │
│       [ 08 ]  :  [ 30 ]  Uhr         [ Vormittags ]         │
│         ▲          ▲                                        │
│       Stunden   Minuten                                     │
│                                                             │
│  Schnellwahl: [ Jetzt: 14:15 ]  [ 08:00 ]  [ 12:30 ]  [ 20:00 ]│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value: string; // "HH:MM" (z.B. "08:30")
  stepMinutes?: number; // Standard: 5
  onchange: (timeStr: string) => void;
}
```
