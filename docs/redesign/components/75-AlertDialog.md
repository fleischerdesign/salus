# Komponentenspezifikation: `AlertDialog.svelte`
**Pfad:** `frontend/src/lib/components/ui/AlertDialog.svelte`  
**Kategorie:** Organismus / Destruktiver Bestätigungsdialog  
**Zweck:** Hochprioritärer Bestätigungsdialog für destruktive Aktionen (z. B. *„Trainingsplan löschen“*, *„Konto zurücksetzen“*, *„Laborbefund unwiderruflich entfernen“*) mit rotem Gefahren-CTA und Tastatur-Fokus-Schutz.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️ TRAININGSPLAN WIRKLICH LÖSCHEN?                          │
├─────────────────────────────────────────────────────────────┤
│ Möchtest du den Plan "Push Day A" wirklich löschen?         │
│ Deine bisherigen Trainings-Logs bleiben in der Historie     │
│ erhalten, aber der Plan wird aus der Auswahl entfernt.      │
├─────────────────────────────────────────────────────────────┤
│ [ Abbrechen (Fokus) ]                [ 🗑️ Ja, Plan löschen ]│
└─────────────────────────────────────────────────────────────┘
```

- **Sicherheits-Standard:** Der Standard-Fokus liegt bewusst auf `[ Abbrechen ]`, um versehentliches Bestätigen per Enter-Taste auszuschließen.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'info';
  onconfirm: () => Promise<void> | void;
  oncancel: () => void;
}
```
