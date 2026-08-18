# Salus 2.0 — Performance-Budgets & Latenz-Optimierung
**Dokument:** `25-performance-budgets-and-optimization.md`  
**Status:** Verbindlich  
**Zweck:** Felsenfest eingehaltene Core Web Vitals (INP < 50ms, CLS = 0.00, LCP < 1.2s), Bundle-Budgets, dynamisches Code-Splitting und virtualisierte Listen.

---

## 1. Core Web Vitals & Performance-Garantien

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ METRIK                  │ ZIEL-BUDGET         │ METHODISCHE UMSETZUNG                   │
├─────────────────────────┼─────────────────────┼─────────────────────────────────────────┤
│ **INP (Interaction)**   │ < 50 ms (Ultra-Fast)│ Zero blocking JavaScript, Svelte 5      │
│                         │                     │ feine Reaktivität ($state / $derived)   │
├─────────────────────────┼─────────────────────┼─────────────────────────────────────────┤
│ **CLS (Layout Shift)**  │ = 0.00 (Zero Shift) │ `SkeletonCard` in exakter Kachelgröße,  │
│                         │                     │ `aspect-ratio` auf allen Grafiken       │
├─────────────────────────┼─────────────────────┼─────────────────────────────────────────┤
│ **LCP (Page Load)**     │ < 1.2 s (Local)     │ Dexie.js Sofort-Lesen aus IndexedDB     │
│                         │                     │ (kein Warten auf API-Roundtrips)        │
├─────────────────────────┼─────────────────────┼─────────────────────────────────────────┤
│ **Initial Bundle Size** │ < 150 KB gzip       │ Dynamisches Code-Splitting für schwere  │
│                         │                     │ Module (Barcode, PDF-Export, Krypto)    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Dynamisches Code-Splitting (Lazy Loading)

Schwere Bibliotheken werden erst dann geladen, wenn der Nutzer die Funktion tatsächlich aufruft:

```typescript
// Erst beim Klick auf "Barcode scannen":
async function loadBarcodeScanner() {
  const { BrowserMultiFormatReader } = await import('@zxing/browser');
  return new BrowserMultiFormatReader();
}

// Erst beim Klick auf "PDF-Arztbericht generieren":
async function loadPdfGenerator() {
  const { generateClinicalPdf } = await import('$lib/services/clinical-pdf');
  return generateClinicalPdf();
}
```

---

## 3. Listen-Virtualisierung (10.000+ Datensätze)

Historien mit tausenden Einträgen oder die 8.000 Lebensmittel der USDA-Datenbank werden virtualisiert gerendert: Nur die aktuell sichtbaren ~20 Zeilen befinden sich im DOM.
