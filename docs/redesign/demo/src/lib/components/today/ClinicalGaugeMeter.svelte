<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let { systolic = 118, diastolic = 76, bpm = 64 } = $props<{
    systolic?: number;
    diastolic?: number;
    bpm?: number;
  }>();
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-[18px] shadow-[var(--shadow-card)] flex flex-col justify-between">
  <div class="flex items-center justify-between mb-2">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="vitals" class="text-[var(--color-vital)]" />
      <span>Kardiovaskulär</span>
    </div>
    <Badge variant="success">ESC: Optimal</Badge>
  </div>

  <div class="flex items-baseline justify-between">
    <div class="text-[1.6rem] font-bold font-mono tabular-nums text-[var(--text-main)]">
      {systolic} / {diastolic} <span class="text-[0.8rem] font-normal text-[var(--text-muted)] font-sans">mmHg</span>
    </div>
    <div class="text-base font-semibold font-mono text-[var(--color-vital)]">
      {bpm} bpm
    </div>
  </div>

  <!-- 4-Zone ESC/EAS Clinical Gauge -->
  <div class="my-2">
    <div class="flex justify-between text-[0.6875rem] font-mono text-[var(--text-muted)] mb-1">
      <span>&lt; 120 (Optimal)</span>
      <span>120–139</span>
      <span>&ge; 140</span>
    </div>
    <div class="h-2 rounded-full flex gap-0.5 overflow-hidden">
      <div class="flex-[2] bg-[var(--color-success)]" title="Optimal"></div>
      <div class="flex-[1.5] bg-[var(--color-circadian)]" title="Erhöht"></div>
      <div class="flex-[1.5] bg-[var(--color-vital)]" title="Hypertonie"></div>
    </div>
    <div class="flex justify-start pl-[20%] mt-0.5">
      <div class="w-0 h-0 border-l-[4px] border-r-[4px] border-b-[6px] border-l-transparent border-r-transparent border-b-[var(--color-success)]"></div>
    </div>
  </div>

  <div class="bg-[var(--bg-surface-50)] rounded-md p-[8px_10px] text-xs text-[var(--text-muted)] mt-4">
    7-Tage EMA: 119/77 mmHg • Optimal
  </div>
</div>
