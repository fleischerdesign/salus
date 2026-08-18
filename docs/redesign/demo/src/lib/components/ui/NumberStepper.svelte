<script lang="ts">
  let {
    value = $bindable(0),
    label = '',
    unit = '',
    min = 0,
    max = 9999,
    step = 1,
    precision = 1,
    quickSteps = [],
    disabled = false,
    onchange
  } = $props<{
    value?: number;
    label?: string;
    unit?: string;
    min?: number;
    max?: number;
    step?: number;
    precision?: number;
    quickSteps?: number[];
    disabled?: boolean;
    onchange?: (val: number) => void;
  }>();

  function increment(amount: number) {
    if (disabled) return;
    const next = Math.min(max, Math.round((value + amount) * 100) / 100);
    value = next;
    onchange?.(value);
  }

  function decrement(amount: number) {
    if (disabled) return;
    const next = Math.max(min, Math.round((value - amount) * 100) / 100);
    value = next;
    onchange?.(value);
  }

  function handleDirectInput(e: Event) {
    const target = e.target as HTMLInputElement;
    const parsed = parseFloat(target.value);
    if (!isNaN(parsed)) {
      value = Math.max(min, Math.min(max, parsed));
      onchange?.(value);
    }
  }
</script>

<div class="w-full space-y-2 text-xs">
  {#if label}
    <div class="flex items-center justify-between">
      <span class="font-bold text-[var(--text-muted)] select-none">{label}</span>
      {#if unit}
        <span class="text-[0.625rem] text-[var(--text-soft)] font-bold tabular-nums">{unit}</span>
      {/if}
    </div>
  {/if}

  <!-- Main Stepper Row -->
  <div class="flex items-center justify-between gap-2 p-1.5 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)]">
    <button
      type="button"
      onclick={() => decrement(step)}
      disabled={disabled || value <= min}
      class="w-10 h-10 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-base font-extrabold text-[var(--text-main)] hover:bg-[var(--bg-surface-100)] active:scale-95 transition-all flex items-center justify-center cursor-pointer shadow-xs disabled:opacity-40 disabled:cursor-not-allowed select-none"
      aria-label="Verringern"
    >
      &minus;
    </button>

    <div class="flex-1 text-center">
      <input
        type="number"
        {min}
        {max}
        {step}
        {disabled}
        value={Number(value.toFixed(precision))}
        oninput={handleDirectInput}
        class="w-full bg-transparent text-center font-extrabold text-lg sm:text-xl text-[var(--text-main)] tabular-nums outline-none select-all"
      />
      {#if unit}
        <span class="text-[0.625rem] font-bold text-[var(--text-soft)] block -mt-1">{unit}</span>
      {/if}
    </div>

    <button
      type="button"
      onclick={() => increment(step)}
      disabled={disabled || value >= max}
      class="w-10 h-10 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-base font-extrabold text-[var(--text-main)] hover:bg-[var(--bg-surface-100)] active:scale-95 transition-all flex items-center justify-center cursor-pointer shadow-xs disabled:opacity-40 disabled:cursor-not-allowed select-none"
      aria-label="Erhöhen"
    >
      +
    </button>
  </div>

  <!-- Optional Quick Stepper Buttons -->
  {#if quickSteps.length > 0}
    <div class="flex gap-1.5 overflow-x-auto no-scrollbar">
      {#each quickSteps as qs}
        <button
          type="button"
          onclick={() => qs > 0 ? increment(qs) : decrement(Math.abs(qs))}
          disabled={disabled}
          class="flex-1 py-1 px-2 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[0.6875rem] font-bold text-[var(--text-muted)] hover:text-[var(--text-main)] hover:border-[var(--border-strong)] transition-all cursor-pointer tabular-nums text-center whitespace-nowrap active:scale-95"
        >
          {qs > 0 ? `+${qs}` : `${qs}`}
        </button>
      {/each}
    </div>
  {/if}
</div>
