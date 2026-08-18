# Komponentenspezifikation: `ContextMenu.svelte`
**Pfad:** `frontend/src/lib/components/ui/ContextMenu.svelte`  
**Kategorie:** Molekül / Desktop Rechtsklick-Kontextmenü  
**Zweck:** Schnelles Rechtsklick-Aktionsmenü auf Desktop-Computern für sofortige Kachel-Manipulation (Größe ändern, Kachel duplizieren, Messwert editieren, Löschen) mit Bildschirmrand-Kollisionserkennung.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ (Rechtsklick auf Kachel):                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📏 Größe: [ S ] [ M (Aktiv) ] [ L ]                     │ │
│ │ ✏️ Kachel konfigurieren                                 │ │
│ │ 📋 Datenpunkt kopieren                                  │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ 🗑️ Vom Dashboard entfernen (Rot)                       │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface ContextMenuItem {
  id: string;
  label: string;
  icon?: string;
  shortcut?: string;
  danger?: boolean;
  onclick: () => void;
}

interface Props {
  items: ContextMenuItem[];
  children: Snippet;
}
```
