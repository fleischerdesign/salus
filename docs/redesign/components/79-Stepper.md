# Komponentenspezifikation: `Stepper.svelte`
**Pfad:** `frontend/src/lib/components/ui/Stepper.svelte`  
**Kategorie:** Molekül / Mehrstufiger Wizard-Fortschritt  
**Zweck:** Visueller Schritt-für-Schritt Ablauf für Onboarding, E2EE-Freigabe-Erstellung oder komplexe Labor-Erfassungen mit erledigten, aktiven und anstehenden Schritt-Indikatoren.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  ( ✓ 1. Daten wählen ) ── ( • 2. Schutz / PIN ) ── ( 3. Link teilen )│
└─────────────────────────────────────────────────────────────┘
```

- **Completed:** `bg-success-500 text-white rounded-full h-8 w-8 flex items-center justify-center`.
- **Active:** `border-2 border-primary-500 text-primary-600 font-bold bg-primary-50 rounded-full h-8 w-8`.
- **Pending:** `border border-surface-300 text-surface-400 bg-surface-100 rounded-full h-8 w-8`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Step {
  id: string;
  label: string;
  description?: string;
}

interface Props {
  steps: Step[];
  currentStepIndex: number;
  onStepClick?: (index: number) => void;
}
```
