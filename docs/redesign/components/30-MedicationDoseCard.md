# Komponentenspezifikation: `MedicationDoseCard.svelte`
**Pfad:** `frontend/src/lib/components/medications/MedicationDoseCard.svelte`  
**Kategorie:** Molekül / Medikamenten-Einnahmekarte  
**Zweck:** Geordnete Einnahme-Kachel mit 1-Klick-Adhärenz-Häkchen, Dosierungs-Stärke, Mahlzeiten-Hinweisen und Vorrats-Warn-Badge.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ [💊] TELMISARTAN                                   08:00 UHR│
│ 20 mg (1 Tablette) • Morgens nüchtern mit Wasser            │
│ [ ⚠️ Vorrat: Noch 5 Tabletten (Rezept anfordern) ]           │
│                                                             │
│                                           [ ✓ Eingenommen ] │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  medicationName: string;
  dosage: string; // z.B. "20 mg"
  scheduledTime: string; // z.B. "08:00"
  instructions?: string; // z.B. "Nüchtern vor dem Frühstück"
  stockRemaining?: number;
  stockThreshold?: number;
  taken: boolean;
  takenAt?: string | null;
  onToggleTaken: (taken: boolean) => Promise<void> | void;
}
```
