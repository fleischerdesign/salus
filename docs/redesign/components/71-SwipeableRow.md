# Komponentenspezifikation: `SwipeableRow.svelte`
**Pfad:** `frontend/src/lib/components/ui/SwipeableRow.svelte`  
**Kategorie:** Molekül / Wischbare Touch-Listenzeile  
**Zweck:** Touch-optimierte Listenzeile für Mobilgeräte mit aufdeckbaren Wischaktionen (z. B. nach rechts wischen für *„Erledigt [✓]“*, nach links wischen für *„Löschen [🗑️]“* und *„Bearbeiten [✏️]“*) mit magnetischem Einrasten und Haptik.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  [ ✓ Erledigt ] ── ➔  [ 3L Wasser getrunken ]  ← ── [ 🗑️ Löschen ]│
└─────────────────────────────────────────────────────────────┘
```

- **Rechts-Wisch (Grün):** Löst bei Überschreiten von 40% Zeilenbreite automatisch die Erfolgs-Aktion aus (inkl. Vibration).
- **Links-Wisch (Rot/Grau):** Deckt Löschen- und Bearbeiten-Buttons auf.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  onSwipeRight?: () => void;
  onSwipeLeft?: () => void;
  rightActionLabel?: string;
  leftActionLabel?: string;
  children: Snippet;
}
```
