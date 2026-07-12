<script lang="ts">
  import { liveQuery } from 'dexie';
  import type { components } from '$lib/api/schema';
  import { db } from '$lib/db/database';
  import type { Measurement as Entry, MetricType as Metric } from '$lib/db/types';
  import { fetchMetricOverview, overviewForMetric } from '$lib/analytics/views/metric-overview';
  import { mutate, nextTempId } from '$lib/db/mutate';
  import Card from '$components/ui/Card.svelte';
  import ListItem from '$components/ui/ListItem.svelte';
  import Menu, { type MenuItem } from '$components/ui/Menu.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import Textarea from '$components/ui/Textarea.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import Pagination from '$components/ui/Pagination.svelte';
  import { page } from '$app/state';

  let metric = liveQuery(() => db.metric_type.get(metricId));
  let overviews = liveQuery(() => fetchMetricOverview());

  let allEntries = liveQuery(() =>
    db.measurement
      .where('metric_type_id')
      .equals(metricId)
      .toArray()
      .then((arr) =>
        arr
          .filter((e) => !e.deleted_at)
          .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())
      )
  );

  let pageNum = $state(1);
  const perPage = 25;

  let entries = $derived(($allEntries ?? []).slice((pageNum - 1) * perPage, pageNum * perPage));
  let total = $derived($allEntries?.length ?? 0);
  let totalPages = $derived(Math.max(1, Math.ceil(total / perPage)));

  // Entry form state
  let showEntryModal = $state(false);
  let editingEntry = $state<Entry | null>(null);
  let entryValue = $state('');
  let entryTimestamp = $state('');
  let entryNotes = $state('');
  let entryError = $state('');
  let saving = $state(false);

  // Delete confirmation
  let entryToDelete = $state<Entry | null>(null);
  let deleteDialogOpen = $state(false);

  const metricId = $derived(Number(page.params.id));

  let overview = $derived($overviews ? overviewForMetric($overviews, metricId) : null);

  function toDatetimeLocal(ts: string): string {
    const dt = new Date(ts);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
  }

  function formatDate(ts: string): string {
    return new Date(ts).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function buildMenuItems(e: Entry): MenuItem[] {
    return [
      { label: 'Edit', icon: 'edit', onclick: () => openEditModal(e) },
      {
        label: 'Delete',
        icon: 'delete',
        variant: 'danger',
        onclick: () => {
          entryToDelete = e;
          deleteDialogOpen = true;
        }
      }
    ];
  }

  function openCreateModal() {
    editingEntry = null;
    entryValue = '';
    entryTimestamp = toDatetimeLocal(new Date().toISOString());
    entryNotes = '';
    entryError = '';
    showEntryModal = true;
  }

  function openEditModal(e: Entry) {
    editingEntry = e;
    entryValue = e.value_text ?? e.value_numeric?.toString() ?? '';
    entryTimestamp = toDatetimeLocal(e.start_time);
    entryNotes = e.notes ?? '';
    entryError = '';
    showEntryModal = true;
  }

  function closeEntryModal() {
    showEntryModal = false;
    editingEntry = null;
  }

  function displayValue(e: Entry): string {
    return e.value_text ?? e.value_numeric?.toString() ?? '—';
  }

  async function saveEntry(e: SubmitEvent) {
    e.preventDefault();
    entryError = '';
    saving = true;
    const value = entryValue;
    const timestamp = entryTimestamp ? new Date(entryTimestamp).toISOString() : undefined;
    const notesVal = entryNotes || undefined;
    const body: Record<string, unknown> = {
      value_numeric: isNaN(Number(value)) ? null : Number(value),
      value_text: isNaN(Number(value)) ? value : null,
      start_time: timestamp || new Date().toISOString(),
      notes: notesVal,
      metric_type_id: metricId,
      data_type: 'number',
      source: 'manual'
    };
    if (editingEntry) {
      const { ok, error } = await mutate({
        table: 'measurement',
        type: 'update',
        data: body,
        optimistic: { ...editingEntry, ...body },
        realId: editingEntry.id
      });
      saving = false;
      if (!ok) {
        entryError = error || 'Failed to update entry';
        return;
      }
    } else {
      const tempId = nextTempId();
      const { ok, error } = await mutate({
        table: 'measurement',
        type: 'create',
        data: {
          metric_type_id: metricId,
          value_numeric: isNaN(Number(value)) ? null : Number(value),
          value_text: isNaN(Number(value)) ? value : null,
          start_time: timestamp || new Date().toISOString(),
          notes: notesVal,
          data_type: 'number',
          source: 'manual'
        },
        optimistic: {
          id: tempId,
          metric_type_id: metricId,
          user_id: 0,
          value_numeric: isNaN(Number(value)) ? null : Number(value),
          value_text: isNaN(Number(value)) ? value : null,
          value_json: null,
          start_time: timestamp || new Date().toISOString(),
          end_time: null,
          notes: notesVal,
          data_type: 'number',
          source: 'manual',
          external_id: null,
          created_at: new Date().toISOString(),
          updated_at: null,
          deleted_at: null
        }
      });
      saving = false;
      if (!ok) {
        entryError = error || 'Failed to create entry';
        return;
      }
    }
    closeEntryModal();
  }

  async function confirmDeleteEntry() {
    if (!entryToDelete) return;
    const target = entryToDelete;
    entryToDelete = null;
    await mutate({
      table: 'measurement',
      type: 'delete',
      optimistic: { id: target.id },
      realId: target.id
    });
  }

  function onPageChange(p: number) {
    pageNum = p;
  }

  // Reset page on metric change
  let prevMetricId = $state(NaN);
  $effect(() => {
    if (metricId !== prevMetricId) {
      prevMetricId = metricId;
      pageNum = 1;
    }
  });
</script>

<svelte:head><title>Salus — {$metric?.name ?? 'Entries'}</title></svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <Card padding={false}>
    {#snippet header()}
      <div class="flex items-center gap-3">
        <a
          href="/entries"
          class="flex h-9 w-9 items-center justify-center rounded-lg text-surface-400 transition-colors duration-150 hover:bg-surface-100 hover:text-surface-700"
          aria-label="Back to Logbook"
        >
          <Icon name="arrow-back" size="sm" />
        </a>
        {#if $metric}
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
            style="background-color: {$metric.color}20; color: {$metric.color}"
          >
            <Icon name={$metric.icon || 'monitoring'} />
          </div>
        {:else}
          <div class="h-10 w-10 shrink-0 animate-pulse rounded-lg bg-surface-200"></div>
        {/if}
        <div class="min-w-0 flex-1">
          <h1 class="truncate text-lg font-semibold text-surface-900">
            {$metric?.name ?? 'Loading…'}
          </h1>
          {#if $metric}
            <p class="text-xs text-surface-500">{$metric.unit || '—'}</p>
          {/if}
        </div>
        <Btn variant="primary" onclick={openCreateModal}>
          <Icon name="add" size="sm" />New Entry
        </Btn>
      </div>
    {/snippet}

    {#if overview}
      <div class="flex flex-wrap items-center gap-x-8 gap-y-4 px-6 py-4">
        <Stat value={overview.latest_value ?? '—'} unit={$metric?.unit} label="Latest" />
        <Stat value={overview.latest_date ?? '—'} label="Last Entry" />
        <Stat value={overview.entry_count} label="Total Entries" />
      </div>
    {:else if !$overviews}
      <div class="flex items-center gap-x-8 px-6 py-4">
        <div class="h-10 w-24 animate-pulse rounded bg-surface-100"></div>
        <div class="h-10 w-24 animate-pulse rounded bg-surface-100"></div>
        <div class="h-10 w-24 animate-pulse rounded bg-surface-100"></div>
      </div>
    {/if}
  </Card>

  <!-- Entries -->
  {#if !$allEntries}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else if total === 0}
    <EmptyState
      title="No entries yet"
      description="Log your first entry for this metric."
      icon="edit-note"
    >
      <Btn variant="primary" onclick={openCreateModal}>+ New Entry</Btn>
    </EmptyState>
  {:else}
    <Card padding={false}>
      <div class="divide-y divide-surface-100">
        {#each entries as e (e.id)}
          <ListItem hoverable primary={displayValue(e)} secondary="">
            {#snippet children()}
              <div class="flex min-w-0 flex-1 items-center justify-between gap-3">
                <div class="min-w-0">
                  <div class="flex items-baseline gap-1">
                    <span class="truncate text-sm font-bold text-surface-900">
                      {displayValue(e)}
                    </span>
                    {#if $metric?.unit}
                      <span class="text-xs text-surface-400">{$metric.unit}</span>
                    {/if}
                  </div>
                  <p class="mt-0.5 truncate text-xs text-surface-500">
                    {formatDate(e.start_time)}
                    {#if e.notes}
                      <span class="italic"> · "{e.notes}"</span>
                    {/if}
                  </p>
                </div>

                <!-- Desktop: hover-to-reveal inline buttons -->
                <div
                  class="hidden items-center gap-0.5 opacity-0 transition-opacity duration-150 group-hover:opacity-100 md:flex [@media(hover:none)]:opacity-60"
                >
                  <button
                    type="button"
                    class="flex h-7 w-7 items-center justify-center rounded text-surface-400 transition-colors duration-150 hover:bg-surface-100 hover:text-surface-700"
                    aria-label="Edit entry"
                    onclick={() => openEditModal(e)}
                  >
                    <Icon name="edit" size="sm" />
                  </button>
                  <button
                    type="button"
                    class="flex h-7 w-7 items-center justify-center rounded text-surface-400 transition-colors duration-150 hover:bg-error-50 hover:text-error-500"
                    aria-label="Delete entry"
                    onclick={() => {
                      entryToDelete = e;
                      deleteDialogOpen = true;
                    }}
                  >
                    <Icon name="delete" size="sm" />
                  </button>
                </div>

                <!-- Mobile: dot menu -->
                <div class="md:hidden">
                  <Menu items={buildMenuItems(e)} />
                </div>
              </div>
            {/snippet}
          </ListItem>
        {/each}
      </div>
    </Card>

    <Pagination page={pageNum} {total} {perPage} itemsLabel="entries" onpage={onPageChange} />
  {/if}
</div>

<Modal title={editingEntry ? 'Edit Entry' : 'New Entry'} bind:open={showEntryModal}>
  <form onsubmit={saveEntry} class="flex flex-col gap-4">
    <FormField label="Value" required>
      <Input name="value" bind:value={entryValue} required />
    </FormField>
    <FormField label="Timestamp">
      <Input name="timestamp" type="datetime-local" bind:value={entryTimestamp} />
    </FormField>
    <FormField label="Notes">
      <Textarea name="notes" bind:value={entryNotes} rows={3} placeholder="Optional notes…" />
    </FormField>
    {#if entryError}
      <p class="text-sm text-error-500">{entryError}</p>
    {/if}
    <div class="flex justify-end gap-2">
      <Btn variant="ghost" onclick={closeEntryModal}>Cancel</Btn>
      <Btn variant="primary" type="submit" loading={saving}>
        {editingEntry ? 'Save' : 'Create'}
      </Btn>
    </div>
  </form>
</Modal>

<ConfirmDialog
  bind:open={deleteDialogOpen}
  title="Delete Entry"
  variant="danger"
  message="Delete this entry? This cannot be undone."
  confirmLabel="Delete"
  onconfirm={confirmDeleteEntry}
  oncancel={() => {
    entryToDelete = null;
  }}
/>
