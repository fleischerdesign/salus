# Komponentenspezifikation: `BarcodeScanner.svelte`
**Pfad:** `frontend/src/lib/components/food/BarcodeScanner.svelte`  
**Kategorie:** Organismus / Kamera-Scanner  
**Zweck:** Extrem schneller, kamera-basierter Barcode-Scanner für Lebensmittel (EAN-13, UPC) mit animiertem Fadenkreuz-Zielsucher, Taschenlampen-Schalter und sofortigem Dexie-/OpenFoodFacts-Lookup.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  [ 🔦 Blitz ]        BARCODE SCANNEN                 [ ✕ ] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌───────────────────┐                    │
│                    │ ╔               ╗ │                    │
│                    │   ═════════════   │ (Roter Laser-Scan) │
│                    │ ╚               ╝ │                    │
│                    └───────────────────┘                    │
│                                                             │
│       "Halte den Barcode in den Rahmen zur Erkennung"       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  open: boolean;
  onDetect: (barcode: string) => void;
  onClose: () => void;
}
```
