# Komponentenspezifikation: `Pagination.svelte`
**Pfad:** `frontend/src/lib/components/ui/Pagination.svelte`  
**Kategorie:** Molekül / Seiten-Navigation  
**Zweck:** Barrierefreie Pagination für Tabellen, Historien-Listen und Rezept-Kataloge mit Seitennummern, Auslassungspunkten (`...`), Vor/Zurück-Buttons und Zeilen-pro-Seite-Wähler.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  Zeige 1 - 20 von 248 Einträgen            [ 20 pro Seite ▾]│
│                                                             │
│  [ ◀ Zurück ]  [ 1 ]  [ 2 (Aktiv) ]  [ 3 ]  ...  [ 13 ]  [ Weiter ▶]│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  currentPage: number;
  totalPages: number;
  pageSize?: number;
  totalItems?: number;
  pageSizeOptions?: number[]; // [10, 20, 50, 100]
  onPageChange: (newPage: number) => void;
  onPageSizeChange?: (newSize: number) => void;
}
```
