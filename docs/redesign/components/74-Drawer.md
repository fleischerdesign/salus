# Komponentenspezifikation: `Drawer.svelte`
**Pfad:** `frontend/src/lib/components/ui/Drawer.svelte`  
**Kategorie:** Organismus / Universeller Slide-Over Drawer  
**Zweck:** Universelles, in alle 4 Richtungen ausfahrbares Seiten-Panel (Rechts für Kataloge & Einstellungen, Unten für Mobile Sheets, Links für Menüs) mit Gesten-Wisch-Schließen.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  [×] DRAWER-TITEL                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ( Scrollbarer Inhalt des Drawers )                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  [ Abbrechen ]                              [ Übernehmen ]  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  open: boolean;
  side?: 'left' | 'right' | 'bottom' | 'top';
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'full';
  onclose: () => void;
  header?: Snippet;
  footer?: Snippet;
  children: Snippet;
}
```
