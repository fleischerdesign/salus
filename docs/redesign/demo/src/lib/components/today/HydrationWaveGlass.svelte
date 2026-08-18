<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  let { currentMl = $bindable(2250), targetMl = 3000 } = $props<{
    currentMl?: number;
    targetMl?: number;
  }>();

  let percentage = $derived(Math.min(100, Math.round((currentMl / targetMl) * 100)));

  function addAmount(ml: number) {
    currentMl = Math.min(targetMl, currentMl + ml);
  }
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-[18px] shadow-[var(--shadow-card)] flex flex-col justify-between">
  <div class="flex items-center justify-between mb-3">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="droplet" class="text-[var(--color-hydrate)]" />
      <span>Wasserhaushalt</span>
    </div>
    <Badge variant="hydrate">{percentage}% Soll</Badge>
  </div>

  <!-- Physical Glass Container with Sine Wave -->
  <div class="relative w-[120px] h-[150px] border-2 border-b-0 border-[rgba(2,132,199,0.35)] rounded-b-[16px] bg-[rgba(2,132,199,0.02)] overflow-hidden mx-auto mb-3">
    <div
      class="absolute bottom-0 inset-x-0 bg-gradient-to-b from-[rgba(2,132,199,0.45)] to-[rgba(2,132,199,0.85)] transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]"
      style="height: {percentage}%;"
    >
      <svg class="absolute -top-3 left-0 w-[200%] h-3.5 animate-[waveFlow_4s_linear_infinite]" viewBox="0 0 500 20" preserveAspectRatio="none">
        <path d="M0,10 C150,20 350,0 500,10 L500,20 L0,20 Z" fill="rgba(2, 132, 199, 0.4)"></path>
      </svg>
    </div>
  </div>

  <div class="text-center mb-3">
    <div class="text-[1.35rem] font-bold font-mono tabular-nums text-[var(--text-main)]">
      {currentMl.toLocaleString('de-DE')} / {targetMl.toLocaleString('de-DE')} ml
    </div>
  </div>

  <div class="grid grid-cols-2 gap-2">
    <button class="btn btn-secondary" onclick={() => addAmount(250)}>+ 250 ml</button>
    <button class="btn btn-secondary" onclick={() => addAmount(500)}>+ 500 ml</button>
  </div>
</div>

<style>
  @keyframes waveFlow {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
  }
</style>
