<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { Measurement as Entry, MetricGroup } from '$lib/db/types';
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

  const metricId = $derived(page.params.id);

  let loading = $state(true);
  let isGroup = $state(false);
  let group = $state<MetricGroup | null>(null);
  let groupMetrics = $state<MetricWithPreference[]>([]);
  let metricDetail = $state<MetricWithPreference | null>(null);

  $effect(() => {
    const id = metricId;
    loading = true;
    (async () => {
      try {
        if (!id) return;
        const g = await db.metric_group.get(id);
        if (g) {
          isGroup = true;
          group = g;
        const defs = (await db.metric_definition.toArray()).filter(d => d.group_key === g.key);
        defs.sort((a, b) => a.sort_order - b.sort_order);
          const prefs = await db.user_metric_preference.toArray();
          groupMetrics = mergeMetricPrefs(defs, prefs);
          metricDetail = null;
        } else {
          isGroup = false;
          group = null;
          groupMetrics = [];
          const defs = await db.metric_definition.toArray();
          const prefs = await db.user_metric_preference.toArray();
          const merged = mergeMetricPrefs(defs, prefs);
          metricDetail = merged.find((m) => m.code === id) || null;
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
      .equals(metricId!)
      .toArray()
      .then((arr) =>
        arr
          .filter((e) => !e.deleted_at)
          .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())
      )
  );

  let entriesForGroup = $state<Entry[]>([]);
  let entriesForGroupLoading = $state(true);

  $effect(() => {
    const gKey = group?.key;
    const mode = group?.input_mode;
    if (!isGroup || !gKey || mode !== 'combined') {
      entriesForGroup = [];
      entriesForGroupLoading = false;
      return;
    }
    entriesForGroupLoading = true;
    const subscription = liveQuery(async () => {
      const defs = (await db.metric_definition.toArray()).filter((d) => d.group_key === gKey);
      const codes = defs.map((d) => d.code);
      if (codes.length === 0) return [] as Entry[];
      const all = await db.measurement.where('metric_code').anyOf(codes).toArray();
      return all
        .filter((e) => !e.deleted_at)
        .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
    }).subscribe((v) => {
      entriesForGroup = v;
      entriesForGroupLoading = false;
    });
    return () => subscription.unsubscribe();
  });

  let pairedEntries = $derived(
    group?.input_mode === 'combined' ? groupByTimestamp(entriesForGroup) : null
  );

  function groupByTimestamp(entries: Entry[]): { timestamp: string; values: Record<string, string | number | null>; notes: string | null }[] {
    const map = new Map<string, { values: Record<string, string | number | null>; notes: string | null }>();
    for (const e of entries) {
      const key = e.start_time;
      const existing = map.get(key);
      if (existing) {
        existing.values[e.metric_code!] = e.value_text ?? e.value_numeric ?? '—';
        if (e.notes) existing.notes = e.notes;
      } else {
        map.set(key, { values: { [e.metric_code!]: e.value_text ?? e.value_numeric ?? '—' }, notes: e.notes });
      }
    }
    return [...map.entries()].map(([timestamp, data]) => ({ timestamp, ...data }));
  }

  let chartDataForGroup = $state<{ code: string; name: string; color: string; data: (number | null)[]; labels: string[] }[]>([]);

  $effect(() => {
    const gKey = group?.key;
    if (!isGroup || !gKey || group?.input_mode !== 'combined') {
      chartDataForGroup = [];
      return;
    }
    const subscription = liveQuery(async () => {
      const defs = (await db.metric_definition.toArray()).filter((d) => d.group_key === gKey);
      const result: { code: string; name: string; color: string; data: (number | null)[]; labels: string[] }[] = [];
      for (const d of defs) {
        const meas = await db.measurement.where('metric_code').equals(d.code).toArray();
        const clean = meas
          .filter((e) => !e.deleted_at)
          .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
        if (clean.length > 0) {
          result.push({
            code: d.code, name: d.name, color: '#4f46e5',
            labels: clean.map((e) => new Date(e.start_time).toLocaleDateString()),
            data: clean.map((e) => e.value_numeric ?? (e.value_text ? parseFloat(e.value_text) : null))
          });
        }
      }
      return result;
    }).subscribe((v) => { chartDataForGroup = v; });
    return () => subscription.unsubscribe();
  });

  let pageNum = $state(1);
  const perPage = 25;
  let entries = $derived(($allEntries ?? []).slice((pageNum - 1) * perPage, pageNum * perPage));
  let total = $derived($allEntries?.length ?? 0);
  let range = $state('90d');
  let trend = $derived(useTrend(metricDetail?.data_type ?? '', range));
  let overview = $derived($overviews ? overviewForMetric($overviews, metricId!) : null);

  let allGroupMetrics = $derived(isGroup ? groupMetrics : []);

  let showEntryModal = $state(false);
  let editingEntry = $state<Entry | null>(null);
  let entryValue = $state('');
  let combinedValues = $state<Record<string, string>>({});
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
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  }

  function displayValue(e: Entry): string {
    return e.value_text ?? e.value_numeric?.toString() ?? '—';
  }

  function openCreateModal() {
    editingEntry = null; entryValue = '';
    combinedValues = Object.fromEntries(allGroupMetrics.map(m => [m.code, '']));
    entryTimestamp = toDatetimeLocal(new Date().toISOString()); entryNotes = ''; entryError = '';
    showEntryModal = true;
  }

  function openEditModal(e: Entry) {
    editingEntry = e; entryValue = e.value_text ?? e.value_numeric?.toString() ?? '';
    combinedValues = {};
    entryTimestamp = toDatetimeLocal(e.start_time); entryNotes = e.notes ?? ''; entryError = '';
    showEntryModal = true;
  }

  function closeEntryModal() { showEntryModal = false; editingEntry = null; }

  async function saveEntry(e: SubmitEvent) {
    e.preventDefault(); entryError = ''; saving = true;

    if (isGroup && !editingEntry) {
      const ts = entryTimestamp ? new Date(entryTimestamp).toISOString() : undefined;
      const notesVal = entryNotes || undefined;
      const combined = allGroupMetrics;
      const values: { code: string; value: number }[] = [];
      for (const m of combined) {
        const raw = combinedValues[m.code].trim();
        if (!raw) {
          if (group?.input_mode === 'combined') {
            entryError = `Enter a value for ${m.name}`;
            saving = false;
            return;
          }
          continue;
        }
        const v = parseFloat(raw);
        if (isNaN(v)) {
          entryError = `Invalid number for ${m.name}`;
          saving = false;
          return;
        }
        values.push({ code: m.code, value: v });
      }
      if (values.length === 0) {
        entryError = 'Enter at least one value';
        saving = false;
        return;
      }
      for (const { code, value } of values) {
        const { ok, error } = await createMeasurement(code, {
          value_numeric: value, start_time: ts || new Date().toISOString(),
          notes: notesVal, data_type: 'number', source: 'manual'
        });
        if (!ok) { entryError = error || 'Failed'; saving = false; return; }
      }
      saving = false;
      closeEntryModal(); return;
    }

    if (!metricDetail) return;
    const value = entryValue;
    const ts = entryTimestamp ? new Date(entryTimestamp).toISOString() : undefined;
    const notesVal = entryNotes || undefined;
    const body: Record<string, unknown> = {
      value_numeric: isNaN(Number(value)) ? null : Number(value),
      value_text: isNaN(Number(value)) ? value : null,
      start_time: ts || new Date().toISOString(), notes: notesVal,
      metric_code: metricId, data_type: 'number', source: 'manual'
    };
    if (editingEntry) {
      const { ok, error } = await updateMeasurement(editingEntry.id, body);
      saving = false; if (!ok) { entryError = error || 'Failed'; return; }
    } else {
      const { ok, error } = await createMeasurement(metricId!, body);
      saving = false; if (!ok) { entryError = error || 'Failed'; return; }
    }
    closeEntryModal();
  }

  async function confirmDeleteEntry() {
    if (!entryToDelete) return;
    const target = entryToDelete; entryToDelete = null;
    await deleteMeasurement(target.id);
  }

  function onPageChange(p: number) { pageNum = p; }

  let prevMetricId = $state<string | undefined>(undefined);
  $effect(() => {
    if (metricId !== prevMetricId) { prevMetricId = metricId; pageNum = 1; }
  });

  function buildMenuItems(e: Entry): MenuItem[] {
    return [
      { label: 'Edit', icon: 'edit', onclick: () => openEditModal(e) },
      { label: 'Delete', icon: 'delete', variant: 'danger', onclick: () => { entryToDelete = e; deleteDialogOpen = true; } }
    ];
  }
</script>

<svelte:head><title>Salus — {isGroup ? group?.name : metricDetail?.name ?? 'Entries'}</title></svelte:head>

{#if loading}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else if isGroup && group}
  {@const g = group}
  <div class="space-y-6">
    <PageHeader
      title={g.name}
      subtitle={g.description || ''}
      backUrl="/entries"
      icon={g.icon || 'monitoring'}
      iconColor={groupMetrics[0]?.color || '#4f46e5'}
    >
      {#snippet actions()}
          <button type="button" class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white transition-colors hover:bg-primary-600 active:bg-primary-700" onclick={openCreateModal}>
            <Icon name="add" size="sm" /><span>New Entry</span>
          </button>
      {/snippet}
    </PageHeader>

    {#if groupMetrics.length > 0}
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {#each groupMetrics as m, i (m.code)}
          {@const ov = overviewForMetric($overviews ?? [], m.code)}
          <a href="/entries/{g.key}/{m.code}" class="no-underline" in:fade={{ ...staggerFade(i) }}>
            <Card padding={false} hoverable>
              {#snippet header()}
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg" style="background-color: {m.color}20; color: {m.color}">
                    <Icon name={m.icon || 'monitoring'} />
                  </div>
                  <div class="min-w-0 flex-1">
                    <p class="truncate text-sm font-medium text-surface-900">{m.name}</p>
                    <p class="text-xs text-surface-500">{m.unit || '—'}</p>
                  </div>
                </div>
              {/snippet}
              <div class="p-6">
                {#if ov}
                  <div class="flex items-baseline gap-1"><span class="text-lg font-bold text-surface-900">{ov.latest_value ?? '—'}</span>{#if ov.latest_value && m.unit}<span class="text-xs text-surface-400">{m.unit}</span>{/if}</div>
                  <p class="mt-0.5 text-xs text-surface-400">{ov.latest_date ?? 'No entries'} · {ov.entry_count} entries</p>
                {:else}
                  <p class="text-xs text-surface-400">No entries yet</p>
                {/if}
              </div>
            </Card>
          </a>
        {/each}
      </div>
    {/if}

    {#if g.input_mode === 'combined' && chartDataForGroup && chartDataForGroup.length > 0 && chartDataForGroup[0].labels.length > 0}
      <Card padding={false}>
        {#snippet header()}
          <div class="flex w-full items-center justify-between pr-2">
            <div class="flex items-center gap-2"><Icon name="monitoring" size="sm" class="text-surface-400" /><span class="text-sm font-semibold text-surface-900">Trend</span></div>
            <div class="flex gap-1">
              {#each ['7d', '30d', '90d', '1y'] as r}
                <Btn variant={range === r ? 'primary' : 'secondary'} size="sm" onclick={() => (range = r)}>{r === '1y' ? '1Y' : r === '90d' ? '90D' : r === '30d' ? '30D' : '7D'}</Btn>
              {/each}
            </div>
          </div>
        {/snippet}
        <div class="p-6">
          <LineChart
            labels={chartDataForGroup[0].labels}
            series={chartDataForGroup.map((s) => ({ label: s.name, data: s.data as number[], color: s.color, yAxis: 'left' as const }))}
            leftUnit={groupMetrics[0]?.unit || ''}
          />
        </div>
      </Card>
    {/if}

    {#if g.input_mode === 'combined'}
      {#if entriesForGroupLoading}
        <div class="flex justify-center py-20"><Spinner size="lg" /></div>
      {:else if pairedEntries && pairedEntries.length > 0}
        <Card padding={false}>
          {#snippet header()}
            <div class="flex items-center gap-2"><Icon name="list" size="sm" class="text-surface-400" /><span class="text-sm font-semibold text-surface-900">Entries</span></div>
          {/snippet}
          <div class="divide-y divide-surface-100">
            {#each pairedEntries as pe (pe.timestamp)}
              <div in:fade={{ ...staggerFade(0) }}>
                <ListItem hoverable primary="" secondary="">
                  {#snippet children()}
                    <div class="flex min-w-0 flex-1 items-center justify-between gap-3">
                      <div class="min-w-0">
                        <div class="flex flex-wrap items-baseline gap-1">
                          {#each Object.keys(pe.values) as code}
                            {@const sub = groupMetrics.find((m) => m.code === code)}
                            <span class="text-sm font-bold text-surface-900">{pe.values[code]}</span>
                            {#if sub?.unit}<span class="text-xs text-surface-400">{sub.unit}</span>{/if}
                          {/each}
                        </div>
                        <p class="mt-0.5 truncate text-xs text-surface-500">{formatDate(pe.timestamp)}{#if pe.notes}<span class="italic"> · "{pe.notes}"</span>{/if}</p>
                      </div>
                    </div>
                  {/snippet}
                </ListItem>
              </div>
            {/each}
          </div>
        </Card>
      {:else}
        <EmptyState title="No entries yet" description="Log your first blood pressure reading." icon="edit-note">
          <Btn variant="primary" onclick={openCreateModal}>+ New Entry</Btn>
        </EmptyState>
      {/if}
    {/if}
  </div>

{:else}
  {@const md = metricDetail!}
  <div class="space-y-6">
    {#if !metricDetail}
      <div class="flex justify-center py-20"><Spinner size="lg" /></div>
    {:else}
      <PageHeader title={md.name} subtitle={md.unit || '—'} backUrl="/entries" icon={md.icon || 'monitoring'} iconColor={md.color}>
        {#snippet actions()}
          <button type="button" class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white transition-colors hover:bg-primary-600 active:bg-primary-700" onclick={openCreateModal}>
            <Icon name="add" size="sm" /><span>New Entry</span>
          </button>
        {/snippet}
        {#snippet stats()}
          {#if overview}
            <div class="grid grid-cols-1 divide-y divide-surface-100 sm:grid-cols-3 sm:divide-x sm:divide-y-0">
              <div class="px-6 py-4"><Stat value={overview.latest_value ?? '—'} unit={md.unit} label="Latest" /></div>
              <div class="px-6 py-4"><Stat value={overview.latest_date ?? '—'} label="Last Entry" /></div>
              <div class="px-6 py-4"><Stat value={overview.entry_count} label="Total Entries" /></div>
            </div>
          {:else}
            <div class="grid grid-cols-1 divide-y divide-surface-100 sm:grid-cols-3 sm:divide-x sm:divide-y-0">
              <div class="px-6 py-4"><div class="h-10 w-24 animate-pulse rounded bg-surface-100"></div></div>
              <div class="px-6 py-4"><div class="h-10 w-24 animate-pulse rounded bg-surface-100"></div></div>
              <div class="px-6 py-4"><div class="h-10 w-24 animate-pulse rounded bg-surface-100"></div></div>
            </div>
          {/if}
        {/snippet}
      </PageHeader>

      {#if $trend && $trend.values.length >= 2}
        <Card padding={false}>
          {#snippet header()}
            <div class="flex w-full items-center justify-between pr-2">
              <div class="flex items-center gap-2"><Icon name="monitoring" size="sm" class="text-surface-400" /><span class="text-sm font-semibold text-surface-900">Trend & History</span></div>
              <div class="flex gap-1">
                {#each ['7d', '30d', '90d', '1y'] as r}
                  <Btn variant={range === r ? 'primary' : 'secondary'} size="sm" onclick={() => (range = r)}>{r === '1y' ? '1Y' : r === '90d' ? '90D' : r === '30d' ? '30D' : '7D'}</Btn>
                {/each}
              </div>
            </div>
          {/snippet}
          <div class="p-6">
            <LineChart
              labels={$trend.labels}
              series={[{ label: md.name ?? 'Value', data: $trend.values, color: md.color ?? 'var(--color-primary-500)', yAxis: 'left' }]}
              leftUnit={md.unit}
              regressionLine={$trend.regression?.points}
              regressionCI={$trend.regression?.ci}
            />
            {#if $trend.regression}
              <div class="mt-2 text-center text-xs text-surface-400">
                OLS Trend: {$trend.regression.slope > 0 ? 'Increasing' : $trend.regression.slope < 0 ? 'Decreasing' : 'Flat'} (r² = {$trend.regression.r_squared.toFixed(3)} · n = {$trend.regression.n})
              </div>
            {/if}
          </div>
        </Card>
      {/if}

      {#if $allEntries === undefined}
        <div class="flex justify-center py-20"><Spinner size="lg" /></div>
      {:else if total === 0}
        <EmptyState title="No entries yet" description="Log your first entry for this metric." icon="edit-note">
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
                        <div class="flex items-baseline gap-1"><span class="truncate text-sm font-bold text-surface-900">{displayValue(e)}</span>{#if md.unit}<span class="text-xs text-surface-400">{md.unit}</span>{/if}</div>
                        <p class="mt-0.5 truncate text-xs text-surface-500">{formatDate(e.start_time)}{#if e.notes}<span class="italic"> · "{e.notes}"</span>{/if}</p>
                      </div>
                      <div class="duration-micro hidden items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 md:flex [@media(hover:none)]:opacity-60">
                        <button type="button" class="duration-micro flex h-7 w-7 items-center justify-center rounded text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-700" aria-label="Edit entry" onclick={() => openEditModal(e)}><Icon name="edit" size="sm" /></button>
                        <button type="button" class="duration-micro flex h-7 w-7 items-center justify-center rounded text-surface-400 transition-colors hover:bg-error-50 hover:text-error-500" aria-label="Delete entry" onclick={() => { entryToDelete = e; deleteDialogOpen = true; }}><Icon name="delete" size="sm" /></button>
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
    {/if}
  </div>
{/if}

<Modal title={editingEntry ? 'Edit Entry' : (isGroup ? `New ${group?.name} Reading` : 'New Entry')} bind:open={showEntryModal}>
  <form onsubmit={saveEntry} class="flex flex-col gap-4">
    {#if isGroup && !editingEntry}
      <div class="flex gap-4">
        {#each allGroupMetrics as m (m.code)}
          <FormField label="{m.name} ({m.unit})" required={group?.input_mode === 'combined'} class="flex-1">
            <Input name={m.code} bind:value={combinedValues[m.code]} required={group?.input_mode === 'combined'} type="number" />
          </FormField>
        {/each}
      </div>
    {:else}
      <FormField label="Value" required><Input name="value" bind:value={entryValue} required /></FormField>
    {/if}
    <FormField label="Timestamp"><Input name="timestamp" type="datetime-local" bind:value={entryTimestamp} /></FormField>
    <FormField label="Notes"><Textarea name="notes" bind:value={entryNotes} rows={3} placeholder="Optional notes…" /></FormField>
    {#if entryError}<p class="text-sm text-error-500">{entryError}</p>{/if}
    <div class="flex justify-end gap-2">
      <Btn variant="ghost" onclick={closeEntryModal}>Cancel</Btn>
      <Btn variant="primary" type="submit" loading={saving}>{editingEntry ? 'Save' : 'Create'}</Btn>
    </div>
  </form>
</Modal>

<ConfirmDialog bind:open={deleteDialogOpen} title="Delete Entry" variant="danger" message="Delete this entry? This cannot be undone." confirmLabel="Delete" onconfirm={confirmDeleteEntry} oncancel={() => { entryToDelete = null; }} />
