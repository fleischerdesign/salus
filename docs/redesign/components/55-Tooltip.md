# Komponentenspezifikation: `Tooltip.svelte`
**Pfad:** `frontend/src/lib/components/ui/Tooltip.svelte`  
**Kategorie:** Atom / Schwebender Mikro-Hinweis  
**Zweck:** Glasmorphismus-Mikro-Tooltip für Icons, Abkürzungen und Buttons mit automatischer Kollisionserkennung an Bildschirmrändern und konfigurierbarem Delay.

---

## 1. Visuelle Spezifikation

```
         ┌───────────────────────────────┐
         │ 7-Tage Exponential Moving Avg │
         └───────────────▼───────────────┘
                 [ (•) 7T-EMA ]
```

- **Styling:** `bg-surface-900/90 text-white text-xs font-medium px-2.5 py-1.5 rounded-lg shadow-lg backdrop-blur-sm pointer-events-none z-50`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  text: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delayMs?: number; // Standard: 200ms
  children: Snippet;
}
```
