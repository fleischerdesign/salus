<script lang="ts">
  import { liveQuery } from 'dexie';
  import Sortable from 'sortablejs';
  import { onDestroy } from 'svelte';
  import { slide } from 'svelte/transition';
  import {
    addWidget as addWidgetMut,
    updateWidget as updateWidgetMut,
    deleteWidget as deleteWidgetMut
  } from '$lib/mutations/dashboard';
  import { fetchDashboard, type DashboardWidgetView } from '$lib/analytics/views/dashboard';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Select from '$components/ui/Select.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import ChromeCard from '$components/ui/ChromeCard.svelte';
  import Tabs from '$components/ui/Tabs.svelte';
  import VizBar from '$components/dashboard/VizBar.svelte';
  import VizCandlestick from '$components/dashboard/VizCandlestick.svelte';
  import VizNumber from '$components/dashboard/VizNumber.svelte';
  import VizPills from '$components/dashboard/VizPills.svelte';
  import VizProgress from '$components/dashboard/VizProgress.svelte';
  import VizSparkline from '$components/dashboard/VizSparkline.svelte';
  import VizWorkoutLauncher from '$components/dashboard/VizWorkoutLauncher.svelte';
  import VizSleepCoach from '$components/dashboard/VizSleepCoach.svelte';
  import VizWater from '$components/dashboard/VizWater.svelte';
  import VizCircadian from '$components/dashboard/VizCircadian.svelte';
  import VizLineChart from '$components/dashboard/VizLineChart.svelte';

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
  let widgetType = $state<'metric' | 'custom'>('metric');
  let selectedWidgetId = $state('');
  let selectedSize = $state<'small' | 'medium' | 'large'>('medium');
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
    if (!selectedWidgetId) return;
    adding = true;
    try {
      if (widgetType === 'metric') {
        await addWidgetMut('metric', selectedWidgetId, selectedSize, widgets.length);
      } else {
        await addWidgetMut(selectedWidgetId, null, 'medium', widgets.length);
      }
      addModalOpen = false;
      selectedWidgetId = '';
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

  const availableMetrics = $derived(
    (metrics ?? [])
      .filter((m) => !widgets.some((w) => w.metric_code === m.code))
      .map((m) => ({
        id: String(m.code),
        name: m.name,
        description:
          m.source_data_type === 'steps'
            ? 'Track daily step counts, progress towards goals, and walking trends.'
            : m.source_data_type === 'heart_rate'
              ? 'Monitor pulse, resting heart rate, and recovery metrics.'
              : m.source_data_type === 'sleep'
                ? 'Analyze sleep cycles, sleep duration, and rest hygiene.'
                : m.source_data_type === 'weight'
                  ? 'Monitor body weight fluctuations and BMI trends.'
                  : m.source_data_type === 'blood_pressure'
                    ? 'Track systolic and diastolic arterial pressure trends.'
                    : 'Track values and log measurements over time.',
        icon: m.icon || 'monitoring',
        color: m.color || '#64748b',
        source_data_type: m.source_data_type
      }))
  );

  const availableCustoms = $derived(
    [
      {
        id: 'workout_launcher',
        name: 'Workout Launcher',
        description: 'Start workout routines and log active sets directly in real-time.',
        icon: 'play-arrow',
        color: '#6366f1',
        source_data_type: 'workout_launcher'
      },
      {
        id: 'sleep_coach',
        name: 'Sleep Coach',
        description: 'Track cumulative sleep debt and get ideal wind-down bedtime recommendations.',
        icon: 'psychology',
        color: '#4f46e5',
        source_data_type: 'sleep_coach'
      },
      {
        id: 'water_logger',
        name: 'Water Intake',
        description: 'Track hydration and log water consumption directly from your dashboard.',
        icon: 'water-drop',
        color: '#06b6d4',
        source_data_type: 'water_logger'
      },
      {
        id: 'circadian_timeline',
        name: 'Circadian Timeline',
        description:
          'Monitor optimal sun light windows, caffeine cuts, and wind-down phases today.',
        icon: 'routine',
        color: '#f59e0b',
        source_data_type: 'circadian_timeline'
      }
    ].filter((opt) => !widgets.some((w) => w.widget_type === opt.id))
  );

  $effect(() => {
    // Keep category toggle changes in sync with selection
    if (widgetType === 'metric') {
      const first = availableMetrics[0];
      selectedWidgetId = first ? first.id : '';
    } else {
      const first = availableCustoms[0];
      selectedWidgetId = first ? first.id : '';
    }
  });

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
      <div class="flex h-full items-stretch divide-x divide-surface-200 select-none">
        <!-- Date Navigator Segment -->
        <div class="flex h-full items-center gap-2 px-6">
          <button
            class="duration-micro flex h-8 w-8 items-center justify-center rounded-full text-surface-500 transition-colors hover:bg-surface-200 hover:text-surface-700"
            onclick={() => setDate(new Date(new Date(displayDate).getTime() - 86400000))}
            aria-label="Previous day"
            type="button"
          >
            <Icon name="chevron-left" />
          </button>

          <button
            class="duration-micro cursor-pointer px-2 text-sm font-semibold tracking-[0.05em] text-surface-700 transition-colors hover:text-primary-600"
            type="button"
            onclick={() => {
              const input = document.getElementById('dash-hidden-date') as HTMLInputElement;
              input?.showPicker();
            }}
          >
            {displayDateFormatted}
          </button>
          <input
            id="dash-hidden-date"
            type="date"
            class="sr-only"
            onchange={(e) => handleDateChange((e.target as HTMLInputElement).value)}
          />

          <button
            class="duration-micro flex h-8 w-8 items-center justify-center rounded-full text-surface-500 transition-colors hover:bg-surface-200 hover:text-surface-700"
            onclick={() => setDate(new Date(new Date(displayDate).getTime() + 86400000))}
            aria-label="Next day"
            type="button"
          >
            <Icon name="chevron-right" />
          </button>

          {#if !isToday}
            <button
              type="button"
              class="ml-1 rounded bg-primary-50 px-1.5 py-0.5 text-[10px] font-semibold text-primary-600 transition-colors hover:text-primary-700"
              onclick={() => handleDateChange(new Date().toISOString().split('T')[0])}
            >
              Today
            </button>
          {/if}
        </div>

        <!-- Edit Layout Segment -->
        <button
          type="button"
          class="duration-micro flex h-full items-center justify-center gap-2 px-6 text-sm font-semibold text-surface-700 transition-colors hover:bg-surface-100"
          class:bg-primary-50={editing}
          class:text-primary-600={editing}
          onclick={toggleEdit}
        >
          <Icon
            name={editing ? 'check' : 'edit'}
            size="sm"
            class={editing ? 'text-primary-600' : ''}
          />
          <span>{editing ? 'Done' : 'Edit Layout'}</span>
        </button>

        <!-- Add Widget Segment -->
        {#if editing}
          <button
            type="button"
            transition:slide={{ axis: 'x', duration: 150 }}
            class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white transition-colors hover:bg-primary-600 active:bg-primary-700"
            onclick={() => (addModalOpen = true)}
          >
            <Icon name="add" size="sm" />
            <span>Add Widget</span>
          </button>
        {/if}
      </div>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-6">
      <!-- eslint-disable-next-line @typescript-eslint/no-unused-vars -->
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
          {:else if viz.type === 'workout_launcher'}
            <VizWorkoutLauncher />
          {:else if viz.type === 'sleep_coach'}
            <VizSleepCoach />
          {:else if viz.type === 'water_logger'}
            <VizWater />
          {:else if viz.type === 'circadian_timeline'}
            <VizCircadian />
          {:else if viz.type === 'line_chart'}
            <VizLineChart
              labels={viz.labels ?? []}
              series={(viz.series ?? []) as { label: string; data: number[]; color: string }[]}
              unit={viz.unit ?? undefined}
            />
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
  <div class="space-y-6">
    <!-- Category Tabs -->
    <Tabs
      tabs={[
        { key: 'metric', label: `Standard Metrics (${availableMetrics.length})` },
        { key: 'custom', label: `Coaching & Actions (${availableCustoms.length})` }
      ]}
      bind:activeTab={widgetType}
    />

    <!-- Catalog Grid -->
    {#if widgetType === 'metric'}
      {#if availableMetrics.length > 0}
        <div class="max-h-[340px] overflow-y-auto pr-1">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {#each availableMetrics as opt}
              <button
                type="button"
                class="group relative flex flex-col justify-between overflow-hidden rounded-xl border border-surface-200 bg-surface-50 p-4 text-left transition-all hover:border-primary-300 hover:bg-surface-0 hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
                class:border-primary-500={selectedWidgetId === opt.id}
                class:bg-surface-0={selectedWidgetId === opt.id}
                class:shadow-sm={selectedWidgetId === opt.id}
                class:ring-1={selectedWidgetId === opt.id}
                class:ring-primary-500={selectedWidgetId === opt.id}
                onclick={() => (selectedWidgetId = opt.id)}
              >
                <!-- Mini Preview Area -->
                <div
                  class="mb-3 flex h-24 w-full items-center justify-center overflow-hidden rounded-lg bg-surface-100/50 p-2 select-none"
                >
                  {#if opt.source_data_type === 'steps'}
                    <div class="flex w-full flex-col justify-center gap-2 px-2 opacity-80">
                      <div class="flex items-baseline justify-between text-[10px]">
                        <span class="font-bold text-amber-500">8,432</span>
                        <span class="text-surface-400">/ 10k</span>
                      </div>
                      <div class="h-2 w-full overflow-hidden rounded-full bg-surface-200">
                        <div class="h-full rounded-full bg-amber-500" style="width: 84%"></div>
                      </div>
                    </div>
                  {:else if opt.source_data_type === 'heart_rate'}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-1 text-center opacity-80"
                    >
                      <Icon name="monitor-heart" size="lg" class="text-rose-500" />
                      <span class="text-xs font-bold text-rose-600">72 bpm</span>
                    </div>
                  {:else if opt.source_data_type === 'sleep'}
                    <div class="flex h-12 w-full items-end justify-center gap-1.5 opacity-80">
                      <div class="h-4 w-4 rounded-t bg-indigo-500/40"></div>
                      <div class="h-8 w-4 rounded-t bg-indigo-500/70"></div>
                      <div class="h-12 w-4 rounded-t bg-indigo-500"></div>
                    </div>
                  {:else if opt.source_data_type === 'weight'}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-1 text-center opacity-80"
                    >
                      <span class="text-xs font-bold text-emerald-600">78.5 kg</span>
                      <div class="flex h-4 items-end justify-center gap-0.5">
                        <div class="h-3 w-1 bg-emerald-500/30"></div>
                        <div class="h-2.5 w-1 bg-emerald-500/50"></div>
                        <div class="h-2 w-1 bg-emerald-500/70"></div>
                        <div class="h-1.5 w-1 bg-emerald-500"></div>
                      </div>
                    </div>
                  {:else if opt.source_data_type === 'blood_pressure'}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-0.5 text-center opacity-80"
                    >
                      <Icon name="vital-signs" size="lg" class="text-red-500" />
                      <span class="text-xs font-bold text-red-600">120 / 80</span>
                      <span class="text-[9px] text-surface-400">mmHg</span>
                    </div>
                  {:else if opt.source_data_type === 'exercise'}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-0.5 text-center opacity-80"
                    >
                      <Icon name="fitness-center" size="lg" class="text-violet-500" />
                      <span class="text-xs font-bold text-violet-600">45 mins</span>
                      <span class="text-[9px] text-surface-400">320 kcal</span>
                    </div>
                  {:else if opt.source_data_type === 'nutrition'}
                    <div class="flex w-full flex-col justify-center gap-1 px-2 opacity-80">
                      <div class="flex items-baseline justify-between text-[10px]">
                        <span class="font-bold text-emerald-600">2,100</span>
                        <span class="text-surface-400">kcal</span>
                      </div>
                      <div
                        class="flex h-1.5 w-full gap-0.5 overflow-hidden rounded-full bg-surface-200"
                      >
                        <div class="h-full bg-amber-500" style="width: 40%"></div>
                        <div class="h-full bg-red-500" style="width: 30%"></div>
                        <div class="h-full bg-emerald-500" style="width: 30%"></div>
                      </div>
                    </div>
                  {:else if opt.source_data_type === 'blood_glucose'}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-0.5 text-center opacity-80"
                    >
                      <Icon name="bloodtype" size="lg" class="text-orange-500" />
                      <span class="text-xs font-bold text-orange-600">95 mg/dL</span>
                    </div>
                  {:else if opt.source_data_type === 'body_fat'}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-0.5 text-center opacity-80"
                    >
                      <Icon name="body-fat" size="lg" class="text-pink-500" />
                      <span class="text-xs font-bold text-pink-600">14.5 %</span>
                    </div>
                  {:else if opt.source_data_type === 'water'}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-0.5 text-center opacity-80"
                    >
                      <Icon name="water-drop" size="lg" class="text-cyan-500" />
                      <span class="text-xs font-bold text-cyan-600">850 ml</span>
                    </div>
                  {:else if opt.source_data_type === 'stress'}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-0.5 text-center opacity-80"
                    >
                      <Icon name="psychology" size="lg" class="text-rose-500" />
                      <span class="text-xs font-bold text-rose-600">Low (18)</span>
                    </div>
                  {:else if opt.source_data_type === 'hrv'}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-0.5 text-center opacity-80"
                    >
                      <Icon name="monitoring" size="lg" class="text-cyan-500" />
                      <span class="text-xs font-bold text-cyan-600">58 ms</span>
                    </div>
                  {:else if opt.source_data_type === 'readiness'}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-0.5 text-center opacity-80"
                    >
                      <Icon name="checklist" size="lg" class="text-purple-500" />
                      <span class="text-xs font-bold text-purple-600">85 / 100</span>
                    </div>
                  {:else}
                    <div
                      class="flex w-full flex-col items-center justify-center gap-1 text-center opacity-80"
                    >
                      <Icon name="show-chart" size="lg" class="text-surface-400" />
                      <span class="text-xs font-bold text-surface-600">72.0</span>
                    </div>
                  {/if}
                </div>

                <!-- Info Area -->
                <div class="w-full">
                  <div class="flex items-center gap-1.5">
                    <Icon name={opt.icon} size="sm" style="color: {opt.color}" />
                    <span class="text-sm leading-none font-bold text-surface-900">{opt.name}</span>
                  </div>
                  <p class="mt-1 line-clamp-2 text-[11px] leading-snug text-surface-500">
                    {opt.description}
                  </p>
                </div>

                <!-- Active Checkmark Indicator -->
                {#if selectedWidgetId === opt.id}
                  <div
                    class="absolute top-2 right-2 flex h-5 w-5 items-center justify-center rounded-full bg-primary-500 text-white shadow-sm ring-2 ring-white"
                  >
                    <Icon name="check" size="sm" />
                  </div>
                {/if}
              </button>
            {/each}
          </div>
        </div>

        <!-- Custom Size Selector for Metrics -->
        <div class="flex flex-col gap-2 rounded-xl border border-surface-100 bg-surface-50 p-4">
          <span class="text-xs font-bold tracking-wider text-surface-500 uppercase"
            >Widget Display Size</span
          >
          <div class="grid grid-cols-3 gap-2">
            {#each [{ value: 'small' as const, label: 'Small', desc: '1 Column' }, { value: 'medium' as const, label: 'Medium', desc: '2 Columns' }, { value: 'large' as const, label: 'Large', desc: 'Full Width' }] as sz}
              <button
                type="button"
                class="flex flex-col items-center justify-center rounded-lg border border-surface-200 bg-surface-0 p-2.5 transition-all hover:bg-surface-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
                class:border-primary-500={selectedSize === sz.value}
                class:ring-1={selectedSize === sz.value}
                class:ring-primary-500={selectedSize === sz.value}
                onclick={() => (selectedSize = sz.value)}
              >
                <span class="text-sm font-semibold text-surface-800">{sz.label}</span>
                <span class="text-[10px] text-surface-400">{sz.desc}</span>
              </button>
            {/each}
          </div>
        </div>

        <div class="flex justify-end gap-2 border-t border-surface-100 pt-4">
          <Btn variant="ghost" onclick={() => (addModalOpen = false)}>Cancel</Btn>
          <Btn variant="primary" loading={adding} onclick={addWidget}>Add to Dashboard</Btn>
        </div>
      {:else}
        <EmptyState
          icon="dashboard"
          title="All metrics added"
          description="Every standard metric already has a widget on your dashboard."
        />
      {/if}
    {:else if availableCustoms.length > 0}
      <div class="max-h-[340px] overflow-y-auto pr-1">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {#each availableCustoms as opt}
            <button
              type="button"
              class="group relative flex flex-col justify-between overflow-hidden rounded-xl border border-surface-200 bg-surface-50 p-4 text-left transition-all hover:border-primary-300 hover:bg-surface-0 hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
              class:border-primary-500={selectedWidgetId === opt.id}
              class:bg-surface-0={selectedWidgetId === opt.id}
              class:shadow-sm={selectedWidgetId === opt.id}
              class:ring-1={selectedWidgetId === opt.id}
              class:ring-primary-500={selectedWidgetId === opt.id}
              onclick={() => (selectedWidgetId = opt.id)}
            >
              <!-- Mini Preview Area -->
              <div
                class="mb-3 flex h-24 w-full items-center justify-center overflow-hidden rounded-lg bg-surface-100/50 p-2 select-none"
              >
                {#if opt.source_data_type === 'workout_launcher'}
                  <div
                    class="flex w-full flex-col items-center justify-center gap-1.5 text-center opacity-80"
                  >
                    <Icon name="play-circle" size="xl" class="animate-pulse text-primary-500" />
                    <div class="h-1.5 w-16 rounded bg-surface-300"></div>
                    <div class="h-3 w-24 rounded bg-primary-500/20"></div>
                  </div>
                {:else if opt.source_data_type === 'sleep_coach'}
                  <div class="flex w-full items-center justify-center gap-3 opacity-80">
                    <div class="flex flex-col items-center">
                      <span class="text-xs font-bold text-error-500">+4.5h</span>
                      <span class="text-[8px] text-surface-400">Debt</span>
                    </div>
                    <div class="h-8 w-px bg-surface-200"></div>
                    <div class="flex flex-col items-center">
                      <span class="text-xs font-bold text-primary-500">09:30</span>
                      <span class="text-[8px] text-surface-400">Wind Down</span>
                    </div>
                  </div>
                {/if}
              </div>

              <!-- Info Area -->
              <div class="w-full">
                <div class="flex items-center gap-1.5">
                  <Icon name={opt.icon} size="sm" style="color: {opt.color}" />
                  <span class="text-sm leading-none font-bold text-surface-900">{opt.name}</span>
                </div>
                <p class="mt-1 line-clamp-2 text-[11px] leading-snug text-surface-500">
                  {opt.description}
                </p>
              </div>

              <!-- Active Checkmark Indicator -->
              {#if selectedWidgetId === opt.id}
                <div
                  class="absolute top-2 right-2 flex h-5 w-5 items-center justify-center rounded-full bg-primary-500 text-white shadow-sm ring-2 ring-white"
                >
                  <Icon name="check" size="sm" />
                </div>
              {/if}
            </button>
          {/each}
        </div>
      </div>

      <div class="flex justify-end gap-2 border-t border-surface-100 pt-4">
        <Btn variant="ghost" onclick={() => (addModalOpen = false)}>Cancel</Btn>
        <Btn variant="primary" loading={adding} onclick={addWidget}>Add to Dashboard</Btn>
      </div>
    {:else}
      <EmptyState
        icon="dashboard"
        title="All custom widgets added"
        description="Every custom coaching widget is already on your dashboard."
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
