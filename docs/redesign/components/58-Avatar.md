# Komponentenspezifikation: `Avatar.svelte`
**Pfad:** `frontend/src/lib/components/ui/Avatar.svelte`  
**Kategorie:** Atom / Benutzer-Avatar  
**Zweck:** Ästhetischer Benutzer-Avatar mit Initialen-Fallback, deterministischem Farbverlauf, Bild-Unterstützung und optionalem Live-Sync Status-Dot.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  [ ( PM ) 🟢 ] Philipp M. • Live Sync aktiv                 │
└─────────────────────────────────────────────────────────────┘
```

- **Größen:** `xs` (24px), `sm` (32px), `md` (40px), `lg` (48px), `xl` (64px).
- **Status-Dot:** Grüner, gelber oder roter 8px-Kreis am unteren rechten Rand (`border-2 border-surface-0`).

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  name: string;
  src?: string | null;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  status?: 'active' | 'syncing' | 'offline' | 'error' | null;
}
```
