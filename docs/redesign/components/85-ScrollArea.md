# Komponentenspezifikation: `ScrollArea.svelte`
**Pfad:** `frontend/src/lib/components/ui/ScrollArea.svelte`  
**Kategorie:** Atom / Eleganter Scroll-Container  
**Zweck:** Maßgeschneiderter Scroll-Bereich mit ultra-subtilen Scrollbalken, sanften Fade-Out Schatten an oberen und unteren Rändern und physikalischem Trägheits-Scrollen auf Touch-Geräten.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ ░░░░░░░░░░░░ (Sanfter oberer Ausblend-Schatten) ░░░░░░░░░░░ │
│                                                             │
│   ( Scrollbarer Inhalt )                                █   │
│                                                         █   │
│ ░░░░░░░░░░░░ (Sanfter unterer Ausblend-Schatten) ░░░░░░░░░░ │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  maxHeight?: string; // z.B. "400px"
  showFadeMasks?: boolean;
  children: Snippet;
  class?: string;
}
```
