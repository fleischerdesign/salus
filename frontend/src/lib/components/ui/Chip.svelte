<script lang="ts">
  import { type Snippet } from 'svelte';

  interface Props {
    variant?: 'neutral' | 'success' | 'warning' | 'error' | 'primary';
    dimissible?: boolean;
    children?: Snippet;
    onclick?: () => void;
    class?: string;
  }

  let { variant = 'neutral', dimissible = false, children, onclick, class: extraClass = '' }: Props = $props();

  const base = 'inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold transition-colors duration-150';

  const variantClasses: Record<string, string> = {
    neutral: 'bg-surface-100 text-surface-600',
    success: 'bg-success-50 text-success-700',
    warning: 'bg-warning-50 text-warning-700',
    error: 'bg-error-50 text-error-700',
    primary: 'bg-primary-50 text-primary-700',
  };
</script>

{#if onclick}
  <button class="{base} cursor-pointer hover:opacity-80 {variantClasses[variant]} {extraClass}" {onclick} type="button">
    {@render children?.()}
  </button>
{:else}
  <span class="{base} {variantClasses[variant]} {extraClass}">
    {@render children?.()}
    {#if dimissible}
      <button class="ml-0.5 rounded-full p-0.5 hover:bg-surface-200" onclick={onclick} type="button" aria-label="Dismiss">&times;</button>
    {/if}
  </span>
{/if}
