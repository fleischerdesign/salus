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
    elevated: 'shadow-sm',
    outlined: '',
    flat: 'bg-surface-100 border-transparent'
  };
</script>

<div
  class="bg-surface-0 rounded-md border {variantStyles[variant]} {disabled
    ? 'border-surface-200/80 opacity-60'
    : 'border-surface-200'} {hoverable
    ? disabled
      ? 'duration-micro hover:border-surface-300 transition-all hover:opacity-90'
      : 'duration-micro hover:border-surface-300 transition-all hover:shadow-md'
    : ''} {extraClass}"
>
  {#if header}
    <div class="{border ? 'border-surface-100 border-b' : ''} px-6 py-4">
      {@render header()}
    </div>
  {:else if title}
    <div class="border-surface-200 flex items-center gap-3 border-b px-6 py-3">
      <h3 class="text-xs font-semibold {disabled ? 'text-surface-600' : 'text-surface-900'}">
        {title}
      </h3>
    </div>
  {/if}
  <div class={padding ? 'p-6' : ''}>
    {#if loading}
      {#if skeleton}
        {@render skeleton()}
      {:else}
        <div class="space-y-3">
          <div class="bg-surface-100 h-5 w-1/3 animate-pulse rounded"></div>
          <div class="bg-surface-100 h-4 w-3/4 animate-pulse rounded"></div>
          <div class="bg-surface-100 h-4 w-1/2 animate-pulse rounded"></div>
        </div>
      {/if}
    {:else}
      {@render children?.()}
    {/if}
  </div>
</div>
