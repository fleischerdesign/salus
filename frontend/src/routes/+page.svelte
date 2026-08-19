<script lang="ts">
  import { todayString } from '$lib/utils/datetime';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { mutate } from '$lib/mutate';
  import { uuid7 } from '$lib/db/uuid';
  import { SELF_USER_ID } from '$lib/constants';
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
  import type { DashboardWidget as DbDashboardWidget } from '$lib/db/types';

  let selectedDate = $state(todayString());
  let isEditMode = $state(false);

  // 1. Reactive Dexie Query for Synced Dashboard Widgets
  const widgetsQuery = useQuery(
    async () => {
      const rows = await db.dashboard_widget
        .filter((w) => !w.deleted_at && (w.is_visible ?? true))
        .sortBy('position');
      return rows;
    },
    () => true
  );

  let hasSeeded = $state(false);

  // Auto-seed default dashboard layout into db.dashboard_widget if empty
  $effect(() => {
    const rows = widgetsQuery.value;
    if (rows && rows.length === 0 && !hasSeeded) {
      hasSeeded = true;
      void seedDefaultLayout();
    }
  });

  async function seedDefaultLayout() {
    const now = new Date().toISOString();
    for (let pos = 0; pos < DEFAULT_DASHBOARD_ITEMS.length; pos++) {
      const item = DEFAULT_DASHBOARD_ITEMS[pos];
      const id = uuid7();
      if (item.kind === 'group') {
        const row: DbDashboardWidget = {
          id,
          user_id: SELF_USER_ID,
          widget_type: 'group',
          metric_code: null,
          position: pos,
          size: 'medium',
          config_json: JSON.stringify({
            title: item.group.title,
            subtitle: item.group.subtitle,
            columns: item.group.columns,
            widgets: item.group.widgets
          }),
          is_visible: true,
          created_at: now,
          updated_at: now,
          deleted_at: null
        };
        await mutate({
          kind: 'crud',
          op: 'create',
          entity: 'dashboard_widget',
          id,
          optimistic: row as unknown as Record<string, unknown>
        });
      } else {
        const row: DbDashboardWidget = {
          id,
          user_id: SELF_USER_ID,
          widget_type: item.widget.type,
          metric_code: null,
          position: pos,
          size: item.widget.size === 'full' ? 'large' : 'medium',
          config_json: JSON.stringify({
            title: item.widget.title,
            size: item.widget.size
          }),
          is_visible: true,
          created_at: now,
          updated_at: now,
          deleted_at: null
        };
        await mutate({
          kind: 'crud',
          op: 'create',
          entity: 'dashboard_widget',
          id,
          optimistic: row as unknown as Record<string, unknown>
        });
      }
    }
  }

  // 2. Derive items from synced Dexie table
  let dashboardItems = $derived.by<DashboardItem[]>(() => {
    const rows = widgetsQuery.value;
    if (!rows || rows.length === 0) return [];

    return rows.map((row) => {
      if (row.widget_type === 'group') {
        let groupData: Partial<DashboardWidgetGroup> = {};
        try {
          groupData = JSON.parse(row.config_json || '{}');
        } catch {
          // ignore malformed config json
        }
        return {
          id: row.id,
          kind: 'group',
          group: {
            id: row.id,
            title: groupData.title || 'Gruppe',
            subtitle: groupData.subtitle || '',
            columns: groupData.columns || 2,
            widgets: groupData.widgets || []
          }
        };
      } else {
        let widgetData: Partial<DashboardWidget> = {};
        try {
          widgetData = JSON.parse(row.config_json || '{}');
        } catch {
          // ignore malformed config json
        }
        return {
          id: row.id,
          kind: 'widget',
          widget: {
            id: row.id,
            type: row.widget_type,
            title: widgetData.title || row.widget_type,
            size: widgetData.size || 'full',
            config: widgetData.config
          }
        };
      }
    });
  });

  // Modals State
  let isGalleryOpen = $state(false);
  let isGroupEditorOpen = $state(false);
  let activeGroupForGallery = $state<DashboardWidgetGroup | null>(null);
  let activeGroupForEdit = $state<DashboardWidgetGroup | null>(null);
  let isCreatingNewGroup = $state(false);

  function openGalleryForGroup(group: DashboardWidgetGroup) {
    activeGroupForGallery = group;
    isGalleryOpen = true;
  }

  function openRootGallery() {
    activeGroupForGallery = null;
    isGalleryOpen = true;
  }

  async function handleAddWidget(widget: DashboardWidget, targetGroupId: string | null) {
    const rows = widgetsQuery.value ?? [];
    const now = new Date().toISOString();

    if (targetGroupId) {
      const parentRow = rows.find((r) => r.id === targetGroupId);
      if (parentRow) {
        let groupData: Partial<DashboardWidgetGroup> = {};
        try {
          groupData = JSON.parse(parentRow.config_json || '{}');
        } catch {
          // ignore malformed config json
        }
        const existingWidgets = groupData.widgets || [];
        const updatedWidgets = [...existingWidgets, widget];
        const updatedConfig = JSON.stringify({
          ...groupData,
          widgets: updatedWidgets
        });

        await mutate({
          kind: 'crud',
          op: 'update',
          entity: 'dashboard_widget',
          id: parentRow.id,
          optimistic: {
            ...parentRow,
            config_json: updatedConfig,
            updated_at: now
          }
        });
      }
    } else {
      const id = uuid7();
      const pos = rows.length;
      const newRow: DbDashboardWidget = {
        id,
        user_id: SELF_USER_ID,
        widget_type: widget.type,
        metric_code: null,
        position: pos,
        size: widget.size === 'full' ? 'large' : 'medium',
        config_json: JSON.stringify({
          title: widget.title,
          size: widget.size
        }),
        is_visible: true,
        created_at: now,
        updated_at: now,
        deleted_at: null
      };

      await mutate({
        kind: 'crud',
        op: 'create',
        entity: 'dashboard_widget',
        id,
        optimistic: newRow as unknown as Record<string, unknown>
      });
    }
  }

  async function handleRemoveRootItem(itemId: string) {
    const rows = widgetsQuery.value ?? [];
    const row = rows.find((r) => r.id === itemId);
    if (row) {
      await mutate({
        kind: 'crud',
        op: 'delete',
        entity: 'dashboard_widget',
        id: row.id,
        optimistic: {
          ...row,
          deleted_at: new Date().toISOString()
        }
      });
    }
  }

  async function handleRemoveGroupWidget(groupId: string, widgetId: string) {
    const rows = widgetsQuery.value ?? [];
    const parentRow = rows.find((r) => r.id === groupId);
    if (parentRow) {
      let groupData: Partial<DashboardWidgetGroup> = {};
      try {
        groupData = JSON.parse(parentRow.config_json || '{}');
      } catch {
        // ignore malformed config json
      }
      const existingWidgets = groupData.widgets || [];
      const updatedWidgets = existingWidgets.filter((w) => w.id !== widgetId);
      const updatedConfig = JSON.stringify({
        ...groupData,
        widgets: updatedWidgets
      });

      await mutate({
        kind: 'crud',
        op: 'update',
        entity: 'dashboard_widget',
        id: parentRow.id,
        optimistic: {
          ...parentRow,
          config_json: updatedConfig,
          updated_at: new Date().toISOString()
        }
      });
    }
  }

  function openEditGroup(group: DashboardWidgetGroup) {
    activeGroupForEdit = group;
    isCreatingNewGroup = false;
    isGroupEditorOpen = true;
  }

  function openCreateGroup() {
    activeGroupForEdit = {
      id: uuid7(),
      title: 'Neue Gruppe',
      subtitle: '',
      columns: 2,
      widgets: []
    };
    isCreatingNewGroup = true;
    isGroupEditorOpen = true;
  }

  async function handleSaveGroup(savedGroup: DashboardWidgetGroup) {
    const rows = widgetsQuery.value ?? [];
    const now = new Date().toISOString();

    if (isCreatingNewGroup) {
      const id = savedGroup.id || uuid7();
      const pos = rows.length;
      const newRow: DbDashboardWidget = {
        id,
        user_id: SELF_USER_ID,
        widget_type: 'group',
        metric_code: null,
        position: pos,
        size: 'medium',
        config_json: JSON.stringify({
          title: savedGroup.title,
          subtitle: savedGroup.subtitle,
          columns: savedGroup.columns,
          widgets: savedGroup.widgets
        }),
        is_visible: true,
        created_at: now,
        updated_at: now,
        deleted_at: null
      };

      await mutate({
        kind: 'crud',
        op: 'create',
        entity: 'dashboard_widget',
        id,
        optimistic: newRow as unknown as Record<string, unknown>
      });
    } else {
      const existingRow = rows.find((r) => r.id === savedGroup.id);
      if (existingRow) {
        await mutate({
          kind: 'crud',
          op: 'update',
          entity: 'dashboard_widget',
          id: existingRow.id,
          optimistic: {
            ...existingRow,
            config_json: JSON.stringify({
              title: savedGroup.title,
              subtitle: savedGroup.subtitle,
              columns: savedGroup.columns,
              widgets: savedGroup.widgets
            }),
            updated_at: now
          }
        });
      }
    }
  }

  async function handleDeleteGroup(groupId: string) {
    await handleRemoveRootItem(groupId);
  }

  async function moveItemUp(index: number) {
    if (index <= 0) return;
    const rows = widgetsQuery.value ?? [];
    if (index >= rows.length) return;

    const cur = rows[index];
    const prev = rows[index - 1];

    const curPos = cur.position;
    const prevPos = prev.position;

    await Promise.all([
      mutate({
        kind: 'crud',
        op: 'update',
        entity: 'dashboard_widget',
        id: cur.id,
        optimistic: { ...cur, position: prevPos }
      }),
      mutate({
        kind: 'crud',
        op: 'update',
        entity: 'dashboard_widget',
        id: prev.id,
        optimistic: { ...prev, position: curPos }
      })
    ]);
  }

  async function moveItemDown(index: number) {
    const rows = widgetsQuery.value ?? [];
    if (index >= rows.length - 1) return;

    const cur = rows[index];
    const next = rows[index + 1];

    const curPos = cur.position;
    const nextPos = next.position;

    await Promise.all([
      mutate({
        kind: 'crud',
        op: 'update',
        entity: 'dashboard_widget',
        id: cur.id,
        optimistic: { ...cur, position: nextPos }
      }),
      mutate({
        kind: 'crud',
        op: 'update',
        entity: 'dashboard_widget',
        id: next.id,
        optimistic: { ...next, position: curPos }
      })
    ]);
  }

  async function resetDashboardLayout() {
    const rows = widgetsQuery.value ?? [];
    for (const r of rows) {
      await mutate({
        kind: 'crud',
        op: 'delete',
        entity: 'dashboard_widget',
        id: r.id,
        optimistic: { ...r, deleted_at: new Date().toISOString() }
      });
    }
    await seedDefaultLayout();
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
            date={selectedDate}
            onopen={(r) => goto(r)}
            onopenfasting={() => goto('/fasting')}
          />
        </div>

        <!-- CASE B: Visual Group Container -->
      {:else if item.kind === 'group'}
        <DynamicWidgetGroup
          group={item.group}
          date={selectedDate}
          {isEditMode}
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
          Weiteres Widget oder neuen Bereich zum Dashboard hinzufügen
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
  date={selectedDate}
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
