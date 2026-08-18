# Komponentenspezifikation: `SelectDropdown.svelte`
**Pfad:** `frontend/src/lib/components/ui/SelectDropdown.svelte`  
**Kategorie:** Molekül / Durchsuchbare Auswahl-Dropdown  
**Zweck:** Barrierefreies, durchsuchbares Dropdown-Menü für Einheiten, Zeiträume, Übungen oder Kategorien mit Tastaturnavigation, Icons und Gruppen-Headern.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  Zeitzone / Referenzbereich                                 │
│  [ 🇩🇪 Europe/Berlin (UTC+2)                           ▾ ]  │
├─────────────────────────────────────────────────────────────┤
│  (Geöffnetes Dropdown):                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🔍 [ Suche nach Zeitzone oder Stadt... ]              │  │
│  │ ───────────────────────────────────────────────────── │  │
│  │  🇩🇪 Europe/Berlin (UTC+2)                        ✓    │  │
│  │  🇬🇧 Europe/London (UTC+1)                             │  │
│  │  🇺🇸 America/New_York (UTC-4)                          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface SelectOption<T = string> {
  value: T;
  label: string;
  sublabel?: string;
  icon?: string;
  group?: string;
  disabled?: boolean;
}

interface Props<T = string> {
  options: SelectOption<T>[];
  value: T;
  label?: string;
  placeholder?: string;
  searchable?: boolean;
  disabled?: boolean;
  error?: string;
  onchange: (newValue: T) => void;
}
```
