# Komponentenspezifikation: `ProgressBar.svelte`
**Pfad:** `frontend/src/lib/components/ui/ProgressBar.svelte`  
**Kategorie:** Atom / Linearer Fortschrittsbalken  
**Zweck:** Universelle Fortschrittsleiste für Meilensteine, Tagesziele, Ladefortschritte und Speicher-Auslastung mit animierten Streifen (`indeterminate`) oder exakten Prozenten.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  75% abgeschlossen                                          │
│  [████████████████████████████████░░░░░░░░░░]               │
└─────────────────────────────────────────────────────────────┘
```

- **Höhe:** `h-1.5` (subtil), `h-2.5` (Standard), `h-4` (groß mit Label im Balken).
- **Styling:** `bg-surface-200 rounded-full overflow-hidden`.
- **Füllung:** `bg-primary-500 rounded-full transition-all duration-300 ease-out`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value?: number; // 0 bis 100
  max?: number;
  indeterminate?: boolean; // Animierter Ladebalken
  color?: string; // z.B. var(--color-vital)
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}
```
