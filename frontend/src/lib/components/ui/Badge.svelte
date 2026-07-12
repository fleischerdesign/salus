<script lang="ts">
  import { type Snippet } from 'svelte';

  interface Props {
    variant?: 'default' | 'primary' | 'success' | 'warning' | 'error';
    children?: Snippet;
    class?: string;
  }

  let {
    variant = 'default',
    children,
    class: extraClass = ''
  }: Props = $props();

  const variantClasses = {
    default: 'bg-surface-100 text-surface-700',
    primary: 'bg-primary-50 text-primary-700',
    success: 'bg-success-100 text-success-700',
    warning: 'bg-warning-100 text-warning-700',
    error: 'bg-error-100 text-error-700'
  };
</script>

<span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium {variantClasses[variant]} {extraClass}">
  {@render children?.()}
</span>
