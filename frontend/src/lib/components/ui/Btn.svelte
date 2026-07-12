<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';
  const variantClasses = {
    primary: 'bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700',
    secondary:
      'border border-primary-500 bg-transparent text-primary-600 hover:bg-primary-50 active:bg-primary-100',
    ghost: 'bg-transparent text-primary-600 hover:bg-primary-50 active:bg-primary-100',
    danger: 'bg-error-50 text-error-700 hover:bg-error-100 active:bg-error-200'
  };
  const sizeClasses = {
    sm: 'h-8 px-3 text-xs gap-1.5',
    md: 'h-11 px-5 text-sm gap-2'
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
    'relative inline-flex items-center justify-center rounded-md font-semibold leading-none no-underline transition-all duration-150 select-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98] ' +
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
