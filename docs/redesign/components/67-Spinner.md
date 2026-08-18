# Komponentenspezifikation: `Spinner.svelte`
**Pfad:** `frontend/src/lib/components/ui/Spinner.svelte`  
**Kategorie:** Atom / Minimalistischer SVG-Ladekreis  
**Zweck:** Ästhetischer, minimalistischer Ladeindikator für asynchrone Aktionen (z. B. PDF-Generierung, Barcode-Lookup, Sync-Push).

---

## 1. Visuelle Spezifikation

```
( ◌ ) Drehender SVG-Kreis mit sanftem Nachlauf
```

- **Animation:** `animate-spin` mit `cubic-bezier` Rotation.
- **Größen:** `xs` (14px für Buttons), `sm` (20px), `md` (28px), `lg` (44px für Screen-Loader).

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  size?: 'xs' | 'sm' | 'md' | 'lg';
  color?: string; // Standard: currentColor
  class?: string;
}
```
