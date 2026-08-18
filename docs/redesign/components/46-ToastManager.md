# Komponentenspezifikation: `ToastManager.svelte`
**Pfad:** `frontend/src/lib/components/ui/ToastManager.svelte`  
**Kategorie:** Organismus / Globaler Feedback- & Undo-Stack  
**Zweck:** Schwebender Toast-Stack für Erfolgsmeldungen (*„+250ml Wasser erfasst“*), Warnungen und Lösch-Aktionen mit integriertem `[ Rückgängig ]` Button und Haptik-Signal.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ [ ✓ ] 250ml Wasser erfasst!                  [ Rückgängig ] │
│ ─────────────────────────────────────────────────────────── │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (4s Auto-Dismiss-Bar)│
└─────────────────────────────────────────────────────────────┘
```

- **Position:** Feste Verankerung unten rechts auf Desktop (`bottom-6 right-6`), zentriert oben auf Mobile (`top-4 left-4 right-4`).
- **Design:** `bg-surface-900 text-white rounded-xl shadow-2xl p-3.5 flex items-center justify-between gap-3 border border-surface-700`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Toast {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  message: string;
  durationMs?: number;
  undoAction?: () => Promise<void> | void;
}

interface Props {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}
```
