<script lang="ts">
  import { liveQuery } from 'dexie';
  import Sortable from 'sortablejs';
  import { onDestroy } from 'svelte';
  import { db } from '$lib/db/database';
  import {
    addWidget as addWidgetMut,
    updateWidget as updateWidgetMut,
    deleteWidget as deleteWidgetMut
  } from '$lib/mutations/dashboard';
  import {
    fetchDashboard,
    type DashboardWidgetView,
    type DashboardData
  } from '$lib/analytics/views/dashboard';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Select from '$components/ui/Select.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import ChromeCard from '$components/ui/ChromeCard.svelte';
  import DayNavigator from '$components/ui/DayNavigator.svelte';
  import VizBar from '$components/dashboard/VizBar.svelte';
  import VizCandlestick from '$components/dashboard/VizCandlestick.svelte';
  import VizNumber from '$components/dashboard/VizNumber.svelte';
  import VizPills from '$components/dashboard/VizPills.svelte';
  import VizProgress from '$components/dashboard/VizProgress.svelte';
  import VizSparkline from '$components/dashboard/VizSparkline.svelte';

  let displayDate = $state(new Date().toISOString().split('T')[0]);
  let displayDateFormatted = $state(
    new Date().toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    })
  );
  const isToday = $derived(displayDate === new Date().toISOString().split('T')[0]);

  let dashboardData = liveQuery(() => fetchDashboard(displayDate));

  let editing = $state(false);
  let addModalOpen = $state(false);
  let selectedMetricId = $state('');
  let selectedSize = $state('medium');
  let adding = $state(false);

  let editModalOpen = $state(false);
  let editWidget: DashboardWidgetView | null = $state(null);
  let editSize = $state('medium');
  let editSaving = $state(false);

  let deleteConfirmOpen = $state(false);
  let deleteWidgetId = $state<string | null>(null);

  let gridEl: HTMLElement | null = $state(null);
  let sortableInstance: Sortable | null = null;

  let widgets = $derived($dashboardData?.widgets ?? []);
  let metrics = $derived($dashboardData?.metrics ?? []);

  function setDate(d: Date) {
    displayDate = d.toISOString().split('T')[0];
    displayDateFormatted = d.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  }

  function handleDateChange(dateStr: string) {
    const d = new Date(dateStr + 'T00:00:00');
    setDate(d);
  }

  async function addWidget() {
    if (!selectedMetricId) return;
    adding = true;
    try {
      await addWidgetMut(selectedMetricId, selectedSize, widgets.length);
      addModalOpen = false;
      selectedMetricId = '';
    } catch {
      /* error */
    }
    adding = false;
  }

  async function removeWidget(id: string) {
    await deleteWidgetMut(id);
  }

  async function updateWidgetSize() {
    if (!editWidget) return;
    editSaving = true;
    try {
      await updateWidgetMut(editWidget.id, { size: editSize });
      editModalOpen = false;
      editWidget = null;
    } catch {
      /* error */
    }
    editSaving = false;
  }

  async function reorderWidgets(newOrder: string[]) {
    const updates = newOrder.map((id, idx) => updateWidgetMut(id, { position: idx }));
    await Promise.all(updates);
  }

  function toggleEdit() {
    editing = !editing;
  }

  function openEditModal(w: DashboardWidgetView) {
    editWidget = w;
    editSize = w.size;
    editModalOpen = true;
  }

  function confirmDelete() {
    if (deleteWidgetId !== null) {
      removeWidget(deleteWidgetId);
      deleteWidgetId = null;
      deleteConfirmOpen = false;
    }
  }

  function initSortable() {
    if (!gridEl) return;
    if (sortableInstance) sortableInstance.destroy();
    sortableInstance = Sortable.create(gridEl, {
      handle: '.widget-chrome-handle',
      filter: '.edit-chrome-actions',
      preventOnFilter: false,
      animation: 150,
      ghostClass: 'widget-grid__ghost',
      touchStartThreshold: 10,
      onEnd: (evt) => {
        if (evt.oldIndex === evt.newIndex) return;
        const reordered = [...widgets];
        const [moved] = reordered.splice(evt.oldIndex!, 1);
        reordered.splice(evt.newIndex!, 0, moved);
        reorderWidgets(reordered.map((w) => w.id));
      }
    });
  }

  $effect(() => {
    if (gridEl && editing) {
      initSortable();
    } else if (sortableInstance && !editing) {
      sortableInstance.destroy();
      sortableInstance = null;
    }
  });

  onDestroy(() => {
    if (sortableInstance) sortableInstance.destroy();
  });

  const metricOptions = $derived(
    (metrics ?? [])
      .filter((m) => !widgets.some((w) => w.metric_type_id === m.id))
      .map((m) => ({ value: String(m.id), label: m.name }))
  );

  let loading = $derived($dashboardData == null);
</script>

<svelte:head><title>Salus — Dashboard</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Dashboard"
    subtitle="Personal health overview and activity tracker"
    icon="dashboard"
    iconColor="#4f46e5"
  >
    {#snippet actions()}
      <div class="flex flex-wrap items-center gap-4">
        <DayNavigator
          dateDisplay={displayDateFormatted}
          onPrev={() => setDate(new Date(new Date(displayDate).getTime() - 86400000))}
          onNext={() => setDate(new Date(new Date(displayDate).getTime() + 86400000))}
          onDateChange={handleDateChange}
          {isToday}
        />

        <div class="flex items-center gap-2">
          <Btn variant={editing ? 'primary' : 'secondary'} size="sm" onclick={toggleEdit}>
            {editing ? 'Done' : 'Edit Layout'}
          </Btn>
          {#if editing}
            <Btn variant="secondary" size="sm" onclick={() => (addModalOpen = true)}>
              <Icon name="add" size="sm" />Add Widget
            </Btn>
          {/if}
        </div>
      </div>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-6">
      {#each Array(4) as _, i (i)}
        <div class="overflow-hidden rounded-lg border border-surface-200 bg-surface-0">
          <div class="border-b border-surface-100 px-3 py-2">
            <div class="h-3 w-24 animate-pulse rounded bg-surface-100"></div>
          </div>
          <div class="min-h-[80px] space-y-3 px-4 pt-2 pb-4">
            <div class="h-8 w-16 animate-pulse rounded bg-surface-100"></div>
            <div class="h-20 w-full animate-pulse rounded bg-surface-100"></div>
          </div>
        </div>
      {/each}
    </div>
  {:else if widgets.length === 0}
    <EmptyState
      icon="dashboard"
      title="No widgets yet"
      description="Add widgets to start tracking your health data on the dashboard."
    >
      <Btn variant="primary" size="sm" onclick={() => (addModalOpen = true)}>+ Add Widget</Btn>
    </EmptyState>
  {:else}
    <div
      bind:this={gridEl}
      class="duration-micro grid grid-cols-1 gap-4 transition-opacity sm:grid-cols-3 lg:grid-cols-6 {editing
        ? 'rounded-lg bg-surface-100 p-2 ring-1 ring-primary-200'
        : ''}"
    >
      {#each widgets as widget (widget.id)}
        {@const viz = widget.viz}
        <ChromeCard
          title={viz.title}
          icon={undefined}
          iconColor={viz.color ?? undefined}
          unit={viz.unit ?? undefined}
          editMode={editing}
          dragHandle={editing}
          dense
          class={widget.size === 'large'
            ? 'lg:col-span-6'
            : widget.size === 'medium'
              ? 'lg:col-span-3'
              : 'lg:col-span-2'}
        >
          {#snippet editActions()}
            <button
              class="duration-micro flex h-7 w-7 items-center justify-center rounded-md text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-600"
              onclick={() => openEditModal(widget)}
              aria-label="Edit widget size"
            >
              <Icon name="tune" size="sm" />
            </button>
            <button
              class="duration-micro flex h-7 w-7 items-center justify-center rounded-md text-surface-400 transition-colors hover:bg-error-50 hover:text-error-500"
              onclick={() => {
                deleteWidgetId = widget.id;
                deleteConfirmOpen = true;
              }}
              aria-label="Remove widget"
            >
              <Icon name="delete" size="sm" />
            </button>
          {/snippet}

          {#if viz.empty}
            <div class="flex min-h-[60px] items-center justify-center py-6 text-center">
              <span class="max-w-[240px] text-sm text-surface-500">
                {viz.empty_text ?? 'No data'}
              </span>
            </div>
          {:else if viz.type === 'number'}
            <VizNumber
              value={viz.value ?? '—'}
              unit={viz.unit ?? undefined}
              subLabel={viz.subtitle ?? undefined}
              color={viz.color ?? undefined}
              animate={true}
            />
          {:else if viz.type === 'progress'}
            <VizProgress
              value={Number(viz.value) || 0}
              target={viz.goal_target ?? undefined}
              unit={viz.unit ?? undefined}
              color={viz.color ?? undefined}
              showPercent={true}
            />
          {:else if viz.type === 'pills'}
            <VizPills
              items={viz.segments as
                { label: string; value: number; unit?: string; color?: string }[] | undefined}
            />
          {:else if viz.type === 'bar'}
            <VizBar
              segments={viz.segments as
                { label: string; value: number; color: string }[] | undefined}
            />
          {:else if viz.type === 'sparkline'}
            <VizSparkline
              value={viz.value ?? '—'}
              unit={viz.unit ?? undefined}
              points={viz.sparkline_path ?? undefined}
              color={viz.color ?? undefined}
            />
          {:else if viz.type === 'candlestick'}
            <VizCandlestick data={undefined} color={viz.color ?? undefined} />
          {:else}
            <VizNumber
              value={viz.value ?? '—'}
              unit={viz.unit ?? undefined}
              color={viz.color ?? undefined}
              animate={true}
            />
          {/if}
        </ChromeCard>
      {/each}
    </div>
  {/if}
</div>

<Modal title="Add Widget" bind:open={addModalOpen}>
  <div class="space-y-4">
    {#if metricOptions.length > 0}
      <Select name="metric" label="Metric" options={metricOptions} bind:value={selectedMetricId} />
      <Select
        name="size"
        label="Size"
        options={[
          { value: 'small', label: 'Small (1 column)' },
          { value: 'medium', label: 'Medium (2 columns)' },
          { value: 'large', label: 'Large (4 columns)' }
        ]}
        bind:value={selectedSize}
      />
      <div class="flex justify-end gap-2">
        <Btn variant="ghost" onclick={() => (addModalOpen = false)}>Cancel</Btn>
        <Btn variant="primary" loading={adding} onclick={addWidget}>Add</Btn>
      </div>
    {:else}
      <EmptyState
        icon="dashboard"
        title="All metrics added"
        description="Every metric already has a widget on your dashboard."
      />
    {/if}
  </div>
</Modal>

<Modal title="Edit Widget Size" bind:open={editModalOpen}>
  <div class="space-y-4">
    <Select
      name="edit-size"
      label="Size"
      options={[
        { value: 'small', label: 'Small (1 column)' },
        { value: 'medium', label: 'Medium (2 columns)' },
        { value: 'large', label: 'Large (4 columns)' }
      ]}
      bind:value={editSize}
    />
    <div class="flex justify-end gap-2">
      <Btn variant="ghost" onclick={() => (editModalOpen = false)}>Cancel</Btn>
      <Btn variant="primary" loading={editSaving} onclick={updateWidgetSize}>Save</Btn>
    </div>
  </div>
</Modal>

<ConfirmDialog
  bind:open={deleteConfirmOpen}
  title="Remove Widget"
  variant="danger"
  message="Remove this widget from your dashboard? The metric and its data will not be deleted."
  confirmLabel="Remove"
  onconfirm={confirmDelete}
  oncancel={() => {
    deleteWidgetId = null;
    deleteConfirmOpen = false;
  }}
/>
