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
      <label for={name} class="text-surface-700 text-sm font-medium">{label}</label>
      <span class="text-surface-500 text-sm tabular-nums">{value}</span>
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
    class="bg-surface-200 accent-primary-600 [&::-webkit-slider-thumb]:bg-primary-600 h-2 w-full cursor-pointer appearance-none rounded-full [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:shadow-sm"
  />
</div>
