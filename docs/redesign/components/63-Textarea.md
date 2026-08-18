# Komponentenspezifikation: `Textarea.svelte`
**Pfad:** `frontend/src/lib/components/ui/Textarea.svelte`  
**Kategorie:** Atom / Mehrzeiliges Eingabefeld  
**Zweck:** Auto-resizing Textbereich für Journal-Einträge, Arzt-Notizen, Workout-Kommentare und Rezepte mit Zeichenzähler und optionaler Markdown-Vorschau.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  Notizen / Reflexion                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Heute lief das Training besonders gut. Keine Knieschmerzen│  │
│  │ bei Kniebeugen...                                     │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│  Zeichen: 84 / 500                              [ Auto-Grow]│
└─────────────────────────────────────────────────────────────┘
```

- **Auto-Grow:** Passt seine Höhe beim Tippen automatisch dem Inhalt an (`rows` wachsen ohne Scrollbalken).
- **Styling:** `border border-surface-200 bg-surface-0 rounded-xl p-3 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-500/20`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value: string;
  label?: string;
  placeholder?: string;
  minRows?: number; // Standard: 3
  maxRows?: number; // Standard: 10
  maxLength?: number;
  autoGrow?: boolean;
  disabled?: boolean;
  error?: string;
  onchange: (newVal: string) => void;
}
```
