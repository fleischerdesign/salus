# Komponentenspezifikation: `Input.svelte`
**Pfad:** `frontend/src/lib/components/ui/Input.svelte`  
**Kategorie:** Atom / Eingabefeld  
**Zweck:** Hochwertiges Texteingabe- und Ziffernfeld mit Floating Label, numerischem Tastatur-Modus (`inputmode`), Validierungs-Shake und Clear-Button.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  Körpergewicht (kg)                                         │
│  [ 82.4                                         ] [ × Clear]│
│  Letzte Messung: 82.6 kg gestern                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value: string | number;
  label?: string;
  placeholder?: string;
  type?: 'text' | 'number' | 'email' | 'password' | 'date' | 'time';
  inputmode?: 'text' | 'decimal' | 'numeric' | 'tel' | 'search';
  unit?: string; // z.B. "kg", "mmHg", "ml"
  error?: string;
  hint?: string;
  disabled?: boolean;
  autofocus?: boolean;
  onchange?: (val: string) => void;
  onenter?: () => void;
}
```

---

## 3. Besonderheiten für Health-Eingaben
1. **`inputmode="decimal"`:** Öffnet auf iPhones und Android-Geräten sofort den großen Ziffernblock statt der Buchstabentastatur.
2. **Tabellenziffern:** `font-variant-numeric: tabular-nums` für zitterfreie Zahlendarstellung.
3. **Fehler-Animation:** Bei fehlerhafter Eingabe (z. B. unplausibler Wert) rüttelt das Feld kurz horizontal (`animate-shake`).
