<script lang="ts">
  import { type Snippet } from 'svelte';

  interface Props {
    title?: string;
    header?: Snippet;
    padding?: boolean;
    variant?: 'elevated' | 'outlined' | 'flat';
    hoverable?: boolean;
    disabled?: boolean;
    loading?: boolean;
    skeleton?: Snippet;
    children?: Snippet;
    class?: string;
    border?: boolean;
  }

  let {
    title,
    header,
    padding = true,
    variant = 'outlined',
    hoverable = false,
    disabled = false,
    loading = false,
    skeleton,
    children,
    class: extraClass = '',
    border = true
  }: Props = $props();

  const variantStyles: Record<string, string> = {
    elevated: 'shadow-xs',
    outlined: '',
    flat: 'bg-surface-50 border-transparent'
  };
</script>

<div
  class="rounded-2xl border bg-surface-0 {variantStyles[variant]} {disabled
    ? 'border-border-subtle/60 opacity-60'
    : 'border-border-subtle'} {hoverable
    ? disabled
      ? 'transition-all hover:border-border-strong hover:opacity-90'
      : 'transition-all hover:border-border-strong hover:shadow-xs'
    : ''} {extraClass}"
>
  {#if header}
    <div class="{border ? 'border-b border-border-subtle' : ''} px-5 py-3.5">
      {@render header()}
    </div>
  {:else if title}
    <div class="flex items-center gap-3 border-b border-border-subtle px-5 py-3">
      <h3 class="text-xs font-semibold {disabled ? 'text-text-muted' : 'text-text-main'}">
        {title}
      </h3>
    </div>
  {/if}
  <div class={padding ? 'p-5' : ''}>
    {#if loading}
      {#if skeleton}
        {@render skeleton()}
      {:else}
        <div class="space-y-3">
          <div class="h-5 w-1/3 animate-pulse rounded bg-surface-100"></div>
          <div class="h-4 w-3/4 animate-pulse rounded bg-surface-100"></div>
          <div class="h-4 w-1/2 animate-pulse rounded bg-surface-100"></div>
        </div>
      {/if}
    {:else}
      {@render children?.()}
    {/if}
  </div>
</div>
