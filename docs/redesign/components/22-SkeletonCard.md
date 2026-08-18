# Komponentenspezifikation: `SkeletonCard.svelte`
**Pfad:** `frontend/src/lib/components/ui/SkeletonCard.svelte`  
**Kategorie:** Molekül / Ladeplatzhalter (Zero CLS)  
**Zweck:** Subtiler, fließender Shimmer-Ladeplatzhalter mit exakt denselben Abmessungen wie die Ziel-Kacheln, um Cumulative Layout Shift (CLS = 0) zu garantieren.

---

## 1. Visuelle Spezifikation

- **Animation:** `animate-shimmer` mit einem linearen Gradienten von `surface-100` über `surface-200` zurück zu `surface-100`.
- **Form:** Abgerundete Rechtecke (`rounded-xl` / `rounded-2xl`) für Titel, Zahlen und Diagramm-Blöcke.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  variant?: 'metric' | 'chart' | 'table_row' | 'hero_ring' | 'list_item';
  height?: string; // z.B. "160px"
  class?: string;
}
```
