<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    title: string;
    icon?: string;
    iconColor?: string;
    unit?: string;
    actions?: Snippet;
    editActions?: Snippet;
    editMode?: boolean;
    dragHandle?: boolean;
    dense?: boolean;
    children?: Snippet;
    class?: string;
  }

  let {
    title,
    icon,
    iconColor,
    unit,
    actions,
    editActions,
    editMode = false,
    dragHandle = false,
    dense = false,
    children,
    class: extraClass = ''
  }: Props = $props();

  let dragVisible = $derived(editMode && dragHandle);
  let editActionsVisible = $derived(editMode);
</script>

<div
  class="chrome-card overflow-hidden rounded-lg border border-surface-200 bg-surface-0 transition-all duration-fast {editMode ? 'cursor-grab bg-surface-50 active:cursor-grabbing' : 'hover:border-surface-300 hover:shadow-md'} {extraClass}"
  class:widget-chrome-handle={editMode && dragHandle}
>
  <div class="flex items-center gap-1 border-b border-surface-100 px-3 py-2">
    <!-- Drag handle -->
    {#if dragHandle}
      <span
        class="flex items-center overflow-hidden transition-all duration-fast ease-out {dragVisible ? 'max-w-[24px] opacity-100' : 'max-w-0 opacity-0'}"
      >
        <Icon name="drag-indicator" size="sm" class="text-surface-400" />
      </span>
    {/if}

    <!-- Metric icon -->
    {#if icon}
      <Icon name={icon} size="sm" class="text-surface-400" style={iconColor ? `color: ${iconColor}` : undefined} />
    {/if}

    <!-- Title -->
    <span class="flex-1 text-xs font-medium uppercase tracking-wide text-surface-500">{title}</span>
    {#if unit}
      <span class="text-xs text-surface-400">{unit}</span>
    {/if}

    <!-- Always-visible actions (for non-edit cards: Connections, Goals, etc.) -->
    {#if actions}
      <div class="flex items-center gap-0.5">
        {@render actions()}
      </div>
    {/if}

    <!-- Edit-only actions (revealed via transition when editMode is active) -->
    {#if editActions}
      <div
        class="edit-chrome-actions flex items-center gap-0.5 overflow-hidden transition-all duration-fast ease-out {editActionsVisible ? 'max-w-[120px] opacity-100' : 'max-w-0 opacity-0'}"
      >
        {@render editActions()}
      </div>
    {/if}
  </div>

  <!-- Body -->
  <div class="min-h-[80px] {dense ? 'px-4 pb-4 pt-2' : 'p-6'}">
    {@render children?.()}
  </div>
</div>

<style>
  :global(.widget-grid__ghost) {
    opacity: 0.4;
    border: 2px dashed var(--color-primary-500);
    border-radius: var(--radius-lg);
    background: var(--color-primary-50);
  }
  :global(.widget-grid__ghost > *) {
    visibility: hidden;
  }
  :global(.sortable-fallback) {
    position: fixed !important;
    z-index: 10000;
    pointer-events: none;
    box-shadow: var(--shadow-lg);
    opacity: 0.9;
  }
</style>
