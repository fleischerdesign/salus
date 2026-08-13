<script lang="ts">
  import Dexie from 'dexie';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { db } from '$lib/db/database';
  import { MS_PER_DAY } from '$lib/utils/datetime';
  import type { Measurement as Entry, MetricGroup } from '$lib/db/types';
  import type { MetricWithPreference } from '$lib/db/types';
  import { mergeMetricPrefs } from '$lib/theme/metric-prefs';
  import { fetchMetricOverview, overviewForMetric } from '$lib/analytics/views/metric-overview';
  import LineChart from '$components/dashboard/LineChart.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import { createMeasurement } from '$lib/mutations/measurement';
  import Card from '$components/ui/Card.svelte';
  import ListItem from '$components/ui/ListItem.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import Textarea from '$components/ui/Textarea.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import MetricEntryDetail from '$components/entries/MetricEntryDetail.svelte';
  import { page } from '$app/state';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

  const metricId = $derived(page.params.id);

  let isGroup = $state(false);
  let group = $state<MetricGroup | null>(null);
  let groupMetrics = $state<MetricWithPreference[]>([]);
  let metricDetail = $state<MetricWithPreference | null>(null);

  const detailDataQuery = useQuery(async () => {
    const id = metricId;
    if (!id) return null;
    const g = await db.metric_group.get(id);
    if (g) {
      const defs = (await db.metric_definition.toArray()).filter((d) => d.group_key === g.key);
      defs.sort((a, b) => a.sort_order - b.sort_order);
      const prefs = await db.user_metric_preference.toArray();
      return {
        isGroup: true,
        group: g,
        groupMetrics: mergeMetricPrefs(defs, prefs),
        metricDetail: null
      };
    }
    const defs = await db.metric_definition.toArray();
    const prefs = await db.user_metric_preference.toArray();
    const merged = mergeMetricPrefs(defs, prefs);
    return {
      isGroup: false,
      group: null,
      groupMetrics: [],
      metricDetail: merged.find((m) => m.code === id) || null
    };
  });
  const detailData = $derived(detailDataQuery.value);
  const loading = $derived(detailDataQuery.loading);

  $effect(() => {
    const d = detailData;
    if (d) {
      isGroup = d.isGroup;
      group = d.group;
      groupMetrics = d.groupMetrics;
      metricDetail = d.metricDetail;
    }
  });

  const overviewsQuery = useQuery(() => fetchMetricOverview());
  const overviews = $derived(overviewsQuery.value);

  let entriesForGroup = $state<Entry[]>([]);
  let entriesForGroupLoading = $state(true);

  const groupEntriesDataQuery = useQuery(async () => {
    const gKey = group?.key;
    if (!isGroup || !gKey || group?.input_mode !== 'combined') return [] as Entry[];
    const defs = (await db.metric_definition.toArray()).filter((d) => d.group_key === gKey);
    const codes = defs.map((d) => d.code);
    if (codes.length === 0) return [] as Entry[];
    const cutoff = new Date(Date.now() - 90 * MS_PER_DAY).toISOString();
    const results = await Promise.all(
      codes.map((code) =>
        db.measurement
          .where('[metric_code+start_time]')
          .between([code, cutoff], [code, Dexie.maxKey])
          .filter((e) => !e.deleted_at)
          .toArray()
      )
    );
    const all = results.flat();
    return all.sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
  });
  const groupEntriesData = $derived(groupEntriesDataQuery.value);

  $effect(() => {
    if (groupEntriesData) {
      entriesForGroup = groupEntriesData;
      entriesForGroupLoading = false;
    }
  });

  let pairedEntries = $derived(
    group?.input_mode === 'combined' ? groupByTimestamp(entriesForGroup) : null
  );

  function groupByTimestamp(
    entries: Entry[]
  ): { timestamp: string; values: Record<string, string | number | null>; notes: string | null }[] {
    const map = new Map<
      string,
      { values: Record<string, string | number | null>; notes: string | null }
    >();
    for (const e of entries) {
      const key = e.start_time;
      const existing = map.get(key);
      if (existing) {
        existing.values[e.metric_code!] = e.value_text ?? e.value_numeric ?? '—';
        if (e.notes) existing.notes = e.notes;
      } else {
        map.set(key, {
          values: { [e.metric_code!]: e.value_text ?? e.value_numeric ?? '—' },
          notes: e.notes
        });
      }
    }
    return [...map.entries()].map(([timestamp, data]) => ({ timestamp, ...data }));
  }

  let chartDataForGroup = $state<
    { code: string; name: string; color: string; data: (number | null)[]; labels: string[] }[]
  >([]);

  const chartDataQuery = useQuery(async () => {
    const gKey = group?.key;
    if (!isGroup || !gKey || group?.input_mode !== 'combined') return [];
    const defs = (await db.metric_definition.toArray()).filter((d) => d.group_key === gKey);
    const cutoff = new Date(Date.now() - 90 * MS_PER_DAY).toISOString();
    const result: {
      code: string;
      name: string;
      color: string;
      data: (number | null)[];
      labels: string[];
    }[] = [];
    for (const d of defs) {
      const clean = await db.measurement
        .where('[metric_code+start_time]')
        .between([d.code, cutoff], [d.code, Dexie.maxKey])
        .filter((e) => !e.deleted_at)
        .toArray();
      if (clean.length > 0) {
        result.push({
          code: d.code,
          name: d.name,
          color: '#4f46e5',
          labels: clean.map((e) => new Date(e.start_time).toLocaleDateString()),
          data: clean.map(
            (e) => e.value_numeric ?? (e.value_text ? parseFloat(e.value_text) : null)
          )
        });
      }
    }
    return result;
  });
  const chartData = $derived(chartDataQuery.value);

  $effect(() => {
    if (chartData) chartDataForGroup = chartData;
  });

  let allGroupMetrics = $derived(isGroup ? groupMetrics : []);

  let showEntryModal = $state(false);
  let combinedValues = $state<Record<string, string>>({});
  let entryTimestamp = $state('');
  let entryNotes = $state('');
  let entryError = $state('');
  let saving = $state(false);

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

  function openCreateModal() {
    combinedValues = Object.fromEntries(allGroupMetrics.map((m) => [m.code, '']));
    entryTimestamp = toDatetimeLocal(new Date().toISOString());
    entryNotes = '';
    entryError = '';
    showEntryModal = true;
  }

  function closeEntryModal() {
    showEntryModal = false;
  }

  async function saveEntry(e: SubmitEvent) {
    e.preventDefault();
    entryError = '';
    saving = true;

    const ts = entryTimestamp ? new Date(entryTimestamp).toISOString() : undefined;
    const notesVal = entryNotes || undefined;
    const combined = allGroupMetrics;
    const values: { code: string; value: number; source_data_type: string | null }[] = [];
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
      values.push({ code: m.code, value: v, source_data_type: m.source_data_type });
    }
    if (values.length === 0) {
      entryError = 'Enter at least one value';
      saving = false;
      return;
    }
    for (const { code, value, source_data_type } of values) {
      const { ok, error } = await createMeasurement(code, {
        value_numeric: value,
        start_time: ts || new Date().toISOString(),
        notes: notesVal,
        source_data_type: source_data_type ?? '',
        source: 'manual'
      });
      if (!ok) {
        entryError = error || 'Failed';
        saving = false;
        return;
      }
    }
    saving = false;
    closeEntryModal();
  }
</script>

<svelte:head
  ><title>Salus — {isGroup ? group?.name : (metricDetail?.name ?? 'Entries')}</title></svelte:head
>

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
      iconColor={groupMetrics[0]?.color}
    >
      {#snippet actions()}
        <PageHeaderAction icon="add" onclick={openCreateModal}>New Entry</PageHeaderAction>
      {/snippet}
    </PageHeader>

    {#if groupMetrics.length > 0}
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {#each groupMetrics as m, i (m.code)}
          {@const ov = overviewForMetric(overviews ?? [], m.code)}
          <a href="/entries/{g.key}/{m.code}" class="no-underline" in:fade={{ ...staggerFade(i) }}>
            <Card padding={false} hoverable>
              {#snippet header()}
                <div class="flex items-center gap-3">
                  <div
                    class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
                    style="background-color: {m.color}20; color: {m.color}"
                  >
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
                  <div class="flex items-baseline gap-1">
                    <span class="text-lg font-bold text-surface-900">{ov.latest_value ?? '—'}</span
                    >{#if ov.latest_value && m.unit}<span class="text-xs text-surface-400"
                        >{m.unit}</span
                      >{/if}
                  </div>
                  <p class="mt-0.5 text-xs text-surface-400">
                    {ov.latest_date ?? 'No entries'} · {ov.entry_count} entries
                  </p>
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
            <div class="flex items-center gap-2">
              <Icon name="monitoring" size="sm" class="text-surface-400" /><span
                class="text-sm font-semibold text-surface-900">Trend</span
              >
            </div>
          </div>
        {/snippet}
        <div class="p-6">
          <LineChart
            labels={chartDataForGroup[0].labels}
            series={chartDataForGroup.map((s) => ({
              label: s.name,
              data: s.data as number[],
              color: s.color,
              yAxis: 'left' as const
            }))}
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
            <div class="flex items-center gap-2">
              <Icon name="list" size="sm" class="text-surface-400" /><span
                class="text-sm font-semibold text-surface-900">Entries</span
              >
            </div>
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
                            <span class="text-sm font-bold text-surface-900">{pe.values[code]}</span
                            >
                            {#if sub?.unit}<span class="text-xs text-surface-400">{sub.unit}</span
                              >{/if}
                          {/each}
                        </div>
                        <p class="mt-0.5 truncate text-xs text-surface-500">
                          {formatDate(pe.timestamp)}{#if pe.notes}<span class="italic">
                              · "{pe.notes}"</span
                            >{/if}
                        </p>
                      </div>
                    </div>
                  {/snippet}
                </ListItem>
              </div>
            {/each}
          </div>
        </Card>
      {:else}
        <EmptyState
          title="No entries yet"
          description="Log your first blood pressure reading."
          icon="edit-note"
        >
          <Btn variant="primary" onclick={openCreateModal}>+ New Entry</Btn>
        </EmptyState>
      {/if}
    {/if}
  </div>

  <Modal title={`New ${g.name} Reading`} bind:open={showEntryModal}>
    <form onsubmit={saveEntry} class="flex flex-col gap-4">
      <div class="flex gap-4">
        {#each allGroupMetrics as m (m.code)}
          <FormField
            label="{m.name} ({m.unit})"
            required={g.input_mode === 'combined'}
            class="flex-1"
          >
            <Input
              name={m.code}
              bind:value={combinedValues[m.code]}
              required={g.input_mode === 'combined'}
              type="number"
            />
          </FormField>
        {/each}
      </div>
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
        <Btn variant="primary" type="submit" loading={saving}>Create</Btn>
      </div>
    </form>
  </Modal>
{:else if metricDetail}
  <MetricEntryDetail
    metricCode={metricDetail.code}
    metric={metricDetail}
    {overviews}
    backUrl="/entries"
  />
{:else}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{/if}
