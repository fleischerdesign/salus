<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    systolic = 118,
    diastolic = 76,
    bpm = 64
  } = $props<{
    systolic?: number;
    diastolic?: number;
    bpm?: number;
  }>();
</script>

<div
  class="flex flex-col justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-[18px] shadow-[var(--shadow-card)]"
>
  <div class="mb-2 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
      <Icon name="vitals" class="text-[var(--color-vital)]" />
      <span>Kardiovaskulär</span>
    </div>
    <Badge variant="success">ESC: Optimal</Badge>
  </div>

  <div class="flex items-baseline justify-between">
    <div class="font-mono text-[1.6rem] font-bold text-[var(--text-main)] tabular-nums">
      {systolic} / {diastolic}
      <span class="font-sans text-[0.8rem] font-normal text-[var(--text-muted)]">mmHg</span>
    </div>
    <div class="font-mono text-base font-semibold text-[var(--color-vital)]">
      {bpm} bpm
    </div>
  </div>

  <!-- 4-Zone ESC/EAS Clinical Gauge -->
  <div class="my-2">
    <div class="mb-1 flex justify-between font-mono text-[0.6875rem] text-[var(--text-muted)]">
      <span>&lt; 120 (Optimal)</span>
      <span>120–139</span>
      <span>&ge; 140</span>
    </div>
    <div class="flex h-2 gap-0.5 overflow-hidden rounded-full">
      <div class="flex-[2] bg-[var(--color-success)]" title="Optimal"></div>
      <div class="flex-[1.5] bg-[var(--color-circadian)]" title="Erhöht"></div>
      <div class="flex-[1.5] bg-[var(--color-vital)]" title="Hypertonie"></div>
    </div>
    <div class="mt-0.5 flex justify-start pl-[20%]">
      <div
        class="h-0 w-0 border-r-[4px] border-b-[6px] border-l-[4px] border-r-transparent border-b-[var(--color-success)] border-l-transparent"
      ></div>
    </div>
  </div>

  <div
    class="mt-4 rounded-md bg-[var(--bg-surface-50)] p-[8px_10px] text-xs text-[var(--text-muted)]"
  >
    7-Tage EMA: 119/77 mmHg • Optimal
  </div>
</div>
