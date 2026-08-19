<script lang="ts">
  export interface BreadcrumbItem {
    label: string;
    href?: string;
    onclick?: () => void;
    active?: boolean;
  }

  interface Props {
    items: BreadcrumbItem[];
    class?: string;
  }

  let { items, class: extraClass = '' }: Props = $props();
</script>

<nav aria-label="Breadcrumb" class="py-2 {extraClass}">
  <ol class="flex flex-wrap items-center gap-1.5 text-xs font-semibold">
    {#each items as item, index}
      <li class="flex items-center gap-1.5">
        {#if index < items.length - 1 && !item.active}
          {#if item.onclick}
            <button
              type="button"
              onclick={item.onclick}
              class="cursor-pointer text-text-muted transition-colors hover:text-primary"
            >
              {item.label}
            </button>
          {:else if item.href}
            <a href={item.href} class="text-text-muted transition-colors hover:text-primary">
              {item.label}
            </a>
          {:else}
            <span class="text-text-muted">{item.label}</span>
          {/if}
          <span class="text-border-strong select-none">/</span>
        {:else}
          <span class="font-bold text-text-main" aria-current="page">
            {item.label}
          </span>
        {/if}
      </li>
    {/each}
  </ol>
</nav>
