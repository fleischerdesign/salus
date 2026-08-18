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

  let percent = $derived(Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100)));

  function handleInput(e: Event) {
    const val = Number((e.target as HTMLInputElement).value);
    value = val;
    onchange?.(val);
  }

  const colorMap = {
    primary: 'accent-[var(--color-primary)]',
    activity: 'accent-[var(--color-activity)]',
    vital: 'accent-[var(--color-vital)]',
    circadian: 'accent-[var(--color-circadian)]',
    hydrate: 'accent-[var(--color-hydrate)]'
  };
</script>

<div class="w-full space-y-1.5 text-xs">
  <div class="flex items-center justify-between">
    {#if label}
      <label for={id} class="font-bold text-[var(--text-muted)] select-none">
        {label}
      </label>
    {/if}
    <div class="px-2 py-0.5 rounded-lg bg-[var(--bg-surface-100)] border border-[var(--border-subtle)] font-extrabold text-[var(--text-main)] tabular-nums text-[0.6875rem]">
      {value} {unit}
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
      class="w-full h-2 rounded-lg bg-[var(--bg-surface-100)] appearance-none cursor-pointer {colorMap[color]} {disabled ? 'opacity-50 cursor-not-allowed' : ''}"
    />
  </div>

  <div class="flex justify-between text-[0.625rem] text-[var(--text-soft)] font-bold tabular-nums">
    <span>{min} {unit}</span>
    <span>{max} {unit}</span>
  </div>
</div>
