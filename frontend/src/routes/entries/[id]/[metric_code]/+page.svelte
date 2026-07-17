<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { Measurement as Entry } from '$lib/db/types';
  import type { MetricWithPreference } from '$lib/db/types';
  import { mergeMetricPrefs } from '$lib/db/types';
  import { fetchMetricOverview, overviewForMetric } from '$lib/analytics/views/metric-overview';
  import { useTrend } from '$lib/analytics/views/analytics';
  import LineChart from '$components/dashboard/LineChart.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import {
    createMeasurement,
    updateMeasurement,
    deleteMeasurement
  } from '$lib/mutations/measurement';
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
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

  const parentGroupKey = $derived(page.params.id);
  const childMetricCode = $derived(page.params.metric_code);

  let loading = $state(true);
  let metric = $state<MetricWithPreference | null>(null);

  $effect(() => {
    const code = childMetricCode;
    loading = true;
    (async () => {
      try {
        if (!code) return;
        const def = await db.metric_definition.get(code);
        if (def) {
          const prefs = await db.user_metric_preference.where('metric_code').equals(code).first();
          metric = {
            ...def,
            color: prefs?.color ?? '#4f46e5',
            icon: prefs?.icon ?? 'monitoring',
            widget_size: prefs?.widget_size ?? 'medium',
            widget_enabled: prefs?.widget_enabled ?? false,
            enabled: prefs?.enabled ?? true,
            position: prefs?.position ?? 0
          };
        }
      } finally {
        loading = false;
      }
    })();
  });

  let overviews = liveQuery(() => fetchMetricOverview());

  let allEntries = liveQuery(() =>
    db.measurement
      .where('metric_code')
      .equals(childMetricCode!)
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
  let range = $state('90d');
  let trend = $derived(useTrend(metric?.data_type ?? '', range));
  let overview = $derived($overviews ? overviewForMetric($overviews, childMetricCode!) : null);

  let showEntryModal = $state(false);
  let editingEntry = $state<Entry | null>(null);
  let entryValue = $state('');
  let entryTimestamp = $state('');
  let entryNotes = $state('');
  let entryError = $state('');
  let saving = $state(false);
  let entryToDelete = $state<Entry | null>(null);
  let deleteDialogOpen = $state(false);

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

  function displayValue(e: Entry): string {
    return e.value_text ?? e.value_numeric?.toString() ?? '—';
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

  async function saveEntry(e: SubmitEvent) {
    e.preventDefault();
    entryError = '';
    saving = true;
    const value = entryValue;
    const ts = entryTimestamp ? new Date(entryTimestamp).toISOString() : undefined;
    const notesVal = entryNotes || undefined;
    const body: Record<string, unknown> = {
      value_numeric: isNaN(Number(value)) ? null : Number(value),
      value_text: isNaN(Number(value)) ? value : null,
      start_time: ts || new Date().toISOString(),
      notes: notesVal,
      metric_code: childMetricCode,
      data_type: 'number',
      source: 'manual'
    };
    if (editingEntry) {
      const { ok, error } = await updateMeasurement(editingEntry.id, body);
      saving = false;
      if (!ok) {
        entryError = error || 'Failed';
        return;
      }
    } else {
      const { ok, error } = await createMeasurement(childMetricCode!, body);
      saving = false;
      if (!ok) {
        entryError = error || 'Failed';
        return;
      }
    }
    closeEntryModal();
  }

  async function confirmDeleteEntry() {
    if (!entryToDelete) return;
    const target = entryToDelete;
    entryToDelete = null;
    await deleteMeasurement(target.id);
  }

  function onPageChange(p: number) {
    pageNum = p;
  }

  let prevCode = $state<string | undefined>(undefined);
  $effect(() => {
    if (childMetricCode !== prevCode) {
      prevCode = childMetricCode;
      pageNum = 1;
    }
  });

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
</script>

<svelte:head><title>Salus — {metric?.name ?? 'Entries'}</title></svelte:head>

{#if loading || !metric}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else}
  {@const m = metric}
  <div class="space-y-6">
    <PageHeader
      title={m.name}
      subtitle={m.unit || '—'}
      backUrl="/entries/{parentGroupKey}"
      icon={m.icon || 'monitoring'}
      iconColor={m.color}
    >
      {#snippet actions()}
        <button
          type="button"
          class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white transition-colors hover:bg-primary-600 active:bg-primary-700"
          onclick={openCreateModal}
        >
          <Icon name="add" size="sm" /><span>New Entry</span>
        </button>
      {/snippet}
      {#snippet stats()}
        {#if overview}
          <div
            class="grid grid-cols-1 divide-y divide-surface-100 sm:grid-cols-3 sm:divide-x sm:divide-y-0"
          >
            <div class="px-6 py-4">
              <Stat value={overview.latest_value ?? '—'} unit={m.unit} label="Latest" />
            </div>
            <div class="px-6 py-4">
              <Stat value={overview.latest_date ?? '—'} label="Last Entry" />
            </div>
            <div class="px-6 py-4"><Stat value={overview.entry_count} label="Total Entries" /></div>
          </div>
        {:else}
          <div
            class="grid grid-cols-1 divide-y divide-surface-100 sm:grid-cols-3 sm:divide-x sm:divide-y-0"
          >
            <div class="px-6 py-4">
              <div class="h-10 w-24 animate-pulse rounded bg-surface-100"></div>
            </div>
            <div class="px-6 py-4">
              <div class="h-10 w-24 animate-pulse rounded bg-surface-100"></div>
            </div>
            <div class="px-6 py-4">
              <div class="h-10 w-24 animate-pulse rounded bg-surface-100"></div>
            </div>
          </div>
        {/if}
      {/snippet}
    </PageHeader>

    {#if $trend && $trend.values.length >= 2}
      <Card padding={false}>
        {#snippet header()}
          <div class="flex w-full items-center justify-between pr-2">
            <div class="flex items-center gap-2">
              <Icon name="monitoring" size="sm" class="text-surface-400" /><span
                class="text-sm font-semibold text-surface-900">Trend & History</span
              >
            </div>
            <div class="flex gap-1">
              {#each ['7d', '30d', '90d', '1y'] as r}
                <Btn
                  variant={range === r ? 'primary' : 'secondary'}
                  size="sm"
                  onclick={() => (range = r)}
                  >{r === '1y' ? '1Y' : r === '90d' ? '90D' : r === '30d' ? '30D' : '7D'}</Btn
                >
              {/each}
            </div>
          </div>
        {/snippet}
        <div class="p-6">
          <LineChart
            labels={$trend.labels}
            series={[
              {
                label: m.name ?? 'Value',
                data: $trend.values,
                color: m.color ?? 'var(--color-primary-500)',
                yAxis: 'left'
              }
            ]}
            leftUnit={m.unit}
            regressionLine={$trend.regression?.points}
            regressionCI={$trend.regression?.ci}
          />
          {#if $trend.regression}
            <div class="mt-2 text-center text-xs text-surface-400">
              OLS Trend: {$trend.regression.slope > 0
                ? 'Increasing'
                : $trend.regression.slope < 0
                  ? 'Decreasing'
                  : 'Flat'} (r² = {$trend.regression.r_squared.toFixed(3)} · n = {$trend.regression
                .n})
            </div>
          {/if}
        </div>
      </Card>
    {/if}

    {#if $allEntries === undefined}
      <div class="flex justify-center py-20"><Spinner size="lg" /></div>
    {:else if total === 0}
      <EmptyState
        title="No entries yet"
        description="Log your first entry for this m."
        icon="edit-note"
      >
        <Btn variant="primary" onclick={openCreateModal}>+ New Entry</Btn>
      </EmptyState>
    {:else}
      <Card padding={false}>
        <div class="divide-y divide-surface-100">
          {#each entries as e, i (e.id)}
            <div in:fade={{ ...staggerFade(i) }}>
              <ListItem hoverable primary={displayValue(e)} secondary="">
                {#snippet children()}
                  <div class="flex min-w-0 flex-1 items-center justify-between gap-3">
                    <div class="min-w-0">
                      <div class="flex items-baseline gap-1">
                        <span class="truncate text-sm font-bold text-surface-900"
                          >{displayValue(e)}</span
                        >{#if m.unit}<span class="text-xs text-surface-400">{m.unit}</span>{/if}
                      </div>
                      <p class="mt-0.5 truncate text-xs text-surface-500">
                        {formatDate(e.start_time)}{#if e.notes}<span class="italic">
                            · "{e.notes}"</span
                          >{/if}
                      </p>
                    </div>
                    <div
                      class="duration-micro hidden items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 md:flex [@media(hover:none)]:opacity-60"
                    >
                      <button
                        type="button"
                        class="duration-micro flex h-7 w-7 items-center justify-center rounded text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-700"
                        aria-label="Edit entry"
                        onclick={() => openEditModal(e)}><Icon name="edit" size="sm" /></button
                      >
                      <button
                        type="button"
                        class="duration-micro flex h-7 w-7 items-center justify-center rounded text-surface-400 transition-colors hover:bg-error-50 hover:text-error-500"
                        aria-label="Delete entry"
                        onclick={() => {
                          entryToDelete = e;
                          deleteDialogOpen = true;
                        }}><Icon name="delete" size="sm" /></button
                      >
                    </div>
                    <div class="md:hidden"><Menu items={buildMenuItems(e)} /></div>
                  </div>
                {/snippet}
              </ListItem>
            </div>
          {/each}
        </div>
      </Card>
      <Pagination page={pageNum} {total} {perPage} itemsLabel="entries" onpage={onPageChange} />
    {/if}
  </div>
{/if}

<Modal title={editingEntry ? 'Edit Entry' : 'New Entry'} bind:open={showEntryModal}>
  <form onsubmit={saveEntry} class="flex flex-col gap-4">
    <FormField label="Value" required
      ><Input name="value" bind:value={entryValue} required /></FormField
    >
    <FormField label="Timestamp"
      ><Input name="timestamp" type="datetime-local" bind:value={entryTimestamp} /></FormField
    >
    <FormField label="Notes"
      ><Textarea
        name="notes"
        bind:value={entryNotes}
        rows={3}
        placeholder="Optional notes…"
      /></FormField
    >
    {#if entryError}<p class="text-sm text-error-500">{entryError}</p>{/if}
    <div class="flex justify-end gap-2">
      <Btn variant="ghost" onclick={closeEntryModal}>Cancel</Btn>
      <Btn variant="primary" type="submit" loading={saving}>{editingEntry ? 'Save' : 'Create'}</Btn>
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
