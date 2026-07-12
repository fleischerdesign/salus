<script lang="ts">
  import { type Snippet } from 'svelte';

  interface Props {
    label: string;
    error?: string;
    required?: boolean;
    children: Snippet;
    class?: string;
  }

  let { label, error, required = false, children, class: extraClass = '' }: Props = $props();
</script>

<div class="flex flex-col gap-1.5 {extraClass}">
  <span class="text-sm font-medium text-surface-700">
    {label}
    {#if required}
      <span class="ml-0.5 text-error-500">*</span>
    {/if}
  </span>
  {@render children?.()}
  {#if error}
    <p class="text-sm text-error-500">{error}</p>
  {/if}
</div>
