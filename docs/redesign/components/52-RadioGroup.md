# Komponentenspezifikation: `RadioGroup.svelte`
**Pfad:** `frontend/src/lib/components/ui/RadioGroup.svelte`  
**Kategorie:** Molekül / Radio-Kacheln & Auswahlliste  
**Zweck:** Elegante Radio-Buttons und visuelle Auswahl-Kacheln für exklusive Optionen (z. B. Fastenprotokolle: 16:8 vs. 18:6 vs. OMAD) mit leuchtendem Rahmen und weichem Hintergrund.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  WÄHLE DEIN FASTEN-PROTOKOLL:                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ (•) 16:8 Leangains (Standard)            [ Empfohlen ]│  │
│  │     16 Stunden Fasten • 8 Stunden Essensfenster       │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ( ) 18:6 Intensiv                                     │  │
│  │     18 Stunden Fasten • Erhöhte Ketose-Aktivierung    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

- **Aktiv-Kachel:** `border-2 border-primary-500 bg-primary-50/40 shadow-sm`.
- **Inaktiv-Kachel:** `border border-surface-200 bg-surface-0 hover:border-surface-300`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface RadioOption<T = string> {
  value: T;
  label: string;
  description?: string;
  badge?: string;
  icon?: string;
  disabled?: boolean;
}

interface Props<T = string> {
  options: RadioOption<T>[];
  value: T;
  name: string;
  variant?: 'inline' | 'cards' | 'list';
  onchange: (newValue: T) => void;
}
```
