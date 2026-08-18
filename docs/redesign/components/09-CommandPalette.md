# Komponentenspezifikation: `CommandPalette.svelte`
**Pfad:** `frontend/src/lib/components/ui/CommandPalette.svelte`  
**Kategorie:** Organismus / Universelle Befehls- & Suchzentrale  
**Zweck:** Blitzschnelles Durchsuchen der gesamten Salus-Plattform (Lebensmittel, Übungen, Metriken, Rezepte, Einstellungen, Aktionen) per Tastatur (`Cmd+K`).

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔍 [ Tippe einen Befehl oder suche nach Lebensmitteln, Übungen...    ] [ESC]│
├─────────────────────────────────────────────────────────────────────────────┤
│  SCHNELLAKTIONEN:                                                           │
│  [ ➕ ] Wasser erfassen (+250ml / +500ml)                                ↵  │
│  [ 🏃 ] Neues Training starten (Push Day A)                               ↵  │
│  [ ⚖️ ] Körpergewicht eintragen                                           ↵  │
├─────────────────────────────────────────────────────────────────────────────┤
│  DISZIPLINEN & NAVIGATION:                                                  │
│  [ 📊 ] Logbuch: Blutdruck & Ruhepuls                                       │
│  [ 🥗 ] Ernährung: Mahlzeiten-Tagebuch                                      │
│  [ 🧬 ] Klinische Labore & Blutbild                                         │
│  [ ⚙️ ] Einstellungen: E2EE-Freigaben & Arzt-Links                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  SUCHERGEBNISSE (z. B. "Hähnchen"):                                         │
│  [ 🍗 ] Hähnchenbrustfilet (100g • 165 kcal • 31g P • 0g C • 3.6g F)        │
│  [ 🍲 ] Rezept: Hähnchen-Reis-Curry (Portion • 540 kcal • 42g P)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

- **Position:** Zentriertes Floating-Modal (`top: 15vh`, Breite `640px`).
- **Hintergrund:** `bg-surface-0 shadow-2xl rounded-2xl border border-surface-200`.
- **Backdrop:** `backdrop-blur-md bg-surface-900/40`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  open: boolean;
  onclose: () => void;
}
```

---

## 3. Tastatur-Steuerung

- **Pfeiltasten (`Up / Down`):** Navigiert durch die Ergebnisliste mit aktiver Hervorhebung.
- **Enter (`↵`):** Führt die ausgewählte Aktion aus oder navigiert zur ausgewählten Route.
- **Escape (`ESC`):** Schließt die Command Palette sofort.
