# Komponentenspezifikation: `SearchInput.svelte`
**Pfad:** `frontend/src/lib/components/ui/SearchInput.svelte`  
**Kategorie:** Atom / Spezialisiertes Suchfeld  
**Zweck:** Dediziertes Suchfeld mit integriertem Lupen-Icon, Sofort-Debounce (200ms), Lade-Spinner bei asynchroner Suche, `[ × ]` Clear-Button und Tastatur-Shortcut-Badge (`[ / ]` oder `[ ⌘K ]`).

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 [ Lebensmittel, Übungen oder Labore suchen...  ] [ / ] [×]│
└─────────────────────────────────────────────────────────────┘
```

- **Styling:** `h-10 pl-10 pr-10 bg-surface-100 hover:bg-surface-200/70 focus:bg-surface-0 border border-transparent focus:border-primary-500 rounded-xl w-full text-sm`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value: string;
  placeholder?: string;
  debounceMs?: number; // Standard: 200ms
  loading?: boolean;
  shortcutHint?: string; // z.B. "/" oder "⌘K"
  onsearch: (query: string) => void;
  onclear?: () => void;
}
```
