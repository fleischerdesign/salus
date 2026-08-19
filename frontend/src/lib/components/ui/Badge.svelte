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
    default: 'bg-surface-100 text-text-muted border border-border-subtle',
    primary: 'bg-primary-soft text-primary font-bold',
    success: 'bg-success-soft text-success font-bold',
    warning: 'bg-amber-500/10 text-amber-600 font-bold',
    error: 'bg-rose-500/10 text-rose-600 font-bold',
    vital: 'bg-vital-soft text-vital font-bold',
    activity: 'bg-activity-soft text-activity font-bold',
    hydrate: 'bg-hydrate-soft text-hydrate font-bold',
    fasting: 'bg-fasting-soft text-fasting font-bold',
    circadian: 'bg-circadian-soft text-circadian font-bold'
  };
</script>

<span
  class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold tabular-nums select-none {variantClasses[
    variant
  ]} {extraClass}"
>
  {@render children?.()}
</span>
