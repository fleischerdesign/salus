# Komponentenspezifikation: `Btn.svelte`
**Pfad:** `frontend/src/lib/components/ui/Btn.svelte`  
**Kategorie:** Atom / Primäres Interaktionselement  
**Zweck:** Universeller, haptischer Button mit konsistenten Zuständen (Idle, Hover, Active/Spring-Scale, Disabled, Loading mit Spinner).

---

## 1. Visuelle Varianten & Größen

```
┌──────────────┬────────────────────────────────────────────────────────────────────────┐
│ Variante     │ Visueller Stil & Verwendungszweck                                      │
├──────────────┼────────────────────────────────────────────────────────────────────────┤
│ `primary`    │ `bg-primary-500 hover:bg-primary-600 text-white shadow-sm`             │
│ `secondary`  │ `border border-surface-300 bg-surface-0 hover:bg-surface-50 text-main` │
│ `ghost`      │ `bg-transparent hover:bg-surface-100 text-surface-700`                │
│ `danger`     │ `bg-error-50 hover:bg-error-100 text-error-700`                        │
│ `vital`      │ `bg-vital-500 hover:bg-vital-600 text-white shadow-sm`                 │
│ `pill`       │ Abgerundet mit `rounded-full`, ideal für Chips & Quick-Actions         │
└──────────────┴────────────────────────────────────────────────────────────────────────┘
```

### Größen:
- `sm`: `h-8 px-3 text-xs gap-1.5 rounded-lg`
- `md`: `h-10 px-4 text-sm gap-2 rounded-xl` (Standard)
- `lg`: `h-12 px-6 text-base gap-2.5 rounded-xl`
- `icon`: Quadratischer Icon-Button (`h-9 w-9` bzw. `h-11 w-11`).

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'vital' | 'pill';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  href?: string;
  icon?: string;
  iconTrailing?: string;
  onclick?: (e: MouseEvent) => void;
  children?: Snippet;
  class?: string;
}
```

---

## 3. Mikro-Interaktionen
- **Klick-Physik:** `active:scale-[0.97] transition-transform duration-100`.
- **Fokus-Ring:** `focus-visible:outline-2 focus-visible:outline-primary-500 focus-visible:outline-offset-2`.
