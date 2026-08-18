# Komponentenspezifikation: `WidgetGalleryCard.svelte`
**Pfad:** `frontend/src/lib/components/dashboard/WidgetGalleryCard.svelte`  
**Kategorie:** Molekül / Katalog-Vorschaukarte  
**Zweck:** Miniaturisierte, lebendig animierte Live-Vorschaukarte eines Widgets im Add-Widget Drawer, damit der Nutzer vor dem Hinzufügen exakt sieht, wie das Widget mit seinen echten Daten aussehen wird.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 💧 WASSER-TRACKER (Hydration)                   [ + Hinzufügen ]│
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ [Live-Miniatur des animierten Wasserglases]         │   │
│   │ 2.250 / 3.000 ml • 75%                              │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   Verfügbare Größen: [ S ] 1/3   [ M ] 1/2   [ L ] Voll     │
│   "Visualisiert den Flüssigkeitshaushalt mit 1-Tap Buttons" │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  id: string; // z.B. "water_logger", "steps", "fasting_timer"
  title: string;
  category: string; // z.B. "Vitalwerte", "Fitness", "Ernährung"
  description: string;
  icon: string;
  color: string;
  defaultSize?: 'small' | 'medium' | 'large';
  supportedSizes?: Array<'small' | 'medium' | 'large'>;
  onAdd: (size: 'small' | 'medium' | 'large') => void;
}
```
