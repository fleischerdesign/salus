<script lang="ts">
  import type { DashboardWidgetGroup } from '../../types/widget-groups';
  import WidgetRenderer from './WidgetRenderer.svelte';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { todayString } from '$lib/utils/datetime';

  let {
    group,
    date = todayString(),
    isEditMode = false,
    onopenfasting,
    oneditgroup,
    onaddwidget,
    onremovewidget,
    onmoveup,
    onmovedown,
    ondeletegroup
  } = $props<{
    group: DashboardWidgetGroup;
    date?: string;
    isEditMode?: boolean;
    waterAmount?: number;
    liveMetrics?: Map<string, number>;
    onopenfasting?: () => void;
    oneditgroup?: (group: DashboardWidgetGroup) => void;
    onaddwidget?: (group: DashboardWidgetGroup) => void;
    onremovewidget?: (groupId: string, widgetId: string) => void;
    onmoveup?: () => void;
    onmovedown?: () => void;
    ondeletegroup?: () => void;
  }>();

  let isCollapsed = $state(false);

  // Column Grid CSS Class
  let gridColsClass = $derived(
    group.columns === 1
      ? 'grid-cols-1'
      : group.columns === 2
        ? 'grid-cols-1 md:grid-cols-2'
        : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
  );
</script>

<section
  class="mb-6 space-y-4 rounded-3xl border border-border-subtle bg-surface-0/40 p-4 shadow-xs transition-all sm:p-5 {isEditMode
    ? 'border-primary/40 ring-2 ring-primary/20'
    : ''}"
>
  <!-- Group Header with Controls -->
  <div
    class="flex flex-wrap items-center justify-between gap-2 border-b border-border-subtle/60 pb-3"
  >
    <div class="flex items-center gap-3">
      <button
        type="button"
        onclick={() => (isCollapsed = !isCollapsed)}
        class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-xl border border-border-subtle bg-surface-50 text-text-muted transition-transform hover:text-text-main {isCollapsed
          ? '-rotate-90'
          : ''}"
        title={isCollapsed ? 'Gruppe aufklappen' : 'Gruppe einklappen'}
      >
        <Icon name="expand-more" size={16} />
      </button>

      <div>
        <div class="flex items-center gap-2">
          <h2 class="text-sm font-extrabold tracking-tight text-text-main sm:text-base">
            {group.title}
          </h2>
          <Badge variant="default" class="text-[0.625rem] font-bold">
            {group.widgets.length}
            {group.widgets.length === 1 ? 'Widget' : 'Widgets'}
          </Badge>
        </div>
        {#if group.subtitle}
          <p class="mt-0.5 text-xs text-text-muted">{group.subtitle}</p>
        {/if}
      </div>
    </div>

    <!-- Header Action Buttons (ONLY VISIBLE IN EDIT MODE) -->
    {#if isEditMode}
      <div class="flex animate-[fadeIn_0.2s_ease-out] items-center gap-1.5">
        <!-- Add Widget to this group -->
        <button
          type="button"
          onclick={() => onaddwidget?.(group)}
          class="flex cursor-pointer items-center gap-1 rounded-xl bg-primary px-2.5 py-1 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
        >
          <span>+ Widget</span>
        </button>

        <!-- Move Up / Down -->
        <button
          type="button"
          onclick={onmoveup}
          class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-xl border border-border-subtle bg-surface-50 text-xs font-bold text-text-muted hover:text-text-main"
          title="Gruppe nach oben verschieben"
        >
          &uarr;
        </button>
        <button
          type="button"
          onclick={onmovedown}
          class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-xl border border-border-subtle bg-surface-50 text-xs font-bold text-text-muted hover:text-text-main"
          title="Gruppe nach unten verschieben"
        >
          &darr;
        </button>

        <!-- Edit Group Settings -->
        <button
          type="button"
          onclick={() => oneditgroup?.(group)}
          class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-xl border border-border-subtle bg-surface-50 text-xs font-bold text-text-muted hover:text-text-main"
          title="Gruppeneinstellungen bearbeiten"
        >
          <Icon name="settings" size={14} />
        </button>

        <!-- Delete Group -->
        <button
          type="button"
          onclick={ondeletegroup}
          class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-xl border border-rose-500/20 bg-rose-500/10 text-xs font-bold text-rose-500 transition-all hover:bg-rose-500 hover:text-white"
          title="Gruppe löschen"
        >
          &times;
        </button>
      </div>
    {/if}
  </div>

  <!-- Group Body: Dynamic Grid of Widgets -->
  {#if !isCollapsed}
    <div class="grid {gridColsClass} animate-[fadeIn_0.15s_ease-out] gap-4">
      <!-- 1. Existing Widgets -->
      {#each group.widgets as w, wIdx (w.id)}
        <div
          class="relative transition-transform {w.size === 'full'
            ? 'col-span-full'
            : ''} {isEditMode ? (wIdx % 2 === 0 ? 'ios-wiggle-even' : 'ios-wiggle-odd') : ''}"
        >
          <!-- iOS Delete Badge (only in edit mode) -->
          {#if isEditMode}
            <button
              type="button"
              onclick={() => onremovewidget?.(group.id, w.id)}
              class="absolute -top-2 -right-2 z-30 flex h-6 w-6 animate-[scaleIn_0.15s_ease-out] cursor-pointer items-center justify-center rounded-full border-2 border-canvas bg-rose-500 text-sm font-extrabold text-white shadow-lg transition-transform hover:scale-110 active:scale-95"
              title="Widget entfernen"
              aria-label="Widget entfernen"
            >
              &times;
            </button>
          {/if}

          <WidgetRenderer widget={w} {date} {onopenfasting} />
        </div>
      {/each}

      <!-- 2. PLACEHOLDER "+" ADD WIDGET CARD (In Edit Mode OR when Group is empty) -->
      {#if isEditMode || group.widgets.length === 0}
        <button
          type="button"
          onclick={() => onaddwidget?.(group)}
          class="group flex min-h-[140px] cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed border-border-subtle bg-surface-0/20 p-6 text-center text-text-muted shadow-xs transition-all hover:border-primary hover:bg-primary/5 hover:text-primary"
        >
          <div
            class="mb-2 flex h-10 w-10 items-center justify-center rounded-2xl border border-border-subtle bg-surface-50 text-xl font-bold shadow-xs transition-all group-hover:bg-primary group-hover:text-white"
          >
            +
          </div>
          <span class="block text-xs font-bold text-text-main group-hover:text-primary">
            Widget hinzufügen
          </span>
          <span class="mt-0.5 text-[0.6875rem] text-text-muted">
            Katalog für „{group.title}“ öffnen
          </span>
        </button>
      {/if}
    </div>
  {/if}
</section>
