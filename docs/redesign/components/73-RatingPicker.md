# Komponentenspezifikation: `RatingPicker.svelte`
**Pfad:** `frontend/src/lib/components/ui/RatingPicker.svelte`  
**Kategorie:** Atom / Taktiler Bewertungs-Wähler  
**Zweck:** 1–5 Sterne-, Batterie- oder Smiley-Bewertungswähler für subjektive Schlafqualität, Muskelkater-Stärke, Energielevel und Erholungsgefühl.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  Schlafqualität:  [ ⭐ ][ ⭐ ][ ⭐ ][ ⭐ ][ ✰ ]  (4 / 5)    │
│  Subjektive Erholung: "Gut erholt & bereit für Training"    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value: number; // 1 bis max
  max?: number; // Standard: 5
  icon?: 'star' | 'battery' | 'heart' | 'flame';
  labels?: string[]; // ["Schlecht", "Mäßig", "Okay", "Gut", "Exzellent"]
  readonly?: boolean;
  onchange?: (val: number) => void;
}
```
