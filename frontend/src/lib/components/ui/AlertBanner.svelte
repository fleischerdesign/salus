<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    variant?: 'error' | 'warning' | 'success';
    message?: string;
    children?: Snippet;
    class?: string;
  }

  let { variant = 'error', message, children, class: extraClass = '' }: Props = $props();

  const variantConfig: Record<string, { bg: string; border: string; text: string; icon: string }> = {
    error: { bg: 'bg-error-50', border: 'border-error-200', text: 'text-error-700', icon: 'error' },
    warning: { bg: 'bg-warning-50', border: 'border-warning-200', text: 'text-warning-700', icon: 'warning' },
    success: { bg: 'bg-success-50', border: 'border-success-200', text: 'text-success-700', icon: 'check-circle' }
  };

  let classes = $derived(
    `flex items-center gap-3 rounded-lg border p-3 ${variantConfig[variant].bg} ${variantConfig[variant].border} ${variantConfig[variant].text} ${extraClass}`
  );
</script>

<div class={classes} role="alert">
  <Icon name={variantConfig[variant].icon} size="sm" class="flex-shrink-0" />
  {#if children}
    <span class="text-sm">{@render children()}</span>
  {:else if message}
    <span class="text-sm">{message}</span>
  {/if}
</div>
