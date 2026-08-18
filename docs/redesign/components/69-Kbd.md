# Komponentenspezifikation: `Kbd.svelte`
**Pfad:** `frontend/src/lib/components/ui/Kbd.svelte`  
**Kategorie:** Atom / Tastatur-Tastenkappe  
**Zweck:** Ästhetisches Tastenkappen-Element (`[ ⌘K ]`, `[ Esc ]`, `[ L ]`) zur Darstellung von Tastatur-Shortcuts mit subtiler 3D-Prägung und klarem Kontrast.

---

## 1. Visuelle Spezifikation

```
[ ⌘K ]   [ Esc ]   [ L ]   [ ↵ Enter ]
```

- **Styling:** `inline-flex items-center justify-center font-mono font-semibold text-[11px] text-surface-600 bg-surface-100 border border-surface-300 border-b-2 rounded px-1.5 py-0.5 shadow-sm select-none`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  shortcut: string; // z.B. "⌘K", "Esc", "L", "↵"
  class?: string;
}
```
