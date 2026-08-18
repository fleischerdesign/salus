# Komponentenspezifikation: `Collapsible.svelte`
**Pfad:** `frontend/src/lib/components/ui/Collapsible.svelte`  
**Kategorie:** Atom / Flexibles Aufklapp-Primitiv  
**Zweck:** Low-Level Primitiv zum sanften Ein- und Ausblenden beliebiger Inhalte mit stufenloser CSS-Grid-Animation (`grid-template-rows: 0fr -> 1fr`) ohne harte JavaScript-Höhenberechnungen.

---

## 1. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  open: boolean;
  durationMs?: number; // Standard: 200ms
  children: Snippet;
  class?: string;
}
```
