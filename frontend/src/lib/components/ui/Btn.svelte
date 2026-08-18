<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';

  const variantClasses = {
    primary: 'bg-[var(--color-primary)] text-white hover:opacity-90 active:scale-95 shadow-sm',
    secondary:
      'border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-main)] hover:bg-[var(--bg-surface-100)] active:scale-95',
    ghost: 'bg-transparent text-[var(--text-main)] hover:bg-[var(--bg-surface-50)] active:scale-95',
    danger:
      'bg-rose-500/10 text-rose-500 border border-rose-500/20 hover:bg-rose-500/20 active:scale-95'
  };
  const sizeClasses = {
    sm: 'h-8 px-3 text-xs gap-1.5 rounded-xl',
    md: 'h-10 px-4 text-sm gap-2 rounded-xl',
    lg: 'h-12 px-5 text-base gap-2.5 rounded-2xl'
  };

  interface Props {
    variant?: keyof typeof variantClasses;
    size?: keyof typeof sizeClasses;
    type?: 'button' | 'submit' | 'reset';
    disabled?: boolean;
    loading?: boolean;
    fullWidth?: boolean;
    href?: string;
    onclick?: () => void;
    children?: Snippet;
    class?: string;
  }

  let {
    variant = 'secondary',
    size = 'md',
    type = 'button',
    disabled = false,
    loading = false,
    fullWidth = false,
    href,
    onclick,
    children,
    class: extraClass = ''
  }: Props = $props();

  let classes = $derived(
    'relative inline-flex items-center justify-center font-semibold leading-none no-underline transition-all duration-micro select-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-primary)] disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.98] cursor-pointer ' +
      (fullWidth ? 'w-full ' : '') +
      variantClasses[variant] +
      ' ' +
      sizeClasses[size] +
      ' ' +
      extraClass
  );
</script>

{#if href}
  <a {href} class={classes}>
    {#if loading}<Icon name="progress-activity" class="animate-spin" />{/if}
    {@render children?.()}
  </a>
{:else}
  <button {type} {disabled} {onclick} class={classes} aria-busy={loading}>
    {#if loading}
      <Icon name="progress-activity" class="absolute animate-spin" />
    {/if}
    <span class={loading ? 'invisible' : 'contents'}>{@render children?.()}</span>
  </button>
{/if}
