<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';

  type Variant = 'primary' | 'danger' | 'secondary' | 'ghost' | 'ghost-danger';

  interface Props {
    icon?: string;
    variant?: Variant;
    loading?: boolean;
    disabled?: boolean;
    onclick?: () => void;
    children?: Snippet;
  }

  let {
    icon,
    variant = 'primary',
    loading = false,
    disabled = false,
    onclick,
    children
  }: Props = $props();

  const variantClasses: Record<Variant, string> = {
    primary: 'bg-primary-500 text-on-primary hover:bg-primary-600 active:bg-primary-700',
    danger: 'bg-error-500 text-on-error hover:bg-error-600 active:bg-error-700',
    secondary: 'bg-surface-100 text-surface-700 hover:bg-surface-200',
    ghost: 'text-surface-600 hover:bg-surface-100 hover:text-surface-900',
    'ghost-danger': 'text-error-600 hover:bg-error-50 hover:text-error-700'
  };
</script>

<button
  type="button"
  {disabled}
  {onclick}
  class="duration-micro flex h-full items-center justify-center gap-2 px-6 text-sm font-semibold whitespace-nowrap transition-colors disabled:cursor-not-allowed disabled:opacity-50 {variantClasses[
    variant
  ]}"
>
  {#if loading}
    <Icon name="progress-activity" class="animate-spin" />
  {:else if icon}
    <Icon name={icon} size="sm" />
  {/if}
  {#if children}
    <span>{@render children()}</span>
  {/if}
</button>
