<script lang="ts">
  import { liveQuery } from 'dexie';
  import type { components } from '$lib/api/schema';
  import { db } from '$lib/db/database';
  import type { MetricType } from '$lib/db/types';
  import { fetchMetricOverview, overviewForMetric } from '$lib/analytics/views/metric-overview';
  import { createMetricType, updateMetricType, deleteMetricType } from '$lib/mutations/measurement';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';
  import Card from '$components/ui/Card.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import Select from '$components/ui/Select.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';

  type Metric = MetricType;

  let metrics = liveQuery(() => db.metric_type.toArray());
  let overviews = liveQuery(() => fetchMetricOverview());

  // Metric form state
  let showMetricModal = $state(false);
  let editingMetric = $state<Metric | null>(null);
  let metricName = $state('');
  let metricUnit = $state('');
  let metricColor = $state('#4f46e5');
  let metricIcon = $state('monitoring');
  let metricDataType = $state('number');
  let metricError = $state('');
  let saving = $state(false);

  // Delete confirmation state
  let metricToDelete = $state<Metric | null>(null);
  let deleteDialogOpen = $state(false);

  const dataTypeOptions = [
    { value: 'number', label: 'Number' },
    { value: 'text', label: 'Text' },
    { value: 'boolean', label: 'Boolean' }
  ];

  function openCreateModal() {
    editingMetric = null;
    metricName = '';
    metricUnit = '';
    metricColor = '#4f46e5';
    metricIcon = 'monitoring';
    metricDataType = 'number';
    metricError = '';
    showMetricModal = true;
  }

  function openEditModal(m: Metric) {
    editingMetric = m;
    metricName = m.name;
    metricUnit = m.unit;
    metricColor = m.color;
    metricIcon = m.icon;
    metricDataType = m.data_type;
    metricError = '';
    showMetricModal = true;
  }

  function closeModal() {
    showMetricModal = false;
    editingMetric = null;
  }

  async function saveMetric(e: SubmitEvent) {
    e.preventDefault();
    metricError = '';
    saving = true;
    const body = {
      name: metricName,
      unit: metricUnit,
      data_type: metricDataType as 'number' | 'text' | 'boolean',
      color: metricColor,
      icon: metricIcon
    };
    if (editingMetric) {
      const { ok, error } = await updateMetricType(
        editingMetric.id,
        body as Record<string, unknown>
      );
      saving = false;
      if (!ok) {
        metricError = error || 'Failed to update metric';
        return;
      }
    } else {
      const { ok, error } = await createMetricType(body as Record<string, unknown>);
      saving = false;
      if (!ok) {
        metricError = error || 'Failed to create metric';
        return;
      }
    }
    closeModal();
  }

  async function confirmDeleteMetric() {
    if (!metricToDelete) return;
    const target = metricToDelete;
    metricToDelete = null;
    await deleteMetricType(target.id);
  }
</script>

<svelte:head><title>Salus — Logbook</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Logbook"
    subtitle="Select a metric to view and manage its entries."
    icon="library-books"
    iconColor="#4f46e5"
  >
    {#snippet actions()}
      <button
        type="button"
        class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white transition-colors hover:bg-primary-600 active:bg-primary-700"
        onclick={openCreateModal}
      >
        <Icon name="add" size="sm" />
        <span>New Metric</span>
      </button>
    {/snippet}
  </PageHeader>

  {#if !$metrics || !$overviews}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else if $metrics.length === 0}
    <EmptyState
      title="No metrics yet"
      description="Create your first metric to start logging data."
      icon="receipt-long"
    >
      <Btn variant="primary" onclick={openCreateModal}>+ New Metric</Btn>
    </EmptyState>
  {:else}
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {#each $metrics as m, i (m.id)}
        {@const ov = overviewForMetric($overviews, m.id)}
        <a href="/entries/{m.id}" class="no-underline" in:fade={{ ...staggerFade(i) }}>
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
                  <div class="flex items-center gap-1.5">
                    <p class="truncate text-sm font-medium text-surface-900">{m.name}</p>
                    {#if m.is_system}
                      <Badge variant="default">system</Badge>
                    {/if}
                  </div>
                  <p class="text-xs text-surface-500">{m.unit || '—'}</p>
                </div>
                <div class="flex items-center gap-0.5">
                  <button
                    type="button"
                    class="duration-micro flex h-7 w-7 items-center justify-center rounded text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-700"
                    aria-label="Edit metric"
                    onclick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      openEditModal(m);
                    }}
                  >
                    <Icon name="edit" size="sm" />
                  </button>
                  {#if !m.is_system}
                    <button
                      type="button"
                      class="duration-micro flex h-7 w-7 items-center justify-center rounded text-surface-400 transition-colors hover:bg-error-50 hover:text-error-500"
                      aria-label="Delete metric"
                      onclick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        metricToDelete = m;
                        deleteDialogOpen = true;
                      }}
                    >
                      <Icon name="delete" size="sm" />
                    </button>
                  {/if}
                </div>
              </div>
            {/snippet}
            <div class="p-6">
              {#if ov}
                <div class="flex items-baseline gap-1">
                  <span class="text-lg font-bold text-surface-900">
                    {ov.latest_value ?? '—'}
                  </span>
                  {#if ov.latest_value && m.unit}
                    <span class="text-xs text-surface-400">{m.unit}</span>
                  {/if}
                </div>
                <p class="mt-0.5 text-xs text-surface-400">
                  {ov.latest_date ?? 'No entries'} · {ov.entry_count}
                  {ov.entry_count === 1 ? 'entry' : 'entries'}
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
</div>

<Modal title={editingMetric ? 'Edit Metric' : 'New Metric'} bind:open={showMetricModal}>
  <form onsubmit={saveMetric} class="flex flex-col gap-4">
    <FormField label="Name" required>
      <Input name="name" bind:value={metricName} required placeholder="e.g. Weight" />
    </FormField>
    <FormField label="Unit">
      <Input name="unit" bind:value={metricUnit} placeholder="e.g. kg" />
    </FormField>
    <div class="flex gap-4">
      <FormField label="Color" class="flex-1">
        <input
          type="color"
          bind:value={metricColor}
          class="h-11 w-full cursor-pointer rounded-md border border-surface-300"
        />
      </FormField>
      <FormField label="Icon" class="flex-1">
        <Input name="icon" bind:value={metricIcon} placeholder="monitoring" />
      </FormField>
    </div>
    <FormField label="Data Type">
      <Select name="data_type" options={dataTypeOptions} bind:value={metricDataType} />
    </FormField>
    {#if metricError}<p class="text-sm text-error-500">{metricError}</p>{/if}
    <div class="flex justify-end gap-2">
      <Btn variant="ghost" onclick={closeModal}>Cancel</Btn>
      <Btn variant="primary" type="submit" loading={saving}>
        {editingMetric ? 'Save' : 'Create'}
      </Btn>
    </div>
  </form>
</Modal>

<ConfirmDialog
  bind:open={deleteDialogOpen}
  title="Delete Metric"
  variant="danger"
  message="Delete &quot;{metricToDelete?.name}&quot; and all its entries? This cannot be undone."
  confirmLabel="Delete"
  onconfirm={confirmDeleteMetric}
  oncancel={() => {
    metricToDelete = null;
  }}
/>
