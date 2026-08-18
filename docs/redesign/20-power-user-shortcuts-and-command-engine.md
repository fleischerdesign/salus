# Salus 2.0 — Power-User Shortcuts & Command Engine
**Dokument:** `20-power-user-shortcuts-and-command-engine.md`  
**Status:** Verbindlich  
**Zweck:** Vollständige Tastatur-Steuerung für Desktop-Power-User (`Cmd+K` Spotlight-Registry, Einzel-Tasten-Shortcuts, Listen-Navigation).

---

## 1. Einzel-Tasten-Shortcuts (Vim / Desktop-Navigation)

Wenn kein Texteingabefeld fokussiert ist, reagiert Salus auf universelle Einzel-Tasten:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ TASTE         │ AKTION                                                                  │
├───────────────┼─────────────────────────────────────────────────────────────────────────┤
│ `L`           │ Öffnet das Quick-Log Bottom Sheet (`QuickLogSheet.svelte`)              │
│ `W`           │ Startet direkt das nächste geplante Workout                             │
│ `/`           │ Fokussiert die globale Suche / Filterleiste                             │
│ `J` / `K`     │ Nächstes / Vorheriges Element in Tabellen & Listen auswählen            │
│ `X`           │ Aktuell ausgewähltes Element abhaken (Habit, Medikament, Workout-Satz)  │
│ `E`           │ Dashboard in den Kachel-Edit-Modus versetzen                            │
│ `?`           │ Shortcut-Hilfedialog einblenden (`Modal.svelte`)                        │
│ `Escape`      │ Schließt alle offenen Dialoge, Drawers und Tooltips                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Die `Cmd+K` Command-Registry

```typescript
export const COMMAND_REGISTRY = [
  // Schnell-Einträge
  { id: 'log-water', title: 'Wasser eintragen (+250ml)', category: 'Quick Log', icon: 'water_drop', shortcut: 'L W' },
  { id: 'log-bp', title: 'Blutdruck & Puls messen', category: 'Quick Log', icon: 'favorite', shortcut: 'L B' },
  { id: 'log-weight', title: 'Körpergewicht wiegen', category: 'Quick Log', icon: 'scale', shortcut: 'L G' },

  // Navigation
  { id: 'nav-dashboard', title: 'Zum Dashboard (Cockpit)', category: 'Navigation', icon: 'dashboard', shortcut: 'G H' },
  { id: 'nav-workouts', title: 'Zu den Workouts & Plänen', category: 'Navigation', icon: 'fitness_center', shortcut: 'G W' },
  { id: 'nav-labs', title: 'Zu den Laborwerten & Befunden', category: 'Navigation', icon: 'biotech', shortcut: 'G L' },
  { id: 'nav-settings', title: 'Einstellungen öffnen', category: 'Navigation', icon: 'settings', shortcut: 'G S' },

  // Aktionen & Tools
  { id: 'action-export-pdf', title: 'PDF-Arztbericht generieren', category: 'Aktionen', icon: 'picture_as_pdf' },
  { id: 'action-sync-now', title: 'Manuelle Cloud-Synchronisation erzwingen', category: 'Aktionen', icon: 'sync' }
];
```
