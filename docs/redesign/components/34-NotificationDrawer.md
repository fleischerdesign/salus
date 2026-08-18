# Komponentenspezifikation: `NotificationDrawer.svelte`
**Pfad:** `frontend/src/lib/components/layout/NotificationDrawer.svelte`  
**Kategorie:** Organismus / Mitteilungs-Zentrale  
**Zweck:** Seitlicher Slide-Over-Drawer für zirkadiane Empfehlungen, Medikamenten-Erinnerungen, Meilenstein-Glückwünsche und System-Meldungen mit 1-Klick „Alle als gelesen markieren“.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🔔 MITTEILUNGEN                               [ Alle lesen ]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [ ☀️ ] Zirkadianer Impuls                      vor 15 Min   │
│ Koffein-Cutoff in 30 Minuten (14:30 Uhr).                   │
│                                                             │
│ [ 💊 ] Medikamente                             vor 2 Std    │
│ Telmisartan 20mg fällig um 08:00 Uhr.                       │
│                                                             │
│ [ 🏆 ] Neuer Rekord!                           Gestern      │
│ Bankdrücken: Neues 1RM von 94.0 kg erreicht!                │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface NotificationItem {
  id: string;
  type: 'circadian' | 'medication' | 'milestone' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
}

interface Props {
  open: boolean;
  notifications: NotificationItem[];
  onClose: () => void;
  onMarkAllAsRead: () => Promise<void> | void;
  onDismiss: (id: string) => Promise<void> | void;
}
```
