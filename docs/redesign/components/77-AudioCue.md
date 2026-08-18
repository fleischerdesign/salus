# Komponentenspezifikation: `AudioCue.svelte`
**Pfad:** `frontend/src/lib/components/ui/AudioCue.svelte`  
**Kategorie:** Atom / Synthetisiertes Audio- & Akustik-Signal  
**Zweck:** Ressourcenschonende, mathematisch synthetisierte Tonsignale via Web Audio API (Rest-Timer Ende-Gong, Countdown-Ticks, PR-Celebration-Chime, Habit-Klick) ohne externe MP3-Dateien.

---

## 1. Akustische Signal-Arten

1. **`timer_tick`:** Subtiler 800Hz Sinus-Klick (15ms) bei 3.. 2.. 1.. Rest-Timer.
2. **`timer_finish`:** Zweiton-Harmonie (523Hz C5 → 659Hz E5, 250ms) bei Pausenende.
3. **`pr_celebration`:** Aufsteigender Dur-Akkord (C5 - E5 - G5 - C6) bei persönlicher Bestleistung.
4. **`habit_check`:** Knackiger 1200Hz Haptik-Klick.

---

## 2. API-Schnittstelle (Modul / Runes)

```typescript
export type SoundType = 'timer_tick' | 'timer_finish' | 'pr_celebration' | 'habit_check';

export function playAudioCue(type: SoundType, volume = 0.5): void;
```
