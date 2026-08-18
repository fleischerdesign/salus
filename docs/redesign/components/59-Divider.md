# Komponentenspezifikation: `Divider.svelte`
**Pfad:** `frontend/src/lib/components/ui/Divider.svelte`  
**Kategorie:** Atom / Feine Haarlinien-Trennlinie  
**Zweck:** 1px-Haarlinie zur Trennung von Abschnitten mit optionalem zentriertem Label, Icon oder Schattierung.

---

## 1. Visuelle Spezifikation

```
─────── ODER ───────
```

- **Styling:** `border-t border-surface-200/80 my-4`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  label?: string;
  icon?: string;
  vertical?: boolean;
}
```
