<script lang="ts">
  interface Option {
    value: string;
    label: string;
    icon?: string;
  }

  interface Props {
    options: Option[];
    value?: string;
    size?: 'sm' | 'md';
    class?: string;
  }

  let {
    options,
    value = $bindable(''),
    size = 'md',
    class: extraClass = ''
  }: Props = $props();

  let sizeClasses = $derived(
    size === 'sm'
      ? 'px-2.5 py-1 text-xs'
      : 'px-3 py-1.5 text-sm'
  );
</script>

<div class="inline-flex gap-1 rounded-lg bg-surface-100 p-1 {extraClass}">
  {#each options as opt}
    <button
      type="button"
      class="flex items-center gap-1.5 rounded-md font-medium transition-colors duration-150 {sizeClasses} {value === opt.value ? 'bg-surface-0 text-surface-900 shadow-sm' : 'text-surface-500 hover:text-surface-700'}"
      onclick={() => (value = opt.value)}
      aria-pressed={value === opt.value}
    >
      {opt.label}
    </button>
  {/each}
</div>
