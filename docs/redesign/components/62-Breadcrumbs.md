# Komponentenspezifikation: `Breadcrumbs.svelte`
**Pfad:** `frontend/src/lib/components/ui/Breadcrumbs.svelte`  
**Kategorie:** Molekül / Hierarchische Breadcrumb-Navigation  
**Zweck:** Barrierefreier Orientierungspfad auf Detail- und Unterseiten (z. B. `Track / Workouts / Pläne / Push Day A`) mit Icons und Chevron-Trennern.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🏠 Home  /  📊 Track  /  🏋️ Workouts  /  Push Day A         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: string;
}

interface Props {
  items: BreadcrumbItem[];
}
```
