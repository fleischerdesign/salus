# 14 — Motion, Gesten & Haptik-Engine (Salus 2.0)

Salus 2.0 verwendet ein physikalisches Motion-System, das sich natürlich, taktil und reaktionsschnell anfühlt. Animationen dienen nicht der Dekoration, sondern vermitteln Orientierung, räumliche Tiefe und taktiles Feedback.

---

## 1. Physik- und Easing-Kurven (Svelte 5 Motion)

Salus definiert drei kanonische Easing-Kurven für konsistente Übergänge im gesamten Interface:

```css
:root {
  /* 1. Spring-Pop Easing (für Floating Docks, Decks & Dialoge) */
  --ease-spring: cubic-bezier(0.16, 1, 0.3, 1);

  /* 2. Swift Out Easing (für Tab-Wechsel & Einblendungen) */
  --ease-out: cubic-bezier(0, 0, 0.2, 1);

  /* 3. Smooth Decelerate (für Wellen- & Flüssigkeits-Physik) */
  --ease-fluid: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

---

## 2. Navigations-Übergänge & Sheet-Physik

### A. Mobile Bottom-Sheet Drawer Animation
Wenn auf Smartphones im Daumen-Dock ein Menü (`Track` oder `Klinik`) angetippt wird, gleitet das Menü von unten ins Bild:

```css
@keyframes sheetSlideUp {
  0% {
    transform: translateY(100%);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.flyout-deck.mobile {
  animation: sheetSlideUp 0.3s var(--ease-spring);
}
```

### B. Desktop Flyout-Deck Pop
Auf Desktop-Bildschirmen öffnet sich das Sub-Deck mit einer sanften Skalierungs- und Absenkungs-Animation:

```css
@keyframes deckPop {
  0% {
    transform: translateY(-8px) scale(0.98);
    opacity: 0;
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}
```

---

## 3. Touch-Gesten & Haptisches Feedback

### A. Taktile Haptik (`navigator.vibrate`)
Bei Benutzerinteraktionen auf Mobilgeräten wird gezielt haptisches Feedback ausgelöst:

| Event | Haptisches Muster | Zweck |
|---|---|---|
| **Satz im Workout abhaken** | `navigator.vibrate([15, 30, 15])` | Bestätigung des Trainingssatzes |
| **Pausentimer abgelaufen** | `navigator.vibrate([50, 100, 50, 100])` | Akustisch/taktiler Alert für den nächsten Satz |
| **Habit abgeschlossen** | `navigator.vibrate(20)` | Belohnender Mikro-Impuls |
| **Quick-Log Taste gedrückt** | `navigator.vibrate(10)` | Taktiles Tasten-Gefühl auf dem virtuellen Ziffernblock |

### B. Wischgesten (Touch Swiping)
1. **Swipe-to-Dismiss:** Bottom-Sheets können durch eine Wischbewegung nach unten (`touchmove` DeltaY > 80px) flüssig geschlossen werden.
2. **Horizontal Table Scrubbing:** Tabellen mit vielen Zeitreihen-Spalten besitzen `-webkit-overflow-scrolling: touch` mit sanftem kinetischen Trägheits-Scrollen.

---

## 4. Barrierefreiheit & `prefers-reduced-motion`

Für Nutzer mit vestibulären Störungen oder aktivierter Bewegungseinschränkung im Betriebssystem werden alle translatorischen und federnden Animationen automatisch auf sofortige Deckkraft-Wechsel (`opacity`) reduziert:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```
