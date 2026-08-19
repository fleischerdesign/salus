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
    primary: 'accent-primary',
    activity: 'accent-activity',
    vital: 'accent-vital',
    circadian: 'accent-circadian',
    hydrate: 'accent-hydrate'
  };

  let accentClass = $derived(colorMap[color as keyof typeof colorMap] ?? colorMap.primary);
</script>

<div class="w-full space-y-1.5 text-xs">
  <div class="flex items-center justify-between">
    {#if label}
      <label for={id} class="font-bold text-text-muted select-none">
        {label}
      </label>
    {/if}
    <div
      class="rounded-lg border border-border-subtle bg-surface-100 px-2 py-0.5 text-[0.6875rem] font-extrabold text-text-main tabular-nums"
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
      class="h-2 w-full cursor-pointer appearance-none rounded-lg bg-surface-100 {accentClass} {disabled
        ? 'cursor-not-allowed opacity-50'
        : ''}"
    />
  </div>

  <div class="flex justify-between text-[0.625rem] font-bold text-text-soft tabular-nums">
    <span>{min} {unit}</span>
    <span>{max} {unit}</span>
  </div>
</div>
