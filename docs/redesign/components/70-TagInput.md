# Komponentenspezifikation: `TagInput.svelte`
**Pfad:** `frontend/src/lib/components/ui/TagInput.svelte`  
**Kategorie:** Molekül / Multi-Tag & Chip-Eingabefeld  
**Zweck:** Eingabefeld für Tags (z.B. Mahlzeiten-Kategorien, Workout-Fokus oder Journal-Stimmungen) mit Autovervollständigung, Pillen-Entfernung per Backspace und Tastatur-Bestätigung per Enter oder Komma.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  Tags / Kategorien                                          │
│  [ Proteinreich × ]  [ Pre-Workout × ]  [ Tippe Tag...    ] │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  tags: string[];
  suggestions?: string[];
  placeholder?: string;
  maxTags?: number;
  onchange: (tags: string[]) => void;
}
```
