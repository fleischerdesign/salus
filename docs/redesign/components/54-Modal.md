# Komponentenspezifikation: `Modal.svelte`
**Pfad:** `frontend/src/lib/components/ui/Modal.svelte`  
**Kategorie:** Organismus / Universeller Dialog  
**Zweck:** Barrierefreier, animierter Fokus-Dialog mit Backdrop-Blur, Focus-Trap, sanftem Skalierungs-Einstieg (`scale-95` → `scale-100`) und Schließen per `Escape`.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ [Icon] DIALOG-TITEL                                      [×]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ( Modal Body / Inhalt )                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [ Abbrechen ]                               [ Bestätigen ]  │
└─────────────────────────────────────────────────────────────┘
```

- **Backdrop:** `fixed inset-0 bg-surface-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4`.
- **Panel:** `bg-surface-0 rounded-2xl shadow-2xl border border-surface-200 w-full max-w-lg overflow-hidden`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  open: boolean;
  title?: string;
  subtitle?: string;
  icon?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  onclose: () => void;
  header?: Snippet;
  footer?: Snippet;
  children: Snippet;
}
```
