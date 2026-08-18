<script lang="ts">
  import Icon from './Icon.svelte';

  export interface BreadcrumbItem {
    label: string;
    onclick?: () => void;
    active?: boolean;
  }

  let { items = [] } = $props<{
    items: BreadcrumbItem[];
  }>();
</script>

{#if items.length > 0}
  <nav class="flex items-center gap-1.5 text-xs text-[var(--text-muted)] font-mono mb-4 flex-wrap" aria-label="Breadcrumb">
    {#each items as item, i}
      {#if i > 0}
        <Icon name="chevron-down" size={10} class="-rotate-90 text-[var(--text-soft)] shrink-0" />
      {/if}
      {#if item.onclick && !item.active}
        <button
          type="button"
          onclick={item.onclick}
          class="hover:text-[var(--color-primary)] transition-colors cursor-pointer font-medium"
        >
          {item.label}
        </button>
      {:else}
        <span class="{item.active ? 'text-[var(--text-main)] font-bold' : ''}">
          {item.label}
        </span>
      {/if}
    {/each}
  </nav>
{/if}
