<script lang="ts">
  import { todayString } from '$lib/utils/datetime';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import DashboardDateBar from '$components/dashboard/DashboardDateBar.svelte';
  import DynamicWidgetGroup from '$components/dashboard/DynamicWidgetGroup.svelte';
  import WidgetRenderer from '$components/dashboard/WidgetRenderer.svelte';
  import WidgetGalleryModal from '$components/dashboard/WidgetGalleryModal.svelte';
  import WidgetGroupEditorModal from '$components/dashboard/WidgetGroupEditorModal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import {
    DEFAULT_DASHBOARD_ITEMS,
    type DashboardItem,
    type DashboardWidget,
    type DashboardWidgetGroup
  } from '$lib/types/widget-groups';

  const DASHBOARD_STORAGE_KEY = 'salus_dashboard_layout_v2';

  let selectedDate = $state(todayString());
  let isEditMode = $state(false);

  // 1. Reactive Dexie Query for Selected Date (Bounded Time Window)
  const dayQuery = useQuery(
    async () => {
      const dayStart = new Date(selectedDate + 'T00:00:00').toISOString();
      const dayEnd = new Date(selectedDate + 'T23:59:59.999').toISOString();

      const [allMeasurements, allHabits, allHabitLogs] = await Promise.all([
        db.measurement.where('start_time').between(dayStart, dayEnd).toArray(),
        db.habit.toArray(),
        db.habit_log.where('log_date').equals(selectedDate).toArray()
      ]);

      const validM = allMeasurements.filter((m) => !m.deleted_at);
      const metricsMap = new Map<string, number>();
      for (const m of validM) {
        if (m.metric_code && m.value_numeric != null) {
          metricsMap.set(m.metric_code, m.value_numeric);
        }
      }

      const activeHabits = allHabits.filter((h) => !h.deleted_at && !h.is_archived);
      const doneHabits = allHabitLogs.filter((l) => !l.deleted_at && l.completed).length;

      return {
        metricsMap,
        steps: metricsMap.get('steps') ?? 0,
        hydration: metricsMap.get('hydration') ?? 0,
        habitsDone: doneHabits,
        habitsTotal: activeHabits.length
      };
    },
    () => selectedDate
  );

  const liveData = $derived(dayQuery.value);
  const liveMetrics = $derived(liveData?.metricsMap);
  const waterAmount = $derived(liveData?.hydration ?? 0);

  // Modals State
  let isGalleryOpen = $state(false);
  let isGroupEditorOpen = $state(false);
  let activeGroupForGallery = $state<DashboardWidgetGroup | null>(null);
  let activeGroupForEdit = $state<DashboardWidgetGroup | null>(null);
  let isCreatingNewGroup = $state(false);

  function loadInitialItems(): DashboardItem[] {
    if (typeof localStorage === 'undefined') return DEFAULT_DASHBOARD_ITEMS;
    try {
      const saved = localStorage.getItem(DASHBOARD_STORAGE_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch {
      // Fallback
    }
    return DEFAULT_DASHBOARD_ITEMS;
  }

  let dashboardItems = $state<DashboardItem[]>(loadInitialItems());

  function persistDashboard(items: DashboardItem[]) {
    if (typeof localStorage === 'undefined') return;
    try {
      localStorage.setItem(DASHBOARD_STORAGE_KEY, JSON.stringify(items));
    } catch {
      // Silently ignore
    }
  }

  $effect(() => {
    persistDashboard(dashboardItems);
  });

  // Open Gallery for a specific Group
  function openGalleryForGroup(group: DashboardWidgetGroup) {
    activeGroupForGallery = group;
    isGalleryOpen = true;
  }

  // Open Gallery for Dashboard Root
  function openRootGallery() {
    activeGroupForGallery = null;
    isGalleryOpen = true;
  }

  function handleAddWidget(widget: DashboardWidget, targetGroupId: string | null) {
    if (targetGroupId) {
      for (const item of dashboardItems) {
        if (item.kind === 'group' && item.group.id === targetGroupId) {
          item.group.widgets = [...item.group.widgets, widget];
          dashboardItems = [...dashboardItems];
          return;
        }
      }
    } else {
      const newItem: DashboardItem = {
        id: `item_${Date.now()}`,
        kind: 'widget',
        widget
      };
      dashboardItems = [...dashboardItems, newItem];
    }
  }

  function handleRemoveRootItem(itemId: string) {
    dashboardItems = dashboardItems.filter((item) => item.id !== itemId);
  }

  function handleRemoveGroupWidget(groupId: string, widgetId: string) {
    for (const item of dashboardItems) {
      if (item.kind === 'group' && item.group.id === groupId) {
        item.group.widgets = item.group.widgets.filter((w) => w.id !== widgetId);
        dashboardItems = [...dashboardItems];
        return;
      }
    }
  }

  function openEditGroup(group: DashboardWidgetGroup) {
    activeGroupForEdit = group;
    isCreatingNewGroup = false;
    isGroupEditorOpen = true;
  }

  function openCreateGroup() {
    activeGroupForEdit = {
      id: `grp_${Date.now()}`,
      title: 'Neue Gruppe',
      subtitle: '',
      columns: 2,
      widgets: []
    };
    isCreatingNewGroup = true;
    isGroupEditorOpen = true;
  }

  function handleSaveGroup(savedGroup: DashboardWidgetGroup) {
    if (isCreatingNewGroup) {
      const newItem: DashboardItem = {
        id: `item_${savedGroup.id}`,
        kind: 'group',
        group: savedGroup
      };
      dashboardItems = [...dashboardItems, newItem];
    } else {
      const idx = dashboardItems.findIndex(
        (item) => item.kind === 'group' && item.group.id === savedGroup.id
      );
      if (idx !== -1) {
        dashboardItems[idx] = {
          id: dashboardItems[idx].id,
          kind: 'group',
          group: savedGroup
        };
        dashboardItems = [...dashboardItems];
      }
    }
  }

  function handleDeleteGroup(groupId: string) {
    dashboardItems = dashboardItems.filter(
      (item) => !(item.kind === 'group' && item.group.id === groupId)
    );
  }

  function moveItemUp(index: number) {
    if (index <= 0) return;
    const item = dashboardItems[index];
    const newArr = [...dashboardItems];
    newArr.splice(index, 1);
    newArr.splice(index - 1, 0, item);
    dashboardItems = newArr;
  }

  function moveItemDown(index: number) {
    if (index >= dashboardItems.length - 1) return;
    const item = dashboardItems[index];
    const newArr = [...dashboardItems];
    newArr.splice(index, 1);
    newArr.splice(index + 1, 0, item);
    dashboardItems = newArr;
  }

  function resetDashboardLayout() {
    dashboardItems = DEFAULT_DASHBOARD_ITEMS;
    persistDashboard(DEFAULT_DASHBOARD_ITEMS);
    isEditMode = false;
  }
</script>

<div class="mx-auto max-w-7xl space-y-6">
  <!-- 1. DATE NAVIGATOR & EDIT MODE CONTROLS -->
  <DashboardDateBar
    bind:selectedDate
    {isEditMode}
    ontoggleedit={() => (isEditMode = !isEditMode)}
    onaddwidget={openRootGallery}
    onreset={resetDashboardLayout}
  />

  <!-- 2. DYNAMIC USER DASHBOARD (Loose Standalone Widgets + Visual Groups) -->
  <div class="space-y-6">
    {#each dashboardItems as item, idx (item.id)}
      <!-- CASE A: Standalone Loose Widget on Dashboard Canvas -->
      {#if item.kind === 'widget'}
        <div
          class="relative mb-5 transition-transform {isEditMode
            ? idx % 2 === 0
              ? 'ios-wiggle-even'
              : 'ios-wiggle-odd'
            : ''}"
        >
          {#if isEditMode}
            <button
              type="button"
              onclick={() => handleRemoveRootItem(item.id)}
              class="animate-fade-in absolute -top-2 -right-2 z-30 flex h-6 w-6 cursor-pointer items-center justify-center rounded-full border-2 border-[var(--bg-canvas)] bg-rose-500 text-sm font-extrabold text-white shadow-lg transition-transform hover:scale-110 active:scale-95"
              title="Widget entfernen"
              aria-label="Widget entfernen"
            >
              &times;
            </button>
          {/if}

          <WidgetRenderer
            widget={item.widget}
            {waterAmount}
            {liveMetrics}
            onopenfasting={() => goto('/fasting')}
          />
        </div>

        <!-- CASE B: Visual Group Container -->
      {:else if item.kind === 'group'}
        <DynamicWidgetGroup
          group={item.group}
          {isEditMode}
          {waterAmount}
          {liveMetrics}
          onopenfasting={() => goto('/fasting')}
          oneditgroup={openEditGroup}
          onaddwidget={openGalleryForGroup}
          onremovewidget={handleRemoveGroupWidget}
          onmoveup={() => moveItemUp(idx)}
          onmovedown={() => moveItemDown(idx)}
          ondeletegroup={() => handleDeleteGroup(item.group.id)}
        />
      {/if}
    {/each}

    <!-- Bottom Add Dropzone Card (in Edit Mode) -->
    {#if isEditMode}
      <button
        type="button"
        onclick={openRootGallery}
        class="group flex min-h-[90px] w-full cursor-pointer items-center justify-center gap-3 rounded-3xl border-2 border-dashed border-[var(--border-subtle)] bg-[var(--bg-surface-0)]/20 p-4 text-[var(--text-muted)] shadow-xs transition-all hover:border-[var(--color-primary)] hover:bg-[var(--color-primary-soft)] hover:text-[var(--color-primary)]"
      >
        <div
          class="flex h-8 w-8 items-center justify-center rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-base font-bold transition-all group-hover:bg-[var(--color-primary)] group-hover:text-white"
        >
          +
        </div>
        <span
          class="text-xs font-bold text-[var(--text-main)] group-hover:text-[var(--color-primary)]"
        >
          Weiteres Widget oder neue Gruppe zum Dashboard hinzufügen
        </span>
      </button>
    {/if}
  </div>

  {#if dashboardItems.length === 0}
    <div
      class="space-y-3 rounded-3xl border-2 border-dashed border-[var(--border-subtle)] p-12 text-center"
    >
      <p class="text-sm text-[var(--text-muted)]">Dein Dashboard ist leer.</p>
      <Btn variant="primary" onclick={openRootGallery}>+ Erstes Element hinzufügen</Btn>
    </div>
  {/if}
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!-- MODALS: WIDGET GALLERY & GROUP EDITOR                              -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<WidgetGalleryModal
  open={isGalleryOpen}
  targetGroup={activeGroupForGallery}
  onclose={() => (isGalleryOpen = false)}
  onaddwidget={handleAddWidget}
  oncreategroup={openCreateGroup}
/>

<WidgetGroupEditorModal
  open={isGroupEditorOpen}
  group={activeGroupForEdit}
  isNew={isCreatingNewGroup}
  onclose={() => (isGroupEditorOpen = false)}
  onsave={handleSaveGroup}
/>
