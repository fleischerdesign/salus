<script lang="ts">
  import { useQuery } from '$lib/db/use-query.svelte';
  import { db } from '$lib/db/database';
  import { measurementPageBounds } from '$lib/db/measurement-paging';
  import type { Measurement as Entry, MetricWithPreference } from '$lib/db/types';
  import type { MetricOverview } from '$lib/analytics/views/metric-overview';
  import { overviewForMetric } from '$lib/analytics/views/metric-overview';
  import { fetchTrend, RANGE_KEYS } from '$lib/analytics/views/analytics';
  import { getMetricStat } from '$lib/db/metric-stats';
  import LineChart from '$components/dashboard/LineChart.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
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
  import MetricSettingsModal from '$components/forms/MetricSettingsModal.svelte';
  import { boundHint } from '$lib/utils/bounds';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

  let {
    metricCode,
    metric,
    overviews,
    backUrl,
    showSettings = false
  }: {
    metricCode: string;
    metric: MetricWithPreference;
    overviews: MetricOverview[] | undefined;
    backUrl: string;
    showSettings?: boolean;
  } = $props();

  const overview = $derived(overviews ? overviewForMetric(overviews, metricCode) : null);

  let settingsModalOpen = $state(false);

  let totalEntriesCount = $state(0);
  let pagedEntries = $state<Entry[]>([]);

  let pageNum = $state(1);
  const perPage = 25;

  type Cursor = { mode: 'top' } | { mode: 'older'; time: string } | { mode: 'newer'; time: string };
  let cursor = $state<Cursor>({ mode: 'top' });

  // Cursor-based pagination on the [metric_code+start_time] index: O(log n) per page instead
  // of O(page × perPage) offset skips, which is unusable on high-volume metrics.
  const pagedDataQuery = useQuery(
    async () => {
      const code = metricCode;
      if (!code) return { count: 0, items: [] };
      const stat = await getMetricStat(code);
      const bounds = measurementPageBounds(code, cursor);
      const rawItems = await db.measurement
        .where('[metric_code+start_time]')
        .between(bounds.lower, bounds.upper, bounds.includeLower, bounds.includeUpper)
        .reverse()
        .limit(perPage)
        .toArray();
      return { count: stat?.entry_count ?? 0, items: rawItems.filter((e) => !e.deleted_at) };
    },
    () => `${metricCode}:${pageNum}:${cursor.mode}:${cursor.mode === 'top' ? '' : cursor.time}`
  );
  const pagedData = $derived(pagedDataQuery.value);
  const entriesLoading = $derived(pagedDataQuery.loading);

  $effect(() => {
    if (pagedData) {
      totalEntriesCount = pagedData.count;
      pagedEntries = pagedData.items;
    }
  });

  const hasPrev = $derived(cursor.mode !== 'top' && pageNum > 1);
  const hasNext = $derived(pagedEntries.length >= perPage);

  let entries = $derived(pagedEntries);
  let total = $derived(totalEntriesCount);
  let range = $state('90d');
  let trendQuery = useQuery(
    () => fetchTrend(metricCode, range),
    () => `${metricCode}:${range}`
  );
  let trend = $derived(trendQuery.value);

  let showEntryModal = $state(false);
  let editingEntry = $state<Entry | null>(null);
  let entryValue = $state('');
  let entryTimestamp = $state('');
  let entryNotes = $state('');
  let entryError = $state('');
  let saving = $state(false);
  let entryToDelete = $state<Entry | null>(null);
  let deleteDialogOpen = $state(false);

  const flagsQuery = useQuery(() => db.data_quality_flag.toArray());
  const flaggedIds = $derived.by(() => {
    const ids = new Set<string>();
    for (const f of flagsQuery.value ?? []) {
      if (f.measurement_id) ids.add(f.measurement_id);
    }
    return ids;
  });

  const valueHint = $derived(boundHint(entryValue, metric));

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
      metric_code: metricCode,
      source_data_type: metric.source_data_type ?? '',
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
      const { ok, error } = await createMeasurement(metricCode, body);
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
    const first = pagedEntries[0]?.start_time;
    const last = pagedEntries[pagedEntries.length - 1]?.start_time;
    if (p < pageNum) {
      // Prev (newer): bound above the current first item.
      if (first) cursor = { mode: 'newer', time: first };
      pageNum = p;
    } else if (p > pageNum) {
      // Next (older): bound below the current last item.
      if (last) cursor = { mode: 'older', time: last };
      pageNum = p;
    }
  }

  let prevCode = $state<string | undefined>(undefined);
  $effect(() => {
    if (metricCode !== prevCode) {
      prevCode = metricCode;
      pageNum = 1;
      cursor = { mode: 'top' };
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

<div class="space-y-6">
  <PageHeader
    title={metric.name}
    subtitle={metric.unit || '—'}
    {backUrl}
    icon={metric.icon || 'monitoring'}
    iconColor={metric.color}
  >
    {#snippet actions()}
      <div class="flex h-full items-center">
        {#if showSettings}
          <button
            type="button"
            class="duration-micro flex h-full items-center justify-center border-r border-surface-200 px-4 text-surface-600 transition-colors hover:bg-surface-100 hover:text-surface-900"
            onclick={() => (settingsModalOpen = true)}
            title="Metric Settings & Source Priority"
            aria-label="Metric Settings"
          >
            <Icon name="settings" size="sm" />
          </button>
        {/if}
        <PageHeaderAction icon="add" onclick={openCreateModal}>New Entry</PageHeaderAction>
      </div>
    {/snippet}
    {#snippet stats()}
      {#if overview}
        <div
          class="grid grid-cols-1 divide-y divide-surface-100 sm:grid-cols-3 sm:divide-x sm:divide-y-0"
        >
          <div class="px-6 py-4">
            <Stat value={overview.latest_value ?? '—'} unit={metric.unit} label="Latest" />
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

  {#if trend?.building}
    <Card padding={false}>
      {#snippet header()}
        <div class="flex w-full items-center justify-between pr-2">
          <div class="flex items-center gap-2">
            <Icon name="monitoring" size="sm" class="text-surface-400" /><span
              class="text-sm font-semibold text-surface-900">Trend & History</span
            >
          </div>
          <div class="flex gap-1">
            {#each RANGE_KEYS as r}
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
      <div class="flex h-64 items-center justify-center p-6">
        <Spinner size="lg" />
      </div>
    </Card>
  {:else if trend && trend.values.length >= 2}
    <Card padding={false}>
      {#snippet header()}
        <div class="flex w-full items-center justify-between pr-2">
          <div class="flex items-center gap-2">
            <Icon name="monitoring" size="sm" class="text-surface-400" /><span
              class="text-sm font-semibold text-surface-900">Trend & History</span
            >
          </div>
          <div class="flex gap-1">
            {#each RANGE_KEYS as r}
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
          labels={trend.labels}
          series={[
            {
              label: metric.name ?? 'Value',
              data: trend.values,
              color: metric.color ?? 'var(--color-primary-500)',
              yAxis: 'left'
            }
          ]}
          leftUnit={metric.unit}
          regressionLine={trend.regression?.points}
          regressionCI={trend.regression?.ci}
        />
        {#if trend.regression}
          <div class="mt-2 text-center text-xs text-surface-400">
            OLS Trend: {trend.regression.slope > 0
              ? 'Increasing'
              : trend.regression.slope < 0
                ? 'Decreasing'
                : 'Flat'} (r² = {trend.regression.r_squared.toFixed(3)} · n = {trend.regression.n})
          </div>
        {/if}
      </div>
    </Card>
  {/if}

  {#if entriesLoading}
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
        {#each entries as e, i (e.id)}
          <div in:fade={{ ...staggerFade(i) }}>
            <ListItem hoverable primary={displayValue(e)} secondary="">
              {#snippet children()}
                <div class="flex min-w-0 flex-1 items-center justify-between gap-3">
                  <div class="min-w-0">
                    <div class="flex items-baseline gap-1">
                      <span class="truncate text-sm font-bold text-surface-900"
                        >{displayValue(e)}</span
                      >{#if metric.unit}<span class="text-xs text-surface-400">{metric.unit}</span
                        >{/if}
                      {#if flaggedIds.has(e.id)}
                        <Icon
                          name="warning"
                          size="sm"
                          class="ml-1 shrink-0 text-warning-500"
                          ariaHidden={false}
                        />
                      {/if}
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
    <Pagination
      page={pageNum}
      {total}
      {perPage}
      itemsLabel="entries"
      cursorMode
      {hasPrev}
      {hasNext}
      onpage={onPageChange}
    />
  {/if}
</div>

<Modal title={editingEntry ? 'Edit Entry' : 'New Entry'} bind:open={showEntryModal}>
  <form onsubmit={saveEntry} class="flex flex-col gap-4">
    <FormField label="Value" required
      ><Input name="value" bind:value={entryValue} required /></FormField
    >
    {#if valueHint}
      <p class="flex items-center gap-1 text-sm text-warning-600">
        <Icon name="info" size="sm" />
        {valueHint}
      </p>
    {/if}
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

{#if showSettings}
  <MetricSettingsModal
    bind:open={settingsModalOpen}
    metricCode={metric.code}
    metricName={metric.name}
  />
{/if}
