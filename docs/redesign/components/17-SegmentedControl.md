# Komponentenspezifikation: `SegmentedControl.svelte`
**Pfad:** `frontend/src/lib/components/ui/SegmentedControl.svelte`  
**Kategorie:** Atom / Umschalter  
**Zweck:** Schiebende Pillen-Auswahl für Zeiträume (`7T`, `30T`, `90T`, `1J`), Ansichten (`Front / Back`) und Modi mit elastischer CSS-Hintergrund-Animation.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  [  7D  |  30D (Aktiv)  |  90D  |   1Y   |   ALL  ]         │
└─────────────────────────────────────────────────────────────┘
```

- **Hintergrund:** `bg-surface-100 p-1 rounded-xl flex items-center`.
- **Aktive Pille:** Schwebendes weißes Rechteck (`bg-surface-0 shadow-sm rounded-lg`) mit weicher horizontaler Gleit-Animation (`transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1)`).

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Option<T = string> {
  value: T;
  label: string;
  icon?: string;
}

interface Props<T = string> {
  options: Option<T>[];
  value: T;
  size?: 'sm' | 'md';
  onchange: (newValue: T) => void;
}
```
