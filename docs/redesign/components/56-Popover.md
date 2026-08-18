# Komponentenspezifikation: `Popover.svelte`
**Pfad:** `frontend/src/lib/components/ui/Popover.svelte`  
**Kategorie:** Molekül / Schwebendes Kontext-Panel  
**Zweck:** Anker-positioniertes schwebendes Panel für Filter, Detail-Ansichten und Schnellformulare mit Click-Outside-Erkennung und Pfeil-Ausrichtung.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ [ Filter ▾ ]                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ZEITRAUM FILTERN:                                       │ │
│ │ • [ 7 Tage ]  • [ 30 Tage ]  • [ Quartal ]              │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ [ Filter anwenden ]                                     │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  open: boolean;
  position?: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end';
  onclose: () => void;
  trigger: Snippet;
  children: Snippet;
}
```
