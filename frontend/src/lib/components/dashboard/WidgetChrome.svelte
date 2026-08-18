<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';
  interface Props {
    title: string;
    unit?: string;
    color?: string;
    editMode?: boolean;
    onEdit?: () => void;
    onDelete?: () => void;
    children?: Snippet;
    class?: string;
  }

  let {
    title,
    unit,
    color = 'var(--color-primary-500)',
    editMode = false,
    onEdit,
    onDelete,
    children,
    class: extraClass = ''
  }: Props = $props();
</script>

<div class="border-surface-200 rounded-lg border bg-white shadow-sm {extraClass}">
  <div class="h-1 rounded-t-lg" style="background-color: {color}"></div>

  <div class="flex items-center justify-between px-4 pt-3 pb-2">
    <div class="flex items-center gap-2">
      {#if editMode}
        <Icon name="drag_indicator" size="sm" class="text-surface-400 cursor-grab" />
      {/if}
      <h3 class="text-surface-700 text-sm font-medium">{title}</h3>
      {#if unit}
        <span class="text-surface-400 text-xs">{unit}</span>
      {/if}
    </div>

    {#if editMode}
      <div class="flex items-center gap-1">
        {#if onEdit}
          <button
            class="duration-micro text-surface-400 hover:bg-surface-100 hover:text-surface-600 flex h-7 w-7 items-center justify-center rounded-md transition-colors"
            onclick={onEdit}
          >
            <Icon name="edit" size="sm" />
          </button>
        {/if}
        {#if onDelete}
          <button
            class="duration-micro text-surface-400 hover:bg-error-50 hover:text-error-500 flex h-7 w-7 items-center justify-center rounded-md transition-colors"
            onclick={onDelete}
          >
            <Icon name="delete" size="sm" />
          </button>
        {/if}
      </div>
    {/if}
  </div>

  <div class="px-4 pb-4">
    {@render children?.()}
  </div>
</div>
