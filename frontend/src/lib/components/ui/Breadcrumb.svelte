<script lang="ts">
  interface Props {
    items: { href: string; label: string }[];
    class?: string;
  }

  let { items, class: extraClass = '' }: Props = $props();
</script>

<nav aria-label="Breadcrumb" class="py-4 {extraClass}">
  <ol class="flex flex-wrap items-center gap-0">
    {#each items as item, index}
      <li class="flex items-center">
        {#if index < items.length - 1}
          <a href={item.href} class="text-sm text-surface-500 no-underline transition-colors duration-150 hover:text-primary-600">
            {item.label}
          </a>
          <span class="mx-2 text-surface-400 select-none">/</span>
        {:else}
          <span class="text-sm font-semibold text-surface-900" aria-current="page">{item.label}</span>
        {/if}
      </li>
    {/each}
  </ol>
</nav>
