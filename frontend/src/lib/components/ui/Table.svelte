<script lang="ts">
  import { type Snippet } from 'svelte';

  interface Column {
    key: string;
    label: string;
  }

  interface Props {
    columns: Column[];
    rows: Record<string, unknown>[];
    loading?: boolean;
    emptyMessage?: string;
    actions?: Snippet<[row: Record<string, unknown>]>;
    class?: string;
  }

  let {
    columns,
    rows,
    loading = false,
    emptyMessage = 'No data',
    actions,
    class: extraClass = ''
  }: Props = $props();

  let hasActions = $derived(actions !== undefined);
  let colCount = $derived(columns.length + (hasActions ? 1 : 0));
</script>

<div class="overflow-x-auto rounded-lg border border-surface-200 {extraClass}">
  <table class="w-full table-auto">
    <thead>
      <tr class="bg-surface-50">
        {#each columns as col}
          <th class="border-b border-surface-200 px-4 py-2 text-left text-xs font-semibold uppercase text-surface-500">
            {col.label}
          </th>
        {/each}
        {#if hasActions}
          <th class="border-b border-surface-200 px-4 py-2 text-right text-xs font-semibold uppercase text-surface-500">
            Actions
          </th>
        {/if}
      </tr>
    </thead>
    <tbody>
      {#if loading}
        {#each Array(5) as _}
          <tr class="animate-pulse">
            {#each Array(colCount) as __}
              <td class="border-b border-surface-100 px-4 py-3">
                <div class="h-4 w-3/4 rounded bg-surface-200"></div>
              </td>
            {/each}
          </tr>
        {/each}
      {:else if rows.length === 0}
        <tr>
          <td colspan={colCount} class="px-4 py-12 text-center text-sm text-surface-500">
            {emptyMessage}
          </td>
        </tr>
      {:else}
        {#each rows as row}
          <tr class="transition-colors hover:bg-surface-50">
            {#each columns as col}
              <td class="border-b border-surface-100 px-4 py-3 text-sm text-surface-700">
                {row[col.key]}
              </td>
            {/each}
            {#if hasActions}
              <td class="border-b border-surface-100 px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-1">
                  {@render actions?.(row)}
                </div>
              </td>
            {/if}
          </tr>
        {/each}
      {/if}
    </tbody>
  </table>
</div>
