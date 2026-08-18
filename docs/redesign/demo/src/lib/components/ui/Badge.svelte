<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    variant = 'default',
    class: className = '',
    children
  } = $props<{
    variant?: 'default' | 'success' | 'vital' | 'hydrate' | 'fasting' | 'activity';
    class?: string;
    children?: Snippet;
  }>();

  const variantStyles = {
    default: 'bg-[var(--bg-surface-100)] text-[var(--text-muted)]',
    success: 'bg-[var(--color-success-soft)] text-[var(--color-success)]',
    vital: 'bg-[var(--color-vital-soft)] text-[var(--color-vital)]',
    hydrate: 'bg-[var(--color-hydrate-soft)] text-[var(--color-hydrate)]',
    fasting: 'bg-[var(--color-fasting-soft)] text-[var(--color-fasting)]',
    activity: 'bg-[var(--color-activity-soft)] text-[var(--color-activity)]'
  };
</script>

<span
  class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[0.6875rem] font-bold tracking-tight {variantStyles[variant]} {className}"
>
  {@render children?.()}
</span>
