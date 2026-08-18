# Komponentenspezifikation: `ConflictResolver.svelte`
**Pfad:** `frontend/src/lib/components/sync/ConflictResolver.svelte`  
**Kategorie:** Organismus / Datenkonflikt-Auflösung  
**Zweck:** Feld-für-Feld visueller Vergleich und manuelle Auflösung bei kollidierenden Offline-Änderungen mehrerer Geräte.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️ SYNCHRONISATIONS-KONFLIKT BEI DER MAHLZEIT                │
├─────────────────────────────────────────────────────────────┤
│  Feld           Lokale Version (Dieses Gerät)  Server-Version│
│  ────────────────────────────────────────────────────────── │
│  Name           (•) Hähnchen-Reis-Bowl         ( ) Lunch     │
│  Kalorien       ( ) 650 kcal                   (•) 620 kcal  │
│  Notiz          (•) Mit Avocado                ( ) Keine     │
│                                                             │
│  [ Alle Meine übernehmen ]     [ Ausgewählte zusammenführen]│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface ConflictField {
  key: string;
  label: string;
  localValue: unknown;
  serverValue: unknown;
  selected: 'local' | 'server';
}

interface Props {
  entity: string;
  recordId: string;
  fields: ConflictField[];
  onResolve: (mergedRecord: Record<string, unknown>) => Promise<void> | void;
}
```
