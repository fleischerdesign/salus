# Komponentenspezifikation: `E2EEShareCard.svelte`
**Pfad:** `frontend/src/lib/components/sharing/E2EEShareCard.svelte`  
**Kategorie:** Molekül / Kryptographische Freigabekarte  
**Zweck:** Verwaltung aktiver asymmetrischer Arzt- und Coach-Freigaben mit PIN-Reveal, Ablauf-Countdown, verschlüsseltem Link-Kopierer und sofortigem Widerruf-Button (`Revoke`).

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🔐 FREIGABE: DR. MED. WEBER (Kardiologie)       [ Aktiv 🟢 ]│
│ Erstellt am 10.08.2026 • Gültig bis 24.08.2026 (Noch 7 Tage) │
├─────────────────────────────────────────────────────────────┤
│  Freigegebene Daten:                                        │
│  [✓] Blutdruck & Puls  [✓] Lipidprofil  [✓] Medikationsplan │
│                                                             │
│  Link & Schutz:                                             │
│  🔗 [ https://salus.health/shares/e2e_8f3a... ] [ 📋 Kopieren ]│
│  🔑 Einmal-PIN: [ •••• ] [ 👁️ PIN anzeigen: 8492 ]          │
│                                                             │
│  [ 🚫 Freigabe sofort widerrufen ]                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  shareId: string;
  recipientName: string;
  expiresAt: string;
  shareUrl: string;
  pin: string;
  sharedDataTypes: string[];
  accessCount: number;
  onRevoke: () => Promise<void> | void;
}
```
