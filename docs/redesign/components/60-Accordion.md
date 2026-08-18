# Komponentenspezifikation: `Accordion.svelte`
**Pfad:** `frontend/src/lib/components/ui/Accordion.svelte`  
**Kategorie:** Molekül / Aufklappbares Akkordeon  
**Zweck:** Sanft aufklappbare Bereiche (z. B. für FAQ, komplexe Labormarker oder Rezept-Zutaten) mit rotierendem SVG-Chevron und ruckelfreier CSS-Höhenanimation (`grid-template-rows: 0fr -> 1fr`).

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🧬 LIPIDPROFIL (6 Marker)                              [ ▾ ]│
├─────────────────────────────────────────────────────────────┤
│ (Aufgeklappter Inhalt):                                     │
│ • LDL-Cholesterin: 68 mg/dL                                 │
│ • HDL-Cholesterin: 62 mg/dL                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  title: string;
  subtitle?: string;
  icon?: string;
  open?: boolean;
  onToggle?: (open: boolean) => void;
  children: Snippet;
}
```
