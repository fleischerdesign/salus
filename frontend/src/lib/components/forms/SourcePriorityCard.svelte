<script lang="ts">
  import type { MetricDefinition, UserSourcePreference } from '$lib/db/types';
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';
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
    manual: 'Manuelle Eingabe',
    webhook: 'Webhook / API'
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

<div
  class="group relative space-y-3 rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs transition-all hover:border-border-strong"
>
  <!-- Header -->
  <div class="flex items-start justify-between gap-2">
    <div class="flex min-w-0 items-center gap-2.5">
      <div
        class="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary-soft/20 text-primary"
      >
        <Icon name="monitoring" size="sm" />
      </div>
      <div class="min-w-0">
        <h3 class="truncate text-xs font-extrabold text-text-main">{metric.name}</h3>
        <span class="font-mono text-[0.625rem] text-text-muted">{metric.code}</span>
      </div>
    </div>

    <div class="flex shrink-0 items-center gap-2">
      {#if primarySource && !allDisabled}
        <Badge variant="primary" class="text-[0.625rem]">
          <Icon name="star" size="sm" class="mr-1 text-amber-500" />
          {formatSourceLabel(primarySource)}
        </Badge>
      {:else if allDisabled}
        <Badge variant="default" class="text-[0.625rem] text-amber-600 dark:text-amber-400">
          <Icon name="warning" size="sm" class="mr-1" />
          Stummgeschaltet
        </Badge>
      {/if}
    </div>
  </div>

  <!-- Interactive Pill List -->
  {#if items.length <= 1}
    <div
      class="flex items-center justify-between rounded-xl border border-border-subtle bg-surface-50 px-3 py-2 text-xs"
    >
      <div class="flex items-center gap-2">
        <span class="font-bold text-text-muted">1.</span>
        <span class="font-bold text-text-main"
          >{formatSourceLabel(items[0]?.source ?? 'manual')}</span
        >
      </div>
      <span class="text-[0.625rem] text-text-muted">Einzige Quelle</span>
    </div>
  {:else}
    <div class="space-y-1.5">
      {#each items as item, idx (item.source)}
        <div
          class="flex items-center justify-between rounded-xl border px-3 py-2 text-xs transition-colors {item.is_enabled
            ? 'border-border-subtle bg-surface-50 text-text-main'
            : 'border-border-subtle/60 bg-surface-50/40 text-text-muted opacity-60'}"
        >
          <div class="flex min-w-0 items-center gap-2">
            <Icon name="drag-indicator" size="sm" class="shrink-0 cursor-grab text-text-muted" />
            <span class="w-4 shrink-0 font-bold text-text-muted">{idx + 1}.</span>
            <span
              class="truncate font-semibold {item.is_enabled
                ? 'text-text-main'
                : 'text-text-muted line-through'}"
            >
              {formatSourceLabel(item.source)}
            </span>
          </div>

          <div class="ml-2 flex shrink-0 items-center gap-1">
            <button
              type="button"
              class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-lg text-text-muted transition-colors hover:bg-surface-100 hover:text-text-main disabled:opacity-20"
              disabled={idx === 0}
              onclick={() => moveUp(idx)}
              title="Nach oben verschieben"
            >
              <Icon name="arrow-upward" size="sm" />
            </button>
            <button
              type="button"
              class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-lg text-text-muted transition-colors hover:bg-surface-100 hover:text-text-main disabled:opacity-20"
              disabled={idx === items.length - 1}
              onclick={() => moveDown(idx)}
              title="Nach unten verschieben"
            >
              <Icon name="arrow-downward" size="sm" />
            </button>
            <div class="ml-1 border-l border-border-subtle pl-1.5">
              <Toggle checked={item.is_enabled} onchange={() => toggleEnabled(idx)} />
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Action Footer -->
  {#if items.length > 1 && onApplyToCategory}
    <div
      class="flex items-center justify-between border-t border-border-subtle/60 pt-2 text-[0.6875rem]"
    >
      <span class="text-text-muted">{items.length} Quellen konfiguriert</span>
      <button
        type="button"
        class="flex cursor-pointer items-center gap-1 font-bold text-primary hover:underline disabled:opacity-50"
        onclick={onApplyToCategory}
        disabled={saving}
      >
        {#if saving}<Spinner size="sm" />{/if}
        <span>Auf Kategorie anwenden</span>
      </button>
    </div>
  {/if}
</div>
