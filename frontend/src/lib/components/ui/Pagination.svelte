<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    page?: number;
    total?: number;
    perPage?: number;
    itemsLabel?: string;
    onpage?: (page: number) => void;
    class?: string;
  }

  let {
    page = 1,
    total = 0,
    perPage = 20,
    itemsLabel = 'items',
    onpage,
    class: extraClass = ''
  }: Props = $props();

  let totalPages = $derived(Math.max(1, Math.ceil(total / perPage)));

  let pages = $derived.by(() => {
    const result: (number | '...')[] = [];
    const window = 2;
    for (let p = 1; p <= totalPages; p++) {
      if (
        p === 1 ||
        p === totalPages ||
        (p >= page - window && p <= page + window)
      ) {
        result.push(p);
      } else if (result[result.length - 1] === '...') {
        continue;
      } else {
        result.push('...');
      }
    }
    return result;
  });

  function go(p: number) {
    if (p < 1 || p > totalPages || p === page) return;
    onpage?.(p);
  }
</script>

{#if totalPages > 1}
  <nav class="flex flex-wrap items-center justify-center gap-1 {extraClass}" aria-label="Pagination">
    <button
      class="flex h-10 w-10 items-center justify-center rounded-md text-surface-500 transition-colors duration-150 hover:bg-surface-100 disabled:cursor-not-allowed disabled:opacity-50"
      disabled={page <= 1}
      onclick={() => go(page - 1)}
      aria-label="Previous page"
    >
      <Icon name="chevron-left" />
    </button>

    {#each pages as p}
      {#if p === '...'}
        <span class="flex h-10 w-10 items-center justify-center text-sm text-surface-400">…</span>
      {:else}
        <button
          class="flex h-10 min-w-10 items-center justify-center rounded-md px-2 text-sm font-semibold transition-colors duration-150 {page === p ? 'bg-primary-50 text-primary-600' : 'text-surface-600 hover:bg-surface-100'}"
          onclick={() => go(p)}
          aria-current={page === p ? 'page' : undefined}
        >
          {p}
        </button>
      {/if}
    {/each}

    <button
      class="flex h-10 w-10 items-center justify-center rounded-md text-surface-500 transition-colors duration-150 hover:bg-surface-100 disabled:cursor-not-allowed disabled:opacity-50"
      disabled={page >= totalPages}
      onclick={() => go(page + 1)}
      aria-label="Next page"
    >
      <Icon name="chevron-right" />
    </button>

    {#if total > 0}
      <span class="ml-3 text-sm text-surface-500">{total.toLocaleString()} {itemsLabel}</span>
    {/if}
  </nav>
{/if}
