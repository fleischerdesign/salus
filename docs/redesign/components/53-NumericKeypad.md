# Komponentenspezifikation: `NumericKeypad.svelte`
**Pfad:** `frontend/src/lib/components/ui/NumericKeypad.svelte`  
**Kategorie:** Organismus / Taktiler Health-Ziffernblock  
**Zweck:** Großer, extrem reaktionsschneller Ziffernblock für das Smartphone beim Training oder Schnell-Logging (Gewicht, Wiederholungen, Blutdruck, Blutzucker) ohne lästiges Aufploppen und Verdecken durch die native Tastatur.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  GEWICHT: [  82.5  ] kg                      [ ⌫ Löschen ]  │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐ │
│  │     1     │  │     2     │  │     3     │  │   +1.25   │ │
│  ├───────────┤  ├───────────┤  ├───────────┤  ├───────────┤ │
│  │     4     │  │     5     │  │     6     │  │   +2.50   │ │
│  ├───────────┤  ├───────────┤  ├───────────┤  ├───────────┤ │
│  │     7     │  │     8     │  │     9     │  │   +5.00   │ │
│  ├───────────┤  ├───────────┤  ├───────────┤  ├───────────┤ │
│  │     .     │  │     0     │  │     00    │  │   [ OK ]  │ │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────┘
```

- **Tasten:** `h-14 bg-surface-100 hover:bg-surface-200 active:scale-95 text-xl font-bold rounded-xl flex items-center justify-center transition-transform`.
- **Hantelscheiben-Quick-Adds:** Direkte `+1.25`, `+2.5`, `+5.0` kg Schnell-Tasten für Kraftsportler.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value: string;
  unit?: string;
  allowDecimals?: boolean;
  quickAddIncrements?: number[]; // z.B. [1.25, 2.5, 5]
  onchange: (newValue: string) => void;
  onsubmit: (finalValue: string) => void;
}
```
