# Komponentenspezifikation: `BottomNavBar.svelte`
**Pfad:** `frontend/src/lib/components/layout/BottomNavBar.svelte`  
**Kategorie:** Organismus / Mobile PWA-Navigation  
**Zweck:** Daumen-optimierte Navigationsleiste am unteren Bildschirmrand für Smartphones (< 1024px) mit 4 Hauptreitern und einem erhabenen, zentrierten Quick-Log Action Button.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   [ ☀️ ]       [ 📊 ]          ( ➕ )          [ 🧠 ]     [ ⚙️ ]  │
│   Heute        Track          QuickLog       Insights    Hub    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

- **Höhe:** `60px` + `env(safe-area-inset-bottom)` (feste PWA-Positionierung am unteren Bildschirmrand `fixed bottom-0 left-0 right-0 z-50`).
- **Hintergrund:** `bg-surface-0/90 backdrop-blur-lg border-t border-surface-200/80 shadow-float`.
- **Der Zentrierte Quick-Log Button (FAB):**
  - Durchmesser: `52px` × `52px`.
  - Schwebt um `-18px` über die Leiste hinaus (`-translate-y-4`).
  - Farbverlauf: `bg-gradient-to-tr from-primary-600 to-primary-500 text-white shadow-lg shadow-primary-500/30`.
  - Haptischer Klick-Effekt (`active:scale-90 transition-transform`).

---

## 2. Die 5 Navigations-Slots

```
┌───────────┬──────────────┬───────────────────┬────────────────────────────────────────┐
│ Slot      │ Label        │ Icon              │ Ziel-Route                             │
├───────────┼──────────────┼───────────────────┼────────────────────────────────────────┤
│ 1 (Links) │ **Heute**    │ `dashboard`       │ `/` (Dashboard / Cockpit)              │
│ 2         │ **Track**    │ `vital_signs`     │ `/track` (Alle Disziplinen & Logbuch)  │
│ 3 (Mitte) │ **Log (+)**  │ `add`             │ Öffnet `QuickLogSheet.svelte`          │
│ 4         │ **Insights** │ `insights`        │ `/insights` (Trends & Zirkadian-Uhr)   │
│ 5 (Rechts)│ **Hub**      │ `person`          │ `/hub/goals` (Ziele, Profil, Settings) │
└───────────┴──────────────┴───────────────────┴────────────────────────────────────────┘
```

---

## 3. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  currentPath: string;
  onOpenQuickLog: () => void;
}
```

---

## 4. Haptik & Barrierefreiheit

1. **Touch-Target-Größe:** Jeder Tab hat eine Mindestklickfläche von `48px × 48px`.
2. **Haptik:** Bei Tippen auf den Center-FAB oder Tab-Wechsel wird auf Mobilgeräten eine kurze 15ms Vibration ausgelöst (`navigator.vibrate(15)`).
3. **Safe Area:** Die Leiste schmiegt sich nahtlos um die Home-Indicator-Leiste moderner iOS- und Android-Smartphones an.
