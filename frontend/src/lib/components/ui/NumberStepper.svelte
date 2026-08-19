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
      <span class="font-bold text-text-muted select-none">{label}</span>
      {#if unit}
        <span class="text-[0.625rem] font-bold text-text-soft tabular-nums">{unit}</span>
      {/if}
    </div>
  {/if}

  <!-- Main Stepper Row -->
  <div
    class="flex items-center justify-between gap-2 rounded-2xl border border-border-subtle bg-surface-50 p-1.5"
  >
    <button
      type="button"
      onclick={() => decrement(step)}
      disabled={disabled || value <= min}
      class="flex h-10 w-10 cursor-pointer items-center justify-center rounded-xl border border-border-subtle bg-surface-0 text-base font-extrabold text-text-main shadow-xs transition-all select-none hover:bg-surface-100 active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
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
        class="w-full bg-transparent text-center text-lg font-extrabold text-text-main tabular-nums outline-none select-all sm:text-xl"
      />
      {#if unit}
        <span class="-mt-1 block text-[0.625rem] font-bold text-text-soft">{unit}</span>
      {/if}
    </div>

    <button
      type="button"
      onclick={() => increment(step)}
      disabled={disabled || value >= max}
      class="flex h-10 w-10 cursor-pointer items-center justify-center rounded-xl border border-border-subtle bg-surface-0 text-base font-extrabold text-text-main shadow-xs transition-all select-none hover:bg-surface-100 active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
      aria-label="Erhöhen"
    >
      +
    </button>
  </div>

  <!-- Optional Quick Stepper Buttons -->
  {#if quickSteps.length > 0}
    <div class="no-scrollbar flex gap-1.5 overflow-x-auto">
      {#each quickSteps as qs}
        <button
          type="button"
          onclick={() => (qs > 0 ? increment(qs) : decrement(Math.abs(qs)))}
          {disabled}
          class="flex-1 cursor-pointer rounded-xl border border-border-subtle bg-surface-0 px-2 py-1 text-center text-[0.6875rem] font-bold whitespace-nowrap text-text-muted tabular-nums transition-all hover:border-border-strong hover:text-text-main active:scale-95"
        >
          {qs > 0 ? `+${qs}` : `${qs}`}
        </button>
      {/each}
    </div>
  {/if}
</div>
