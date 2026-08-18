# Komponentenspezifikation: `OtpInput.svelte`
**Pfad:** `frontend/src/lib/components/ui/OtpInput.svelte`  
**Kategorie:** Molekül / 4–6-stelliger PIN- & OTP-Eingabeblock  
**Zweck:** Getrennte Ziffernkästchen für die Eingabe von Arzt-Freigabe-PINs oder 2FA-Tokens mit automatischem Vorrücken des Fokus, Backspace-Rücksprung und Clipboard-Paste.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  EINMAL-PIN EINGEBEN:                                       │
│                                                             │
│    ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐            │
│    │ 8 │   │ 4 │   │ 9 │   │ 2 │   │ 0 │   │ 7 │            │
│    └───┘   └───┘   └───┘   └───┘   └───┘   └───┘            │
│                                                             │
│  [ Aus Zwischenablage einfügen ]                            │
└─────────────────────────────────────────────────────────────┘
```

- **Kästchen:** `h-14 w-12 text-2xl font-bold text-center border border-surface-300 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  length?: number; // Standard: 6 (oder 4 für PIN)
  value: string;
  disabled?: boolean;
  onchange: (pin: string) => void;
  oncomplete?: (pin: string) => void;
}
```
