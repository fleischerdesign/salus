<script lang="ts">
  import {
    WIDGET_CATALOG,
    type DashboardWidget,
    type DashboardWidgetGroup
  } from '../../types/widget-groups';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Modal from '../ui/Modal.svelte';

  let {
    open = false,
    targetGroup,
    onadd,
    onclose
  } = $props<{
    open: boolean;
    targetGroup: DashboardWidgetGroup | null;
    onadd: (widget: DashboardWidget, groupId: string) => void;
    onclose: () => void;
  }>();

  let selectedCategory = $state<string>('Alle');
  let searchQuery = $state<string>('');

  const categories = [
    'Alle',
    'Kardiovaskulär',
    'Stoffwechsel',
    'Erholung',
    'Körper',
    'Aktivität',
    'Lifestyle'
  ];

  let filteredCatalog = $derived(
    WIDGET_CATALOG.filter((w) => {
      const matchCat = selectedCategory === 'Alle' || w.category === selectedCategory;
      const matchSearch =
        !searchQuery ||
        w.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        w.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchSearch;
    })
  );

  function handleSelectWidget(item: (typeof WIDGET_CATALOG)[0]) {
    if (!targetGroup) return;
    const newWidget: DashboardWidget = {
      id: `w_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      type: item.type,
      title: item.title,
      size: item.defaultSize
    };
    onadd(newWidget, targetGroup.id);
    onclose();
  }
</script>

<Modal
  open={open && Boolean(targetGroup)}
  title={`Widget zu „${targetGroup?.title || ''}“ hinzufügen`}
  subtitle="Wähle ein Modul aus dem Salus-Katalog"
  icon="wb-sunny"
  size="lg"
  {onclose}
>
  <div class="space-y-5">
    <!-- Search & Category Filters -->
    <div class="space-y-3">
      <Input
        icon="search"
        placeholder="Widgets nach Name oder Metrik durchsuchen..."
        bind:value={searchQuery}
      />

      <div class="flex gap-1.5 overflow-x-auto pb-1">
        {#each categories as cat}
          <button
            type="button"
            onclick={() => (selectedCategory = cat)}
            class="cursor-pointer rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition-all {selectedCategory ===
            cat
              ? 'bg-[var(--color-primary)] text-white'
              : 'bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
          >
            {cat}
          </button>
        {/each}
      </div>
    </div>

    <!-- Widget Grid Cards -->
    <div class="grid max-h-[50vh] grid-cols-1 gap-3 overflow-y-auto pr-1 sm:grid-cols-2">
      {#each filteredCatalog as item}
        <button
          type="button"
          onclick={() => handleSelectWidget(item)}
          class="group flex cursor-pointer flex-col justify-between space-y-2 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-4 text-left transition-all hover:border-[var(--color-primary)] hover:shadow-md"
        >
          <div>
            <div class="mb-1 flex items-center justify-between gap-2">
              <span
                class="text-xs font-extrabold text-[var(--text-main)] group-hover:text-[var(--color-primary)]"
              >
                {item.title}
              </span>
              <Badge variant="default" class="text-[0.5625rem]">
                {item.category}
              </Badge>
            </div>
            <p class="text-[0.6875rem] leading-tight text-[var(--text-muted)]">
              {item.description}
            </p>
          </div>

          <div
            class="flex items-center justify-between border-t border-[var(--border-subtle)]/60 pt-2 text-[0.625rem] text-[var(--text-soft)]"
          >
            <span
              >Standard: {item.defaultSize === 'full'
                ? 'Ganze Breite'
                : item.defaultSize === 'half'
                  ? 'Halbe Spalte'
                  : '1/3 Spalte'}</span
            >
            <span class="font-bold text-[var(--color-primary)] group-hover:underline"
              >+ Hinzufügen</span
            >
          </div>
        </button>
      {/each}
    </div>

    <!-- Footer -->
    <div class="flex justify-end border-t border-[var(--border-subtle)] pt-2">
      <Btn variant="secondary" size="md" onclick={onclose}>Schließen</Btn>
    </div>
  </div>
</Modal>
