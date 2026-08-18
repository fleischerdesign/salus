<script lang="ts">
  import Icon from '../ui/Icon.svelte';

  let {
    initialSeconds = 90,
    running = false,
    oncomplete,
    onclose
  } = $props<{
    initialSeconds?: number;
    running: boolean;
    oncomplete?: () => void;
    onclose?: () => void;
  }>();

  let totalSeconds = $state(90);
  let remainingSeconds = $state(0);
  let intervalId: ReturnType<typeof setInterval> | null = null;

  function playGentleChime() {
    try {
      if (typeof window !== 'undefined') {
        if ('vibrate' in navigator) {
          navigator.vibrate([100, 60, 150]);
        }
        const AudioCtx =
          window.AudioContext ||
          (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        const ctx = new AudioCtx();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
        osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5
        gain.gain.setValueAtTime(0.15, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.5);
      }
    } catch (e) {
      void e;
    }
  }

  $effect(() => {
    if (running) {
      totalSeconds = initialSeconds || 90;
      remainingSeconds = initialSeconds || 90;
      if (intervalId) clearInterval(intervalId);
      intervalId = setInterval(() => {
        if (remainingSeconds > 0) {
          remainingSeconds--;
          if (remainingSeconds === 0) {
            playGentleChime();
          }
        } else {
          if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
          }
          oncomplete?.();
          onclose?.();
        }
      }, 1000);
    } else {
      remainingSeconds = 0;
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
      }
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  });

  function adjustTime(secs: number) {
    remainingSeconds = Math.max(5, remainingSeconds + secs);
    totalSeconds = Math.max(totalSeconds, remainingSeconds);
  }

  function skip() {
    remainingSeconds = 0;
    if (intervalId) clearInterval(intervalId);
    intervalId = null;
    oncomplete?.();
    onclose?.();
  }

  let formattedTime = $derived.by(() => {
    const m = Math.floor(remainingSeconds / 60);
    const s = remainingSeconds % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  });

  let progressPercent = $derived(totalSeconds > 0 ? (remainingSeconds / totalSeconds) * 100 : 0);

  let circumference = 2 * Math.PI * 18;
  let strokeDashoffset = $derived(circumference - (progressPercent / 100) * circumference);
</script>

{#if running && remainingSeconds > 0}
  <!-- Centered Floating Rest Timer Bar (Above Mobile Nav Dock on mobile, Centered bottom on desktop) -->
  <div
    class="fixed bottom-20 left-1/2 z-50 flex w-[calc(100%-2rem)] max-w-sm -translate-x-1/2 animate-[slideUp_0.2s_ease-out] items-center justify-between gap-3 rounded-3xl border border-[var(--color-primary)]/40 bg-[var(--glass-dock-bg)] p-3 shadow-2xl ring-2 ring-[var(--color-primary)]/20 backdrop-blur-2xl sm:max-w-md sm:gap-4 sm:p-3.5 md:bottom-6"
  >
    <!-- Left: Dial Ring + Single Clear Countdown Display -->
    <div class="flex items-center gap-3">
      <!-- Circular Progress Ring (Icon inside, no duplicate numbers) -->
      <div class="relative flex h-10 w-10 shrink-0 items-center justify-center sm:h-11 sm:w-11">
        <svg class="h-full w-full -rotate-90" viewBox="0 0 44 44">
          <circle
            cx="22"
            cy="22"
            r="18"
            fill="none"
            stroke="var(--border-subtle)"
            stroke-width="3.5"
          />
          <circle
            cx="22"
            cy="22"
            r="18"
            fill="none"
            stroke="var(--color-primary)"
            stroke-width="3.5"
            stroke-linecap="round"
            stroke-dasharray={circumference}
            stroke-dashoffset={strokeDashoffset}
            class="transition-all duration-300"
          />
        </svg>
        <span class="absolute flex items-center justify-center text-[var(--color-primary)]">
          <Icon name="timer" size="sm" />
        </span>
      </div>

      <!-- Single Primary Countdown Display -->
      <div>
        <span
          class="block text-[0.625rem] font-extrabold tracking-wider text-[var(--text-muted)] uppercase"
          >Satzpause</span
        >
        <div
          class="text-base leading-tight font-black text-[var(--text-main)] tabular-nums sm:text-lg"
        >
          {formattedTime}
        </div>
      </div>
    </div>

    <!-- Right: Quick Steppers & Skip Button -->
    <div class="flex items-center gap-1 sm:gap-1.5">
      <button
        type="button"
        onclick={() => adjustTime(-15)}
        class="cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] px-2 py-1 text-[0.6875rem] font-bold text-[var(--text-muted)] transition-colors hover:bg-[var(--bg-surface-50)] hover:text-[var(--text-main)]"
        title="-15 Sekunden"
      >
        -15s
      </button>
      <button
        type="button"
        onclick={() => adjustTime(30)}
        class="cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] px-2 py-1 text-[0.6875rem] font-bold text-[var(--text-main)] transition-colors hover:bg-[var(--bg-surface-50)]"
        title="+30 Sekunden"
      >
        +30s
      </button>
      <button
        type="button"
        onclick={skip}
        class="cursor-pointer rounded-xl bg-[var(--color-primary)] px-3 py-1.5 text-xs font-bold whitespace-nowrap text-white shadow-xs transition-all hover:opacity-90"
      >
        Fertig
      </button>
    </div>
  </div>
{/if}
