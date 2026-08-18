<script lang="ts">
  let {
    value = $bindable(50),
    label = '',
    min = 0,
    max = 100,
    step = 1,
    unit = '',
    disabled = false,
    color = 'primary',
    id = `slider_${Math.random().toString(36).slice(2, 7)}`,
    onchange
  } = $props<{
    value?: number;
    label?: string;
    min?: number;
    max?: number;
    step?: number;
    unit?: string;
    disabled?: boolean;
    color?: 'primary' | 'activity' | 'vital' | 'circadian' | 'hydrate';
    id?: string;
    onchange?: (val: number) => void;
  }>();

  function handleInput(e: Event) {
    const val = Number((e.target as HTMLInputElement).value);
    value = val;
    onchange?.(val);
  }

  const colorMap: Record<'primary' | 'activity' | 'vital' | 'circadian' | 'hydrate', string> = {
    primary: 'accent-[var(--color-primary)]',
    activity: 'accent-[var(--color-activity)]',
    vital: 'accent-[var(--color-vital)]',
    circadian: 'accent-[var(--color-circadian)]',
    hydrate: 'accent-[var(--color-hydrate)]'
  };

  let accentClass = $derived(colorMap[color as keyof typeof colorMap] ?? colorMap.primary);
</script>

<div class="w-full space-y-1.5 text-xs">
  <div class="flex items-center justify-between">
    {#if label}
      <label for={id} class="font-bold text-[var(--text-muted)] select-none">
        {label}
      </label>
    {/if}
    <div
      class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-100)] px-2 py-0.5 text-[0.6875rem] font-extrabold text-[var(--text-main)] tabular-nums"
    >
      {value}
      {unit}
    </div>
  </div>

  <div class="relative flex items-center py-1">
    <input
      {id}
      type="range"
      {min}
      {max}
      {step}
      {value}
      {disabled}
      oninput={handleInput}
      class="h-2 w-full cursor-pointer appearance-none rounded-lg bg-[var(--bg-surface-100)] {accentClass} {disabled
        ? 'cursor-not-allowed opacity-50'
        : ''}"
    />
  </div>

  <div class="flex justify-between text-[0.625rem] font-bold text-[var(--text-soft)] tabular-nums">
    <span>{min} {unit}</span>
    <span>{max} {unit}</span>
  </div>
</div>
