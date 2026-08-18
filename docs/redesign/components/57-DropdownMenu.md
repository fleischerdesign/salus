# Komponentenspezifikation: `DropdownMenu.svelte`
**Pfad:** `frontend/src/lib/components/ui/DropdownMenu.svelte`  
**Kategorie:** Molekül / Kontext-Aktionsmenü  
**Zweck:** Menü für Kachel-Aktionen (Größe ändern, Ausblenden, Editieren, Löschen) mit Trennlinien, Icons, Tastaturnavigation und Danger-Highlights.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ [ ⋮ Drei-Punkte-Menü ]                                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ✏️ Kachel bearbeiten                                    │ │
│ │ 📏 Größe ändern: [ S ] [ M ] [ L ]                      │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ 🗑️ Kachel entfernen (Rot)                              │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface MenuItem {
  id: string;
  label: string;
  icon?: string;
  shortcut?: string;
  danger?: boolean;
  disabled?: boolean;
  onclick: () => void;
}

interface Props {
  items: MenuItem[];
  trigger: Snippet;
}
```
