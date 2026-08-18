# Komponentenspezifikation: `Tabs.svelte`
**Pfad:** `frontend/src/lib/components/ui/Tabs.svelte`  
**Kategorie:** Molekül / Tab-Navigation  
**Zweck:** Horizontale Tab-Leiste für Unterabschnitte (z. B. *Übersicht*, *Historie*, *Statistik*, *Notizen*) mit schiebendem Hintergrund-Pillen-Indikator oder unterstrichenem Strich.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  [ 📊 Übersicht (Aktiv) ]   [ 📈 Verlauf ]   [ ℹ️ Details ] │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface TabItem<T = string> {
  id: T;
  label: string;
  icon?: string;
  badge?: string | number;
}

interface Props<T = string> {
  tabs: TabItem<T>[];
  activeTab: T;
  variant?: 'pills' | 'underline';
  onchange: (tabId: T) => void;
}
```
