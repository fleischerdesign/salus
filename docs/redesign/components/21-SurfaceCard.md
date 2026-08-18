# Komponentenspezifikation: `SurfaceCard.svelte`
**Pfad:** `frontend/src/lib/components/ui/SurfaceCard.svelte`  
**Kategorie:** Molekül / Universeller Kachel- & Panel-Container  
**Zweck:** Basiskarte für alle Widgets, Übersichten und Panels mit einheitlichen OKLCH-Elevationen, Radien, interaktivem Hover-Lift und optionalem Drag-Griff.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ [Icon] KACHEL-TITEL                     [ Extra / Aktion ]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ( Card Body / Kachelinhalt )                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ( Optionaler Footer / Metadaten / Zeitstempel )             │
└─────────────────────────────────────────────────────────────┘
```

- **Hintergrund:** `bg-surface-0 border border-surface-200/70 shadow-card rounded-2xl p-4 md:p-6`.
- **Hover-State (wenn `interactive={true}`):**  
  `hover:border-surface-300 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  title?: string;
  subtitle?: string;
  icon?: string;
  color?: string; // Akzentfarbe für Icon/Titel
  elevation?: 0 | 1 | 2; // Surface 0, 1 oder 2
  interactive?: boolean;
  editMode?: boolean; // Zeigt Drag-Handle
  padding?: 'none' | 'sm' | 'md' | 'lg';
  headerAction?: Snippet;
  footer?: Snippet;
  children: Snippet;
  onclick?: () => void;
  class?: string;
}
```
