<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { pullFull } from '$lib/db/sync-pull';
  import type { SystemConfigItem } from '$lib/db/types';
  import { setConfig } from '$lib/mutations/admin';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';

  let configItems = liveQuery(() => db.system_config.toArray());

  let error = $state('');
  let success = $state('');
  let editingKey = $state<string | null>(null);
  let editValue = $state('');

  function startEdit(item: SystemConfigItem) {
    editingKey = item.key;
    editValue = item.value ?? '';
  }

  function cancelEdit() {
    editingKey = null;
    editValue = '';
  }

  async function saveEdit() {
    if (!editingKey) return;
    error = '';
    const result = await setConfig(editingKey, editValue);
    if (!result.ok) {
      error = result.error ?? 'Failed to update';
      return;
    }
    success = `Updated ${editingKey}`;
    editingKey = null;
    await pullFull();
  }
</script>

{#if error}
  <AlertBanner variant="error" class="mb-4">{error}</AlertBanner>
{/if}
{#if success}
  <AlertBanner variant="success" class="mb-4">{success}</AlertBanner>
{/if}

<div class="space-y-6">
  {#if !$configItems}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else}
    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">System Configuration</span>
      {/snippet}
      {#if ($configItems ?? []).length === 0}
        <div class="px-5 py-8 text-center text-sm text-surface-400">No configuration items.</div>
      {:else}
        <div class="divide-y divide-surface-100">
          {#each $configItems as item (item.key)}
            <div class="flex items-center justify-between px-5 py-4">
              <div class="min-w-0 flex-1">
                <div class="text-sm font-medium text-surface-900">
                  {item.key}
                  {#if item.is_secret}
                    <Icon name="lock" size="sm" class="ml-1 inline-block text-amber-500" />
                  {/if}
                </div>
                <div class="text-xs text-surface-400">
                  {item.description ?? item.category}
                </div>
              </div>
              <div class="ml-4 flex items-center gap-2">
                {#if editingKey === item.key}
                  <Input name="value" bind:value={editValue} class="w-64" />
                  <Btn variant="primary" size="sm" onclick={saveEdit}>Save</Btn>
                  <Btn variant="secondary" size="sm" onclick={cancelEdit}>Cancel</Btn>
                {:else}
                  <code
                    class="max-w-xs truncate rounded bg-surface-100 px-2 py-1 text-xs text-surface-600"
                  >
                    {item.is_secret ? '••••••' : item.value}
                  </code>
                  <Btn variant="secondary" size="sm" onclick={() => startEdit(item)}>Edit</Btn>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </Card>
  {/if}
</div>
