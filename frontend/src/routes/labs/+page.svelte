<script lang="ts">
  import { db } from '$lib/db/database';
  import type { LabMarker, LabResult, MetricDefinition } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Input from '$components/ui/Input.svelte';
  import Select from '$components/ui/Select.svelte';
  import Checkbox from '$components/ui/Checkbox.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import { createLabPanel, deleteLabPanel } from '$lib/mutations/lab';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';

  const panelsQuery = useQuery(() => db.notDeleted(db.lab_panel).toArray());
  const panels = $derived(panelsQuery.value);

  const resultsQuery = useQuery(() => db.notDeleted(db.lab_result).toArray());
  const results = $derived(resultsQuery.value);

  const markersQuery = useQuery(() => db.lab_marker.toArray());
  const markers = $derived(markersQuery.value);

  const definitionsQuery = useQuery(() =>
    db.metric_definition.where('group_key').equals('laboratory').toArray()
  );
  const definitions = $derived(definitionsQuery.value);

  const loading = $derived(panelsQuery.loading || markersQuery.loading);

  const markerMap = $derived.by(() => {
    const map: Record<string, LabMarker> = {};
    for (const m of markers ?? []) map[m.code] = m;
    return map;
  });

  const definitionMap = $derived.by(() => {
    const map: Record<string, MetricDefinition> = {};
    for (const d of definitions ?? []) map[d.code] = d;
    return map;
  });

  const resultsByPanel = $derived.by(() => {
    const map: Record<string, LabResult[]> = {};
    for (const r of results ?? []) {
      if (!map[r.panel_id]) map[r.panel_id] = [];
      map[r.panel_id].push(r);
    }
    return map;
  });

  const sortedPanels = $derived(
    (panels ?? []).sort((a, b) => (b.collection_date ?? '').localeCompare(a.collection_date ?? ''))
  );

  const markerOptions = $derived(
    (markers ?? [])
      .map((m) => ({ value: m.code, label: definitionMap[m.code]?.name ?? m.code }))
      .sort((a, b) => a.label.localeCompare(b.label))
  );

  interface ResultRow {
    metric_code: string;
    value: string;
  }

  let formOpen = $state(false);
  let collectionDate = $state(todayString());
  let labName = $state('');
  let fasting = $state(false);
  let rows = $state<ResultRow[]>([{ metric_code: '', value: '' }]);
  let saving = $state(false);

  let pendingDelete = $state<{ id: string; label: string } | null>(null);

  function openForm() {
    collectionDate = todayString();
    labName = '';
    fasting = false;
    rows = [{ metric_code: '', value: '' }];
    formOpen = true;
  }

  function addRow() {
    rows = [...rows, { metric_code: '', value: '' }];
  }

  function removeRow(index: number) {
    rows = rows.filter((_, i) => i !== index);
  }

  async function handleSave() {
    const valid = rows.filter((r) => r.metric_code && r.value !== '');
    if (valid.length === 0) return;
    saving = true;
    const { ok, error } = await createLabPanel({
      collection_date: collectionDate,
      lab_name: labName || null,
      fasting,
      results: valid.map((r) => ({ metric_code: r.metric_code, value: Number(r.value) }))
    });
    saving = false;
    if (ok) formOpen = false;
    else console.error('Failed to create lab panel:', error);
  }

  async function confirmDelete() {
    if (!pendingDelete) return;
    const { ok, error } = await deleteLabPanel(pendingDelete.id);
    if (!ok) console.error('Failed to delete lab panel:', error);
    pendingDelete = null;
  }

  function formatDate(iso: string): string {
    return new Date(iso + 'T12:00').toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  }

  function rangeLabel(r: LabResult, marker: LabMarker | undefined): string {
    const low = r.reference_low ?? marker?.reference_low;
    const high = r.reference_high ?? marker?.reference_high;
    if (low == null && high == null) return '';
    return `ref ${low ?? '—'}–${high ?? '—'}`;
  }
</script>

<svelte:head><title>Salus — Lab Results</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Lab Results"
    subtitle="Track blood work and reference ranges over time"
    icon="science"
  >
    {#snippet actions()}
      <PageHeaderAction icon="add" onclick={openForm}>Add Panel</PageHeaderAction>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="flex justify-center py-20">
      <Spinner />
    </div>
  {:else if (sortedPanels ?? []).length === 0}
    <Card>
      <EmptyState
        icon="science"
        title="No lab panels yet"
        description="Add your first blood panel to start tracking markers against reference ranges."
      >
        <Btn variant="primary" onclick={openForm}>Add Panel</Btn>
      </EmptyState>
    </Card>
  {:else}
    <div class="grid gap-4 lg:grid-cols-2">
      {#each sortedPanels as panel}
        {@const panelResults = resultsByPanel[panel.id] ?? []}
        <Card padding={false} class="overflow-hidden">
          <div class="flex items-start justify-between gap-3 border-b border-surface-100 px-6 py-4">
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-500/10 text-primary-600"
              >
                <Icon name="science" />
              </div>
              <div>
                <h3 class="text-sm font-semibold text-surface-900">
                  {panel.lab_name ?? 'Lab Panel'}
                </h3>
                <p class="text-xs text-surface-500">
                  {formatDate(panel.collection_date)}
                  {panel.fasting ? ' · Fasting' : ''}
                </p>
              </div>
            </div>
            <button
              class="flex h-8 w-8 items-center justify-center rounded-md text-surface-400 transition-colors hover:bg-error-50 hover:text-error-600"
              onclick={() => (pendingDelete = { id: panel.id, label: panel.lab_name ?? 'panel' })}
              aria-label="Delete panel"
            >
              <Icon name="delete" size="sm" />
            </button>
          </div>

          <div class="divide-y divide-surface-100">
            {#each panelResults as r}
              {@const def = definitionMap[r.metric_code]}
              {@const marker = markerMap[r.metric_code]}
              <div class="flex items-center justify-between gap-3 px-6 py-3">
                <div class="min-w-0">
                  <p class="truncate text-sm text-surface-800">{def?.name ?? r.metric_code}</p>
                  <p class="text-xs text-surface-400">{rangeLabel(r, marker)}</p>
                </div>
                <div class="flex items-center gap-2">
                  {#if r.is_abnormal}
                    <span
                      class="rounded-full bg-error-50 px-2 py-0.5 text-xs font-semibold text-error-600"
                    >
                      High/Low
                    </span>
                  {/if}
                  <span class="text-sm font-semibold text-surface-900">
                    {r.value}
                    <span class="text-xs font-normal text-surface-400">{r.unit ?? def?.unit}</span>
                  </span>
                </div>
              </div>
            {:else}
              <p class="px-6 py-3 text-sm text-surface-400">No results recorded.</p>
            {/each}
          </div>
        </Card>
      {/each}
    </div>
  {/if}

  <Modal bind:open={formOpen} title="Add Lab Panel" size="lg">
    <div class="space-y-4">
      <div class="grid gap-4 sm:grid-cols-2">
        <Input
          name="collection_date"
          type="date"
          label="Collection date"
          bind:value={collectionDate}
        />
        <Input name="lab_name" label="Lab name" placeholder="e.g. LabCorp" bind:value={labName} />
      </div>
      <Checkbox name="fasting" label="Fasting sample" bind:checked={fasting} />

      <div>
        <p class="mb-2 text-xs font-semibold text-surface-900">Results</p>
        <div class="space-y-2">
          {#each rows as row, i}
            <div class="flex items-end gap-2">
              <Select
                name="metric_code_{i}"
                options={markerOptions}
                bind:value={row.metric_code}
                class="flex-1"
              />
              <Input
                name="value_{i}"
                type="number"
                step="any"
                placeholder="Value"
                bind:value={row.value}
                class="w-28"
              />
              <button
                class="flex h-10 w-8 items-center justify-center rounded-md text-surface-400 transition-colors hover:bg-error-50 hover:text-error-600"
                onclick={() => removeRow(i)}
                disabled={rows.length === 1}
                aria-label="Remove result"
              >
                <Icon name="close" size="sm" />
              </button>
            </div>
          {/each}
        </div>
        <button
          class="mt-2 text-xs font-semibold text-primary-600 hover:text-primary-700"
          onclick={addRow}
        >
          + Add marker
        </button>
      </div>

      <div class="flex justify-end gap-3 pt-2">
        <Btn variant="ghost" onclick={() => (formOpen = false)}>Cancel</Btn>
        <Btn variant="primary" onclick={handleSave} loading={saving}>Save Panel</Btn>
      </div>
    </div>
  </Modal>

  <ConfirmDialog
    open={pendingDelete != null}
    title="Delete panel?"
    message={pendingDelete ? `This removes "${pendingDelete.label}" and all its results.` : ''}
    confirmLabel="Delete"
    onconfirm={confirmDelete}
    oncancel={() => (pendingDelete = null)}
  />
</div>
