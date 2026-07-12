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

<div class="rounded-lg border border-surface-200 bg-white shadow-sm {extraClass}">
  <div class="h-1 rounded-t-lg" style="background-color: {color}"></div>

  <div class="flex items-center justify-between px-4 pt-3 pb-2">
    <div class="flex items-center gap-2">
      {#if editMode}
        <Icon name="drag_indicator" size="sm" class="cursor-grab text-surface-400" />
      {/if}
      <h3 class="text-sm font-medium text-surface-700">{title}</h3>
      {#if unit}
        <span class="text-xs text-surface-400">{unit}</span>
      {/if}
    </div>

    {#if editMode}
      <div class="flex items-center gap-1">
        {#if onEdit}
          <button
            class="flex h-7 w-7 items-center justify-center rounded-md text-surface-400 transition-colors duration-150 hover:bg-surface-100 hover:text-surface-600"
            onclick={onEdit}
          >
            <Icon name="edit" size="sm" />
          </button>
        {/if}
        {#if onDelete}
          <button
            class="flex h-7 w-7 items-center justify-center rounded-md text-surface-400 transition-colors duration-150 hover:bg-error-50 hover:text-error-500"
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
