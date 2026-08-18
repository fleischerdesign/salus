# Komponentenspezifikation: `DataTable.svelte`
**Pfad:** `frontend/src/lib/components/ui/DataTable.svelte`  
**Kategorie:** Organismus / Sortierbare & filterbare Datentabelle  
**Zweck:** Professionelle, hochperformante Tabelle für klinische Labordaten, Messwerthistorien und Übungslisten mit Spaltensortierung, Pagination, Zeilenauswahl und Sticky Header.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 [ In Tabelle suchen... ]       Spalten: [ ⚙️ ]  [ 📥 CSV ]│
├─────────────────────────────────────────────────────────────┤
│ [✓] Datum ▾        Messwert     Status       Aktion         │
│ ─────────────────────────────────────────────────────────── │
│ [ ] 14.08. 08:30   118/76 mmHg  🟢 Optimal   [ ✏️ ] [ 🗑️ ] │
│ [ ] 13.08. 08:15   122/78 mmHg  🟢 Optimal   [ ✏️ ] [ 🗑️ ] │
│ [ ] 12.08. 09:00   134/84 mmHg  🟡 Erhöht    [ ✏️ ] [ 🗑️ ] │
├─────────────────────────────────────────────────────────────┤
│ Seite 1 von 12     [ ◀ Zurück ]  [ 1 ][ 2 ][ 3 ]  [ Weiter ▶]│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface ColumnDef<T> {
  key: string;
  header: string;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  render?: (row: T) => unknown;
}

interface Props<T> {
  columns: ColumnDef<T>[];
  data: T[];
  searchable?: boolean;
  selectable?: boolean;
  selectedRows?: T[];
  pageSize?: number;
  onRowClick?: (row: T) => void;
  onSelectionChange?: (selected: T[]) => void;
}
```
