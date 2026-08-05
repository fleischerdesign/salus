<script lang="ts">
  import { type Snippet } from 'svelte';

  interface Props {
    title?: string;
    header?: Snippet;
    padding?: boolean;
    variant?: 'elevated' | 'outlined' | 'flat';
    hoverable?: boolean;
    disabled?: boolean;
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
  class="rounded-md border bg-surface-0 {variantStyles[variant]} {disabled
    ? 'border-surface-200/80 opacity-60'
    : 'border-surface-200'} {hoverable
    ? disabled
      ? 'duration-micro transition-all hover:border-surface-300 hover:opacity-90'
      : 'duration-micro transition-all hover:border-surface-300 hover:shadow-md'
    : ''} {extraClass}"
>
  {#if header}
    <div class="{border ? 'border-b border-surface-100' : ''} px-6 py-4">
      {@render header()}
    </div>
  {:else if title}
    <div class="flex items-center gap-3 border-b border-surface-200 px-6 py-3">
      <h3 class="text-[13px] font-semibold {disabled ? 'text-surface-600' : 'text-surface-900'}">
        {title}
      </h3>
    </div>
  {/if}
  <div class={padding ? 'p-6' : ''}>
    {@render children?.()}
  </div>
</div>
