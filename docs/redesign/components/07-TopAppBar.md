# Komponentenspezifikation: `TopAppBar.svelte`
**Pfad:** `frontend/src/lib/components/layout/TopAppBar.svelte`  
**Kategorie:** Organismus / Desktop-Navigation  
**Zweck:** Schlanke, aufgeräumte und elegante Desktop-Navigationsleiste (≥ 1024px) mit 4 Hauptsäulen, globaler Suche (`Cmd+K`), Quick-Log Trigger und Live-Sync Statusanzeige.

---

## 1. Visuelle Spezifikation

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [Logo] salus     [ ☀️ Heute ]  [ 📊 Track ]  [ 🧠 Insights ]  [ 🏆 Hub ]      [ 🔍 Cmd+K ] [ + Log ] [🔔] [👤]│
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Höhe:** `64px` (`h-16`), fixiert am oberen Bildschirmrand (`sticky top-0 z-50`).
- **Hintergrund:** `bg-surface-0/85 backdrop-blur-md` mit extrem subtiler 1px-Trennlinie `border-b border-surface-200/60`.
- **Zentrierung:** Maximalbreite `1440px`, zentriert mit `px-6 md:px-10`.

---

## 2. Die 4 Hauptreiter (Morphing Navigation Indicator)

Jeder Navigations-Tab besitzt einen flüssigen, morphenden Unterstrich-Indikator:
```
[ ☀️ Heute ]   [ 📊 Track ]   [ 🧠 Insights ]   [ 🏆 Hub ]
   ━━━━━━━ (Aktiver Tab mit sanfter Feder-Animation)
```
- **Aktiv-State:** `text-primary-600 font-semibold`, unterstrichen mit 2px `bg-primary-500` und abgerundeten Kanten.
- **Inaktiv-State:** `text-surface-600 font-medium hover:text-surface-900 hover:bg-surface-100/50`.

---

## 3. Header-Aktionen (Rechte Seite)

1. **🔍 Command Palette Button (`Cmd+K`):**
   - Kompakte Suchleiste `[ 🔍 Suchen oder Befehl...  ⌘K ]`.
   - Ein Klick oder Druck auf `Cmd+K` öffnet die globale Such- und Befehlszentrale.
2. **➕ Universal `+ Loggen` Button:**
   - Pillen-Button `bg-primary-500 hover:bg-primary-600 text-white font-semibold shadow-sm`.
   - Öffnet sofort das `QuickLogSheet`.
3. **🔔 Benachrichtigungs-Glocke (`NotificationBell`):**
   - Mit animiertem rotem Badge bei ungelesenen Hinweisen.
4. **👤 Profil & Live-Sync Pille (`UserMenu`):**
   - Zeigt das Benutzer-Avatar-Icon + Status-Dot:
     - 🟢 **Grün (`active`):** SSE Live-Sync verbunden.
     - 🟡 **Amber (`syncing`):** Synchronisation läuft oder offline.
     - 🔴 **Rot (`error`):** Sitzung abgelaufen.

---

## 4. Props & Schnittstellen

```typescript
interface Props {
  currentPath: string;
  dotStatus: 'active' | 'syncing' | 'error';
  unreadNotificationsCount?: number;
  onOpenQuickLog: () => void;
  onOpenCommandPalette: () => void;
}
```
