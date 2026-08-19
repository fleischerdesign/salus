<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { nowIso } from '$lib/utils/datetime';
  import { createMeasurement } from '$lib/mutations/measurement';

  let { currentMl = $bindable(2250), targetMl = 3000 } = $props<{
    currentMl?: number;
    targetMl?: number;
  }>();

  let percentage = $derived(Math.min(100, Math.round((currentMl / targetMl) * 100)));

  async function addAmount(ml: number) {
    currentMl += ml;
    await createMeasurement('hydration', {
      value_numeric: ml,
      start_time: nowIso(),
      unit: 'ml'
    });
  }
</script>

<div
  class="flex flex-col justify-between space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-card"
>
  <div class="flex items-start justify-between gap-3">
    <div class="flex min-w-0 items-center gap-3">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
        style="background-color: color-mix(in srgb, var(--color-hydrate) 12%, transparent); color: var(--color-hydrate);"
      >
        <Icon name="water-drop" size="md" />
      </div>
      <div class="min-w-0">
        <h3 class="truncate text-sm font-extrabold tracking-tight text-text-main">
          Wasserhaushalt
        </h3>
        <p class="truncate text-xs text-text-muted">Tägliche Flüssigkeitszufuhr</p>
      </div>
    </div>
    <Badge variant="hydrate" class="text-[0.625rem] font-bold">{percentage}% Soll</Badge>
  </div>

  <!-- Physical Glass Container with Sine Wave -->
  <div
    class="relative mx-auto mb-3 h-[150px] w-[120px] overflow-hidden rounded-b-[16px] border-2 border-b-0 border-[rgba(2,132,199,0.35)] bg-[rgba(2,132,199,0.02)]"
  >
    <div
      class="absolute inset-x-0 bottom-0 bg-gradient-to-b from-[rgba(2,132,199,0.45)] to-[rgba(2,132,199,0.85)] transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]"
      style="height: {percentage}%;"
    >
      <svg
        class="absolute -top-3 left-0 h-3.5 w-[200%] animate-[waveFlow_4s_linear_infinite]"
        viewBox="0 0 500 20"
        preserveAspectRatio="none"
      >
        <path d="M0,10 C150,20 350,0 500,10 L500,20 L0,20 Z" fill="rgba(2, 132, 199, 0.4)"></path>
      </svg>
    </div>
  </div>

  <div class="mb-3 text-center">
    <div class="font-mono text-[1.35rem] font-bold text-text-main tabular-nums">
      {currentMl.toLocaleString('de-DE')} / {targetMl.toLocaleString('de-DE')} ml
    </div>
  </div>

  <div class="grid grid-cols-2 gap-2">
    <button
      type="button"
      class="cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-3 py-2 text-xs font-bold text-text-main transition-colors hover:bg-surface-100"
      onclick={() => addAmount(250)}
    >
      + 250 ml
    </button>
    <button
      type="button"
      class="cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-3 py-2 text-xs font-bold text-text-main transition-colors hover:bg-surface-100"
      onclick={() => addAmount(500)}
    >
      + 500 ml
    </button>
  </div>
</div>

<style>
  @keyframes waveFlow {
    0% {
      transform: translateX(0);
    }
    100% {
      transform: translateX(-50%);
    }
  }
</style>
