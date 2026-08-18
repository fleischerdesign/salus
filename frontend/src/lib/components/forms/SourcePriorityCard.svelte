<script lang="ts">
  import type { MetricDefinition, UserSourcePreference } from '$lib/db/types';
  import Card from '$components/ui/Card.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Toggle from '$components/ui/Toggle.svelte';
  import Spinner from '$components/ui/Spinner.svelte';

  interface Props {
    metric: MetricDefinition;
    items: UserSourcePreference[];
    saving?: boolean;
    onUpdate: (items: UserSourcePreference[]) => void;
    onApplyToCategory?: () => void;
  }

  let { metric, items = [], saving = false, onUpdate, onApplyToCategory }: Props = $props();

  const KNOWN_LABELS: Record<string, string> = {
    oura: 'Oura Ring',
    apple_health: 'Apple Health',
    health_connect: 'Android Health Connect',
    samsung_health: 'Samsung Health',
    garmin: 'Garmin Connect',
    fitbit: 'Fitbit',
    google_fit: 'Google Fit',
    seed: 'Dev Seed Data',
    manual: 'Manual Input'
  };

  function formatSourceLabel(src: string) {
    return KNOWN_LABELS[src] ?? src.replace(/_/g, ' ').toUpperCase();
  }

  function moveUp(index: number) {
    if (index <= 0) return;
    const newItems = [...items];
    const temp = newItems[index];
    newItems[index] = newItems[index - 1];
    newItems[index - 1] = temp;
    newItems.forEach((item, idx) => {
      item.priority_rank = idx + 1;
    });
    onUpdate(newItems);
  }

  function moveDown(index: number) {
    if (index >= items.length - 1) return;
    const newItems = [...items];
    const temp = newItems[index];
    newItems[index] = newItems[index + 1];
    newItems[index + 1] = temp;
    newItems.forEach((item, idx) => {
      item.priority_rank = idx + 1;
    });
    onUpdate(newItems);
  }

  function toggleEnabled(index: number) {
    const newItems = [...items];
    newItems[index].is_enabled = !newItems[index].is_enabled;
    onUpdate(newItems);
  }

  let primarySource = $derived(items.find((i) => i.is_enabled)?.source ?? items[0]?.source ?? null);
  let allDisabled = $derived(items.length > 0 && items.every((i) => !i.is_enabled));
</script>

<div class="group relative">
  <Card padding={false} class="duration-micro border-surface-200 bg-surface-0 p-4 transition-all">
    <!-- Header -->
    <div class="mb-3 flex items-start justify-between">
      <div class="flex min-w-0 items-center gap-2.5">
        <div
          class="bg-primary-50 text-primary-600 flex h-8 w-8 shrink-0 items-center justify-center rounded-md shadow-2xs"
        >
          <Icon name="monitoring" size="sm" />
        </div>
        <div class="min-w-0">
          <h3 class="text-surface-900 truncate text-xs font-bold">{metric.name}</h3>
          <span class="text-surface-400 font-mono text-[10px]">{metric.code}</span>
        </div>
      </div>

      <div class="flex shrink-0 items-center gap-2">
        {#if primarySource && !allDisabled}
          <span
            class="bg-surface-100 text-surface-700 inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-[10px] font-semibold"
          >
            <Icon name="star" size="sm" class="text-warning-500" />
            {formatSourceLabel(primarySource)}
          </span>
        {:else if allDisabled}
          <span
            class="border-warning-200 bg-warning-50 text-warning-700 inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[10px] font-semibold"
          >
            <Icon name="warning" size="sm" class="text-warning-600" /> Muted
          </span>
        {/if}
      </div>
    </div>

    <!-- Interactive Pill List -->
    {#if items.length <= 1}
      <div
        class="border-surface-200/60 bg-surface-50/50 flex items-center justify-between rounded-md border px-3 py-2 text-xs"
      >
        <div class="flex items-center gap-2">
          <span class="text-surface-500 font-bold">1.</span>
          <span class="text-surface-900 font-medium"
            >{formatSourceLabel(items[0]?.source ?? 'manual')}</span
          >
        </div>
        <span class="text-surface-400 text-[10px]">Single Source</span>
      </div>
    {:else}
      <div class="space-y-1.5">
        {#each items as item, idx (item.source)}
          <div
            class="duration-micro flex items-center justify-between rounded-lg border px-3 py-2 text-xs transition-colors {item.is_enabled
              ? 'border-surface-200 bg-surface-50/50 text-surface-900'
              : 'border-surface-200/50 bg-surface-50/20 text-surface-400 opacity-60'}"
          >
            <div class="flex min-w-0 items-center gap-2">
              <Icon name="drag_indicator" size="sm" class="text-surface-400 shrink-0 cursor-grab" />
              <span class="text-surface-500 w-4 shrink-0 font-bold">{idx + 1}.</span>
              <span
                class="truncate font-medium {item.is_enabled
                  ? 'text-surface-900'
                  : 'text-surface-400 line-through'}"
              >
                {formatSourceLabel(item.source)}
              </span>
            </div>

            <div class="ml-2 flex shrink-0 items-center gap-1">
              <button
                type="button"
                class="text-surface-400 hover:bg-surface-200 hover:text-surface-700 flex h-7 w-7 items-center justify-center rounded transition-colors disabled:opacity-20"
                disabled={idx === 0}
                onclick={() => moveUp(idx)}
                title="Move Up"
              >
                <Icon name="arrow-upward" size="sm" />
              </button>
              <button
                type="button"
                class="text-surface-400 hover:bg-surface-200 hover:text-surface-700 flex h-7 w-7 items-center justify-center rounded transition-colors disabled:opacity-20"
                disabled={idx === items.length - 1}
                onclick={() => moveDown(idx)}
                title="Move Down"
              >
                <Icon name="arrow-downward" size="sm" />
              </button>
              <div class="border-surface-200/60 ml-1 border-l pl-1.5">
                <Toggle checked={item.is_enabled} onchange={() => toggleEnabled(idx)} />
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}

    <!-- Progressive Disclosure Action Footer -->
    {#if items.length > 1 && onApplyToCategory}
      <div
        class="border-surface-100 mt-3 flex items-center justify-between border-t pt-2 text-[10px]"
      >
        <span class="text-surface-400">{items.length} Configured Sources</span>
        <button
          type="button"
          class="duration-micro text-primary-600 hover:text-primary-700 font-semibold opacity-80 transition-colors group-hover:opacity-100"
          onclick={onApplyToCategory}
          disabled={saving}
        >
          {#if saving}<Spinner size="sm" />{/if} Apply to Category
        </button>
      </div>
    {/if}
  </Card>
</div>
