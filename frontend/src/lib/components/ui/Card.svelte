<script lang="ts">
  import { type Snippet } from 'svelte';

  interface Props {
    title?: string;
    header?: Snippet;
    padding?: boolean;
    variant?: 'elevated' | 'outlined' | 'flat';
    hoverable?: boolean;
    children?: Snippet;
    class?: string;
  }

  let {
    title,
    header,
    padding = true,
    variant = 'outlined',
    hoverable = false,
    children,
    class: extraClass = ''
  }: Props = $props();

  const variantStyles: Record<string, string> = {
    elevated: 'shadow-sm',
    outlined: '',
    flat: 'bg-surface-100 border-transparent'
  };
</script>

<div
  class="rounded-md border border-surface-200 bg-surface-0 {variantStyles[variant]} {hoverable
    ? 'duration-micro transition-all hover:border-surface-300 hover:shadow-md'
    : ''} {extraClass}"
>
  {#if header}
    <div class="border-b border-surface-100 px-6 py-4">
      {@render header()}
    </div>
  {:else if title}
    <div class="flex items-center gap-3 border-b border-surface-200 px-6 py-3">
      <h3 class="text-[13px] font-semibold text-surface-900">{title}</h3>
    </div>
  {/if}
  <div class={padding ? 'p-6' : ''}>
    {@render children?.()}
  </div>
</div>
