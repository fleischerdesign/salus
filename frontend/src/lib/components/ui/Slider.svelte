<script lang="ts">
  interface Props {
    name: string;
    label?: string;
    min?: number;
    max?: number;
    step?: number;
    value?: number;
    class?: string;
  }

  let {
    name,
    label,
    min = 0,
    max = 100,
    step = 1,
    value = $bindable(0),
    class: extraClass = ''
  }: Props = $props();
</script>

<div class="flex flex-col gap-1.5 {extraClass}">
  {#if label}
    <div class="flex items-center justify-between">
      <label for={name} class="text-sm font-medium text-surface-700">{label}</label>
      <span class="text-sm text-surface-500 tabular-nums">{value}</span>
    </div>
  {/if}
  <input
    type="range"
    {name}
    id={name}
    bind:value
    {min}
    {max}
    {step}
    class="h-2 w-full cursor-pointer appearance-none rounded-full bg-surface-200 accent-primary-600 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary-600 [&::-webkit-slider-thumb]:shadow-sm"
  />
</div>
