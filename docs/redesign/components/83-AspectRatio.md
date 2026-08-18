# Komponentenspezifikation: `AspectRatio.svelte`
**Pfad:** `frontend/src/lib/components/ui/AspectRatio.svelte`  
**Kategorie:** Atom / Geometrischer Seitenverhältnis-Container  
**Zweck:** Erzwingt ein exaktes mathematisches Seitenverhältnis (16:9 für Video/Kamera, 1:1 für Ziffernblöcke/Avatare, 4:3 für Muskelmodelle) unabhängig von der Viewport-Breite.

---

## 1. Visuelle Spezifikation

```typescript
interface Props {
  ratio?: number; // z.B. 16/9, 4/3, 1 (Standard: 1)
  children: Snippet;
  class?: string;
}
```

- **CSS-Standard:** Nutzt natives `aspect-ratio: ratio` mit automatischem Fallback.
