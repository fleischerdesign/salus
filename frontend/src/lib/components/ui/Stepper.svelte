<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
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
    min = -Infinity,
    max = Infinity,
    step = 1,
    value = $bindable(0),
    class: extraClass = ''
  }: Props = $props();

  function decrement() {
    const next = value - step;
    if (next >= min) {
      value = next;
    }
  }

  function increment() {
    const next = value + step;
    if (next <= max) {
      value = next;
    }
  }
</script>

<div class="flex flex-col gap-1.5 {extraClass}">
  {#if label}
    <label for={name} class="text-sm font-medium text-surface-700">{label}</label>
  {/if}
  <div class="flex items-center">
    <button
      type="button"
      class="inline-flex h-9 w-9 items-center justify-center rounded-md border border-surface-300 bg-white text-surface-600 hover:bg-surface-100 disabled:cursor-not-allowed disabled:opacity-50"
      disabled={value <= min}
      onclick={decrement}
    >
      <Icon name="remove" size="sm" />
    </button>
    <input type="hidden" {name} {value} />
    <span class="min-w-[3rem] px-3 text-center text-sm font-medium text-surface-900 tabular-nums">
      {value}
    </span>
    <button
      type="button"
      class="inline-flex h-9 w-9 items-center justify-center rounded-md border border-surface-300 bg-white text-surface-600 hover:bg-surface-100 disabled:cursor-not-allowed disabled:opacity-50"
      disabled={value >= max}
      onclick={increment}
    >
      <Icon name="add" size="sm" />
    </button>
  </div>
</div>
