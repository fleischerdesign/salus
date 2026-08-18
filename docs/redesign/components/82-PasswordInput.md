# Komponentenspezifikation: `PasswordInput.svelte`
**Pfad:** `frontend/src/lib/components/ui/PasswordInput.svelte`  
**Kategorie:** Atom / Sicheres Passworteingabe-Feld  
**Zweck:** Passwortfeld mit Auge-Umschalter (Passwort anzeigen/verbergen), Caps-Lock-Warnanzeige und optionalem dynamischem Passwort-Stärkebalken.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  Passwort                                                   │
│  [ ••••••••••••••••••                          ] [ 👁️ Zeigen]│
│  [██████████████████████░░░░░░] Stärke: Stark (14 Zeichen)  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value: string;
  label?: string;
  placeholder?: string;
  showStrength?: boolean;
  error?: string;
  onchange: (val: string) => void;
}
```
