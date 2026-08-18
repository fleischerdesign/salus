# Komponentenspezifikation: `Checkbox.svelte`
**Pfad:** `frontend/src/lib/components/ui/Checkbox.svelte`  
**Kategorie:** Atom / Taktile Checkbox  
**Zweck:** Ästhetische, barrierefreie Checkbox mit animiertem SVG-Häkchen, Indeterminate-Status (Teilauswahl bei Listen) und haptischem Feedback.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  [ ✓ ] Blutdruck & Puls in den Export einbeziehen           │
│  [ - ] Lipidprofil (3 von 6 Markern ausgewählt)             │
│  [   ] Medikamentenplan ausschließen                        │
└─────────────────────────────────────────────────────────────┘
```

- **Unchecked:** `h-5 w-5 rounded-md border-2 border-surface-300 bg-surface-0 hover:border-primary-400 transition-colors`.
- **Checked:** `h-5 w-5 rounded-md bg-primary-500 text-white border-primary-500 shadow-sm flex items-center justify-center`.
- **SVG Check-Draw:** Das weiße Häkchen zeichnet sich flüssig von links unten nach rechts oben (`stroke-dashoffset: 0`).

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  checked: boolean;
  indeterminate?: boolean; // Teilauswahl-Strich
  label?: string;
  sublabel?: string;
  disabled?: boolean;
  onchange: (checked: boolean) => void;
}
```
