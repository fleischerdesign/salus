<script lang="ts">
  import { type Snippet } from 'svelte';

  export type BadgeVariant =
    | 'default'
    | 'primary'
    | 'success'
    | 'warning'
    | 'error'
    | 'vital'
    | 'activity'
    | 'hydrate'
    | 'fasting'
    | 'circadian';

  interface Props {
    variant?: BadgeVariant;
    children?: Snippet;
    class?: string;
  }

  let { variant = 'default', children, class: extraClass = '' }: Props = $props();

  const variantClasses: Record<BadgeVariant, string> = {
    default:
      'bg-[var(--bg-surface-100)] text-[var(--text-muted)] border border-[var(--border-subtle)]',
    primary: 'bg-[var(--color-primary-soft)] text-[var(--color-primary)] font-bold',
    success: 'bg-[var(--color-success-soft)] text-[var(--color-success)] font-bold',
    warning: 'bg-amber-500/10 text-amber-600 font-bold',
    error: 'bg-rose-500/10 text-rose-600 font-bold',
    vital: 'bg-[var(--color-vital-soft)] text-[var(--color-vital)] font-bold',
    activity: 'bg-[var(--color-activity-soft)] text-[var(--color-activity)] font-bold',
    hydrate: 'bg-[var(--color-hydrate-soft)] text-[var(--color-hydrate)] font-bold',
    fasting: 'bg-[var(--color-fasting-soft)] text-[var(--color-fasting)] font-bold',
    circadian: 'bg-[var(--color-circadian-soft)] text-[var(--color-circadian)] font-bold'
  };
</script>

<span
  class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold tabular-nums select-none {variantClasses[
    variant
  ]} {extraClass}"
>
  {@render children?.()}
</span>
