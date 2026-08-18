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
    loading?: boolean;
    skeleton?: Snippet;
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
    loading = false,
    skeleton,
    children,
    class: extraClass = ''
  }: Props = $props();

  let dragVisible = $derived(editMode && dragHandle);
  let editActionsVisible = $derived(editMode);
</script>

<div
  class="chrome-card duration-micro border-surface-200 bg-surface-0 overflow-hidden rounded-lg border transition-all {editMode
    ? 'bg-surface-50 cursor-grab active:cursor-grabbing'
    : 'hover:border-surface-300 hover:shadow-md'} {extraClass}"
  class:widget-chrome-handle={editMode && dragHandle}
>
  <div class="border-surface-100 flex items-center gap-1 border-b px-3 py-2">
    <!-- Drag handle -->
    {#if dragHandle}
      <span
        class="duration-micro flex items-center overflow-hidden transition-all ease-out {dragVisible
          ? 'max-w-[24px] opacity-100'
          : 'max-w-0 opacity-0'}"
      >
        <Icon name="drag-indicator" size="sm" class="text-surface-400" />
      </span>
    {/if}

    <!-- Metric icon -->
    {#if icon}
      <Icon
        name={icon}
        size="sm"
        class="text-surface-400"
        style={iconColor ? `color: ${iconColor}` : undefined}
      />
    {/if}

    <!-- Title -->
    <span class="text-surface-500 flex-1 text-xs font-medium tracking-wide uppercase">{title}</span>
    {#if unit}
      <span class="text-surface-400 text-xs">{unit}</span>
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
        class="edit-chrome-actions duration-micro flex items-center gap-0.5 overflow-hidden transition-all ease-out {editActionsVisible
          ? 'max-w-[120px] opacity-100'
          : 'max-w-0 opacity-0'}"
      >
        {@render editActions()}
      </div>
    {/if}
  </div>

  <!-- Body -->
  <div class="min-h-[80px] {dense ? 'px-4 pt-2 pb-4' : 'p-6'}">
    {#if loading}
      {#if skeleton}
        {@render skeleton()}
      {:else}
        <div class="space-y-2.5">
          <div class="bg-surface-100 h-7 w-20 animate-pulse rounded"></div>
          <div class="bg-surface-100 h-16 w-full animate-pulse rounded"></div>
        </div>
      {/if}
    {:else}
      {@render children?.()}
    {/if}
  </div>
</div>

<style>
  :global(.widget-grid__ghost) {
    opacity: 0.4;
    border: 2px dashed var(--color-primary-500);
    border-radius: var(--radius-lg);
  }
</style>
