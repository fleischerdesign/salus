<script lang="ts">
  import type { DashboardWidgetGroup } from '../../types/widget-groups';
  import WidgetRenderer from './WidgetRenderer.svelte';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    group,
    isEditMode = false,
    waterAmount = 2250,
    onopenfasting,
    oneditgroup,
    onaddwidget,
    onremovewidget,
    onmoveup,
    onmovedown,
    ondeletegroup
  } = $props<{
    group: DashboardWidgetGroup;
    isEditMode?: boolean;
    waterAmount?: number;
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
    group.columns === 1 ? 'grid-cols-1' :
    group.columns === 2 ? 'grid-cols-1 md:grid-cols-2' :
    'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
  );
</script>

<section class="bg-[var(--bg-surface-0)]/40 border border-[var(--border-subtle)] rounded-3xl p-4 sm:p-5 shadow-xs transition-all space-y-4 mb-6 {isEditMode ? 'ring-2 ring-[var(--color-primary)]/20 border-[var(--color-primary)]/40' : ''}">
  
  <!-- Group Header with Controls -->
  <div class="flex items-center justify-between flex-wrap gap-2 border-b border-[var(--border-subtle)]/60 pb-3">
    <div class="flex items-center gap-3">
      <button
        type="button"
        onclick={() => isCollapsed = !isCollapsed}
        class="w-7 h-7 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center cursor-pointer transition-transform {isCollapsed ? '-rotate-90' : ''}"
        title={isCollapsed ? 'Gruppe aufklappen' : 'Gruppe einklappen'}
      >
        <Icon name="chevron-down" size={16} />
      </button>

      <div>
        <div class="flex items-center gap-2">
          <h2 class="text-sm sm:text-base font-extrabold text-[var(--text-main)] tracking-tight">
            {group.title}
          </h2>
          <Badge variant="default" class="text-[0.625rem] font-bold">
            {group.widgets.length} {group.widgets.length === 1 ? 'Widget' : 'Widgets'}
          </Badge>
        </div>
        {#if group.subtitle}
          <p class="text-xs text-[var(--text-muted)] mt-0.5">{group.subtitle}</p>
        {/if}
      </div>
    </div>

    <!-- Header Action Buttons (ONLY VISIBLE IN EDIT MODE) -->
    {#if isEditMode}
      <div class="flex items-center gap-1.5 animate-[fadeIn_0.2s_ease-out]">
        <!-- Add Widget to this group -->
        <button
          type="button"
          onclick={() => onaddwidget?.(group)}
          class="px-2.5 py-1 rounded-xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer flex items-center gap-1 shadow-xs"
        >
          <span>+ Widget</span>
        </button>

        <!-- Move Up / Down -->
        <button
          type="button"
          onclick={onmoveup}
          class="w-7 h-7 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center cursor-pointer text-xs font-bold"
          title="Gruppe nach oben verschieben"
        >
          ▲
        </button>
        <button
          type="button"
          onclick={onmovedown}
          class="w-7 h-7 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center cursor-pointer text-xs font-bold"
          title="Gruppe nach unten verschieben"
        >
          ▼
        </button>

        <!-- Edit Group Settings Modal Trigger -->
        <button
          type="button"
          onclick={() => oneditgroup?.(group)}
          class="w-7 h-7 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center cursor-pointer"
          title="Gruppe bearbeiten"
        >
          <Icon name="sun" size={14} />
        </button>

        <!-- Delete Group -->
        <button
          type="button"
          onclick={() => {
            if (confirm(`Gruppe „${group.title}“ wirklich löschen?`)) {
              ondeletegroup?.();
            }
          }}
          class="w-7 h-7 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-500 hover:bg-rose-500 hover:text-white transition-all flex items-center justify-center cursor-pointer text-xs font-bold"
          title="Gruppe löschen"
        >
          &times;
        </button>
      </div>
    {/if}
  </div>

  <!-- Group Body: Dynamic Grid of Widgets -->
  {#if !isCollapsed}
    <div class="grid {gridColsClass} gap-4 animate-[fadeIn_0.15s_ease-out]">
      <!-- 1. Existing Widgets -->
      {#each group.widgets as w, wIdx (w.id)}
        <div
          class="relative transition-transform {w.size === 'full' ? 'col-span-full' : ''} {isEditMode ? (wIdx % 2 === 0 ? 'ios-wiggle-even' : 'ios-wiggle-odd') : ''}"
        >
          <!-- iOS Delete Badge (only in edit mode) -->
          {#if isEditMode}
            <button
              type="button"
              onclick={() => onremovewidget?.(group.id, w.id)}
              class="absolute -top-2 -right-2 z-30 w-6 h-6 rounded-full bg-rose-500 text-white font-extrabold text-sm flex items-center justify-center shadow-lg hover:scale-110 active:scale-95 transition-transform cursor-pointer border-2 border-[var(--bg-canvas)] animate-[scaleIn_0.15s_ease-out]"
              title="Widget entfernen"
              aria-label="Widget entfernen"
            >
              &times;
            </button>
          {/if}

          <WidgetRenderer
            widget={w}
            {waterAmount}
            {onopenfasting}
          />
        </div>
      {/each}

      <!-- 2. PLACEHOLDER "+" ADD WIDGET CARD (In Edit Mode OR when Group is empty) -->
      {#if isEditMode || group.widgets.length === 0}
        <button
          type="button"
          onclick={() => onaddwidget?.(group)}
          class="min-h-[140px] rounded-3xl border-2 border-dashed border-[var(--border-subtle)] hover:border-[var(--color-primary)] bg-[var(--bg-surface-0)]/20 hover:bg-[var(--color-primary)]/5 text-[var(--text-muted)] hover:text-[var(--color-primary)] flex flex-col items-center justify-center p-6 text-center transition-all cursor-pointer group shadow-xs"
        >
          <div class="w-10 h-10 rounded-2xl bg-[var(--bg-surface-50)] group-hover:bg-[var(--color-primary)] group-hover:text-white border border-[var(--border-subtle)] flex items-center justify-center text-xl font-bold transition-all mb-2 shadow-xs">
            +
          </div>
          <span class="text-xs font-bold block text-[var(--text-main)] group-hover:text-[var(--color-primary)]">
            Widget hinzufügen
          </span>
          <span class="text-[0.6875rem] text-[var(--text-muted)] mt-0.5">
            Katalog für „{group.title}“ öffnen
          </span>
        </button>
      {/if}
    </div>
  {/if}

</section>

<style>
  @keyframes iosWiggleEven {
    0% { transform: rotate(-0.4deg) translate(-0.3px, 0); }
    50% { transform: rotate(0.45deg) translate(0.3px, -0.3px); }
    100% { transform: rotate(-0.4deg) translate(-0.3px, 0); }
  }

  @keyframes iosWiggleOdd {
    0% { transform: rotate(0.45deg) translate(0.3px, 0); }
    50% { transform: rotate(-0.4deg) translate(-0.3px, 0.3px); }
    100% { transform: rotate(0.45deg) translate(0.3px, 0); }
  }

  .ios-wiggle-even {
    animation: iosWiggleEven 0.88s infinite ease-in-out;
    transform-origin: 50% 50%;
  }

  .ios-wiggle-odd {
    animation: iosWiggleOdd 0.94s infinite ease-in-out;
    transform-origin: 50% 50%;
  }
</style>
