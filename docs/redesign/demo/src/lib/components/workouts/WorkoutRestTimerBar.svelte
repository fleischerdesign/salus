<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

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
  let remainingSeconds = $state(90);
  let intervalId: any = null;

  $effect(() => {
    if (running) {
      totalSeconds = initialSeconds;
      remainingSeconds = initialSeconds;
      if (intervalId) clearInterval(intervalId);
      intervalId = setInterval(() => {
        if (remainingSeconds > 0) {
          remainingSeconds--;
        } else {
          clearInterval(intervalId);
          intervalId = null;
          oncomplete?.();
        }
      }, 1000);
    } else {
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
      }
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  });

  function addTime(secs: number) {
    remainingSeconds = Math.max(0, remainingSeconds + secs);
    totalSeconds = Math.max(totalSeconds, remainingSeconds);
  }

  function skip() {
    remainingSeconds = 0;
    if (intervalId) clearInterval(intervalId);
    oncomplete?.();
    onclose?.();
  }

  let formattedTime = $derived.by(() => {
    const m = Math.floor(remainingSeconds / 60);
    const s = remainingSeconds % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  });

  let progressPercent = $derived(
    totalSeconds > 0 ? (remainingSeconds / totalSeconds) * 100 : 0
  );

  let circumference = 2 * Math.PI * 18;
  let strokeDashoffset = $derived(
    circumference - (progressPercent / 100) * circumference
  );
</script>

{#if running || remainingSeconds > 0}
  <div class="fixed bottom-6 right-6 z-50 bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--color-primary)]/40 rounded-3xl p-3.5 shadow-2xl flex items-center gap-4 animate-[slideUp_0.2s_ease-out] ring-2 ring-[var(--color-primary)]/20">
    
    <!-- Circular Progress Dial -->
    <div class="relative w-12 h-12 flex items-center justify-center shrink-0">
      <svg class="w-full h-full -rotate-90" viewBox="0 0 44 44">
        <circle cx="22" cy="22" r="18" fill="none" stroke="var(--border-subtle)" stroke-width="3.5" />
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
      <span class="absolute text-[0.6875rem] font-extrabold text-[var(--color-primary)] tabular-nums">
        {remainingSeconds}s
      </span>
    </div>

    <!-- Timer Info & Time String -->
    <div>
      <div class="flex items-center gap-1.5">
        <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Pausentimer</span>
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
      </div>
      <div class="text-lg font-extrabold text-[var(--text-main)] tabular-nums">
        {formattedTime}
      </div>
    </div>

    <!-- Controls -->
    <div class="flex items-center gap-1.5 border-l border-[var(--border-subtle)] pl-3">
      <button
        type="button"
        onclick={() => addTime(30)}
        class="px-2 py-1 rounded-lg bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[0.6875rem] font-bold text-[var(--text-main)] hover:bg-[var(--bg-surface-50)] cursor-pointer"
        title="+30 Sekunden"
      >
        +30s
      </button>
      <button
        type="button"
        onclick={() => addTime(15)}
        class="px-2 py-1 rounded-lg bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[0.6875rem] font-bold text-[var(--text-main)] hover:bg-[var(--bg-surface-50)] cursor-pointer"
        title="+15 Sekunden"
      >
        +15s
      </button>
      <button
        type="button"
        onclick={skip}
        class="px-2.5 py-1 rounded-lg bg-[var(--color-primary)] text-white text-[0.6875rem] font-bold hover:opacity-90 cursor-pointer shadow-2xs"
      >
        Fertig
      </button>
    </div>

  </div>
{/if}
