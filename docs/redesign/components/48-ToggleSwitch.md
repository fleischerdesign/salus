# Komponentenspezifikation: `ToggleSwitch.svelte`
**Pfad:** `frontend/src/lib/components/ui/ToggleSwitch.svelte`  
**Kategorie:** Atom / Taktiler Schalter  
**Zweck:** Ästhetischer Schalter (iOS/macOS-Stil) für binäre Optionen (z. B. *„7-Tage-EMA anzeigen“*, *„Koffein-Warnungen aktiv“*) mit elastischem Daumen-Gleiten und Haptik.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  [ (•)   ] 7-Tage-EMA Glättungslinie einblenden             │
│  [   (•) ] Zirkadianer Koffein-Cutoff aktiviert (14:30 Uhr) │
└─────────────────────────────────────────────────────────────┘
```

- **Off:** `w-11 h-6 bg-surface-200 rounded-full p-0.5 transition-colors duration-200`. Daumen: `w-5 h-5 bg-white rounded-full shadow-sm translate-x-0`.
- **On:** `w-11 h-6 bg-primary-500 rounded-full p-0.5 transition-colors duration-200`. Daumen: `w-5 h-5 bg-white rounded-full shadow-sm translate-x-5`.
- **Daumen-Physik:** Beim Ziehen dehnt sich der Daumen leicht in Bewegungsrichtung (`scale-x-110`).

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  checked: boolean;
  label?: string;
  description?: string;
  disabled?: boolean;
  color?: string; // z.B. 'primary', 'vital', 'success'
  onchange: (checked: boolean) => void;
}
```
