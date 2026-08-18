# Komponentenspezifikation: `ColorPicker.svelte`
**Pfad:** `frontend/src/lib/components/ui/ColorPicker.svelte`  
**Kategorie:** Atom / Farbfeld- & Swatch-Wähler  
**Zweck:** Auswahl von Akzentfarben für benutzerdefinierte Metrik-Präferenzen, Habits und Kachel-Hervorhebungen mit harmonisch aufeinander abgestimmten OKLCH-Farbfeldern.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  AKZENTFARBE WÄHLEN:                                        │
│  [ ● Violett ] [ ● Türkis ] [ ● Koralle ] [ ● Bernstein ]    │
│  [ ● Smaragd ] [ ● Ozean ]  [ ● Rubin ]   [ ● Indigo ]       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value: string; // Hex oder OKLCH
  presets?: string[];
  onchange: (newColor: string) => void;
}
```
