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

  let { options, value = $bindable(''), size = 'md', class: extraClass = '' }: Props = $props();

  let sizeClasses = $derived(size === 'sm' ? 'px-2.5 py-1 text-xs' : 'px-3 py-1.5 text-sm');
</script>

<div
  class="inline-flex gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-1 {extraClass}"
>
  {#each options as opt}
    <button
      type="button"
      class="flex cursor-pointer items-center gap-1.5 rounded-lg font-bold transition-all {sizeClasses} {value ===
      opt.value
        ? 'bg-[var(--color-primary)] text-white shadow-xs'
        : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      onclick={() => (value = opt.value)}
      aria-pressed={value === opt.value}
    >
      {opt.label}
    </button>
  {/each}
</div>
