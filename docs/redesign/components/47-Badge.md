# Komponentenspezifikation: `Badge.svelte`
**Pfad:** `frontend/src/lib/components/ui/Badge.svelte`  
**Kategorie:** Atom / Status- & Kategorie-Pille  
**Zweck:** Hochpräzises, typografisch fein abgestimmtes Status- und Kennzeichnungs-Element mit optionalem pulsierendem Live-Punkt, Icon und semantischen Farbvarianten.

---

## 1. Visuelle Varianten

```
┌──────────────┬────────────────────────────────────────────────────────────────────────┐
│ Variante     │ Visueller Stil & Verwendungszweck                                      │
├──────────────┼────────────────────────────────────────────────────────────────────────┤
│ `neutral`    │ `bg-surface-100 text-surface-700 border border-surface-200/80`         │
│ `primary`    │ `bg-primary-50 text-primary-700 border border-primary-200/60`          │
│ `success`    │ `bg-emerald-50 text-emerald-700 border border-emerald-200/60` (Optimal)│
│ `warning`    │ `bg-amber-50 text-amber-700 border border-amber-200/60` (Grenzwertig)  │
│ `error`      │ `bg-rose-50 text-rose-700 border border-rose-200/60` (Kritisch)        │
│ `vital`      │ `bg-vital-50 text-vital-700 border border-vital-200/60` (Kardiologie)  │
│ `activity`   │ `bg-activity-50 text-activity-700 border border-activity-200/60`       │
│ `outline`    │ `bg-transparent text-surface-600 border border-surface-300`            │
└──────────────┴────────────────────────────────────────────────────────────────────────┘
```

- **Größen:**
  - `sm`: `h-5 px-1.5 text-[11px] font-semibold tracking-wide uppercase rounded-md`
  - `md`: `h-6 px-2.5 text-xs font-semibold rounded-lg` (Standard)
  - `lg`: `h-7 px-3 text-sm font-semibold rounded-lg`

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  variant?: 'neutral' | 'primary' | 'success' | 'warning' | 'error' | 'vital' | 'activity' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean; // Zeigt pulsierenden Live-Punkt
  dotColor?: string;
  icon?: string; // Material Symbols Icon
  removable?: boolean; // Zeigt (x)-Button zum Entfernen
  onremove?: () => void;
  children: Snippet;
  class?: string;
}
```
