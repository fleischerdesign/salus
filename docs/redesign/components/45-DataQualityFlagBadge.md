# Komponentenspezifikation: `DataQualityFlagBadge.svelte`
**Pfad:** `frontend/src/lib/components/ui/DataQualityFlagBadge.svelte`  
**Kategorie:** Atom / Datenqualitäts-Warnbadge  
**Zweck:** Dezent platziertes Warn-Badge bei unplausiblen Messwerten (z. B. 800 kg statt 80.0 kg, doppelter Eintrag, Zeitzonenverschiebung) mit 1-Klick Reparatur-Dialog.

---

## 1. Visuelle Spezifikation

```
[ ⚠️ Unplausibler Wert: 800.0 kg ] ➔ (Öffnet Reparatur-Popover)
┌─────────────────────────────────────────────────────────────┐
│ ⚠️ DATENQUALITÄTS-WARNUNG                                   │
├─────────────────────────────────────────────────────────────┤
│ Wert weicht um +900% vom 7-Tage-Schnitt (82.4 kg) ab.       │
│ Wahrscheinlich liegt ein Komma-Tippfehler vor.              │
│                                                             │
│ [ ✏️ Auf 80.0 kg korrigieren ]   [ 🗑️ Eintrag löschen ]     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  flagType: 'outlier' | 'duplicate' | 'timezone_anomaly';
  currentValue: number | string;
  suggestedFix?: number | string;
  onApplyFix: () => Promise<void> | void;
  onDismiss: () => void;
}
```
