<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let selectedRange = $state<'7D' | '30D' | '90D' | '1Y'>('30D');

  const points = [
    { date: '16. Jul', val: 83.2, ema: 83.4 },
    { date: '21. Jul', val: 82.8, ema: 83.1 },
    { date: '26. Jul', val: 82.5, ema: 82.7 },
    { date: '31. Jul', val: 82.9, ema: 82.6 },
    { date: '05. Aug', val: 82.2, ema: 82.4 },
    { date: '10. Aug', val: 81.9, ema: 82.1 },
    { date: '14. Aug', val: 81.8, ema: 82.0 }
  ];
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
    <div>
      <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
        <Icon name="chart" class="text-[var(--color-primary)]" />
        <span>Körpergewicht und 7-Tage-EMA Glättung</span>
      </div>
      <p class="text-xs text-[var(--text-muted)] mt-0.5">Trend: ↘ -1.4 kg / Monat • Zielkorridor: 78–80 kg</p>
    </div>

    <!-- Time Range Selector -->
    <div class="flex gap-1 bg-[var(--bg-surface-50)] p-1 rounded-lg border border-[var(--border-subtle)]">
      {#each ['7D', '30D', '90D', '1Y'] as r}
        <button
          type="button"
          class="px-2.5 py-1 text-xs font-mono font-bold rounded cursor-pointer transition-all {selectedRange === r ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-xs' : 'text-[var(--text-muted)]'}"
          onclick={() => selectedRange = r as any}
        >
          {r}
        </button>
      {/each}
    </div>
  </div>

  <!-- Interactive SVG Spline Canvas -->
  <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 my-2">
    <svg class="w-full h-44" viewBox="0 0 700 160" preserveAspectRatio="none">
      <!-- Target Band 78-80kg -->
      <rect x="0" y="110" width="700" height="35" fill="var(--color-success-soft)" />
      <line x1="0" y1="110" x2="700" y2="110" stroke="var(--color-success)" stroke-width="1" stroke-dasharray="3 3" />
      <line x1="0" y1="145" x2="700" y2="145" stroke="var(--color-success)" stroke-width="1" stroke-dasharray="3 3" />

      <!-- Raw Measurements Points & Line -->
      <polyline
        points="30,40 130,55 230,70 330,50 430,90 530,105 650,110"
        fill="none"
        stroke="var(--border-strong)"
        stroke-width="1.5"
      />

      <!-- 7-Day EMA Smooth Curve -->
      <path
        d="M 30 35 Q 130 50 230 65 T 430 85 T 650 102"
        fill="none"
        stroke="var(--color-primary)"
        stroke-width="3"
      />

      <!-- Data Dots -->
      <circle cx="30" cy="40" r="3.5" fill="var(--color-primary)" />
      <circle cx="130" cy="55" r="3.5" fill="var(--color-primary)" />
      <circle cx="230" cy="70" r="3.5" fill="var(--color-primary)" />
      <circle cx="330" cy="50" r="3.5" fill="var(--color-primary)" />
      <circle cx="430" cy="90" r="3.5" fill="var(--color-primary)" />
      <circle cx="530" cy="105" r="3.5" fill="var(--color-primary)" />
      <circle cx="650" cy="110" r="5" fill="var(--color-primary)" stroke="#fff" stroke-width="2" />
    </svg>
    <div class="flex justify-between text-[0.6875rem] font-mono text-[var(--text-soft)] mt-1 px-1">
      <span>16. Jul (83.2 kg)</span>
      <span>Zielkorridor (78–80 kg)</span>
      <span>14. Aug (81.8 kg)</span>
    </div>
  </div>

  <div class="flex items-center justify-between text-xs text-[var(--text-muted)] pt-2">
    <span>Letzter Messwert: <strong class="text-[var(--text-main)] font-mono">81.8 kg</strong> (Heute)</span>
    <span class="font-mono text-[var(--color-primary)] font-bold">EMA: 82.0 kg</span>
  </div>
</div>
