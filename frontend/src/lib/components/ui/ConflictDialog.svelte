<script lang="ts">
  import Modal from './Modal.svelte';
  import AlertBanner from './AlertBanner.svelte';
  import Btn from './Btn.svelte';
  import { computeDiff, formatValue, entityLabel } from '$lib/utils/diff';
  import type { DiffRow } from '$lib/utils/diff';

  interface Props {
    open?: boolean;
    table: string;
    clientRecord?: Record<string, unknown>;
    serverRecord?: Record<string, unknown>;
    onresolve?: (fields: Record<string, unknown> | null) => void;
  }

  let {
    open = $bindable(false),
    table,
    clientRecord,
    serverRecord,
    onresolve,
  }: Props = $props();

  const diff = $derived(computeDiff(clientRecord ?? {}, serverRecord ?? {}));

  let selection = $state<Record<string, 'mine' | 'server'>>({});

  $effect(() => {
    const next: Record<string, 'mine' | 'server'> = {};
    for (const row of diff) {
      next[row.field] = 'mine';
    }
    selection = next;
  });

  function apply() {
    const fields: Record<string, unknown> = {};
    for (const row of diff) {
      if (selection[row.field] === 'mine' && clientRecord) {
        fields[row.field] = clientRecord[row.field];
      }
    }
    open = false;
    onresolve?.(fields);
  }

  function discard() {
    open = false;
    onresolve?.(null);
  }
</script>

<Modal bind:open title="{entityLabel(table)} — Conflict" size="lg" onclose={discard}>
  <div class="flex flex-col gap-4">
    <AlertBanner variant="warning" message="This record was modified by another session. Choose which version to keep for each changed field." />

    {#if diff.length > 0}
      <div class="overflow-x-auto rounded-lg border border-surface-200">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-surface-200 bg-surface-50">
              <th class="px-4 py-2 font-medium text-surface-500">Field</th>
              <th class="px-4 py-2 font-medium text-surface-500">Server</th>
              <th class="px-4 py-2 font-medium text-surface-500">Yours</th>
            </tr>
          </thead>
          <tbody>
            {#each diff as row (row.field)}
              <tr class="border-b border-surface-100 last:border-b-0">
                <td class="px-4 py-2 text-surface-700">{row.field}</td>
                <td class="px-4 py-2">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="diff-{row.field}"
                      value="server"
                      checked={selection[row.field] === 'server'}
                      onchange={() => selection[row.field] = 'server'}
                      class="h-4 w-4 accent-primary-500"
                    />
                    <span class="text-surface-600">{formatValue(row.server)}</span>
                  </label>
                </td>
                <td class="px-4 py-2">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="diff-{row.field}"
                      value="mine"
                      checked={selection[row.field] === 'mine'}
                      onchange={() => selection[row.field] = 'mine'}
                      class="h-4 w-4 accent-primary-500"
                    />
                    <span class="text-surface-600">{formatValue(row.client)}</span>
                  </label>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <p class="text-sm text-surface-500">No field differences detected. The server version will be used.</p>
    {/if}

    <div class="flex justify-end gap-3">
      <Btn variant="ghost" onclick={discard}>Discard my changes</Btn>
      {#if diff.length > 0}
        <Btn variant="primary" onclick={apply}>Apply</Btn>
      {/if}
    </div>
  </div>
</Modal>
