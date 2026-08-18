<script lang="ts">
  import { WIDGET_CATALOG, type DashboardWidget, type DashboardWidgetGroup, type WidgetType } from '../../types/widget-groups';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

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

  const categories = ['Alle', 'Kardiovaskulär', 'Stoffwechsel', 'Erholung', 'Körper', 'Aktivität', 'Lifestyle'];

  let filteredCatalog = $derived(
    WIDGET_CATALOG.filter(w => {
      const matchCat = selectedCategory === 'Alle' || w.category === selectedCategory;
      const matchSearch = !searchQuery || w.title.toLowerCase().includes(searchQuery.toLowerCase()) || w.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchSearch;
    })
  );

  function handleSelectWidget(item: typeof WIDGET_CATALOG[0]) {
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

{#if open && targetGroup}
  <div class="fixed inset-0 bg-black/75 backdrop-blur-md z-60 flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl space-y-5 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center font-bold">
            <Icon name="sun" size={22} />
          </div>
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Widget zu „{targetGroup.title}“ hinzufügen</h2>
            <p class="text-xs text-[var(--text-muted)]">Wähle ein Modul aus dem Salus-Katalog</p>
          </div>
        </div>
        <button
          type="button"
          onclick={onclose}
          class="text-[var(--text-muted)] hover:text-[var(--text-main)] text-xl cursor-pointer"
        >
          &times;
        </button>
      </div>

      <!-- Search & Category Filters -->
      <div class="space-y-3">
        <input
          type="text"
          placeholder="Widgets nach Name oder Metrik durchsuchen..."
          bind:value={searchQuery}
          class="w-full px-4 py-2.5 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
        />

        <div class="flex gap-1.5 overflow-x-auto pb-1">
          {#each categories as cat}
            <button
              type="button"
              onclick={() => selectedCategory = cat}
              class="px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap cursor-pointer transition-all {selectedCategory === cat ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
            >
              {cat}
            </button>
          {/each}
        </div>
      </div>

      <!-- Widget Grid Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[50vh] overflow-y-auto pr-1">
        {#each filteredCatalog as item}
          <button
            type="button"
            onclick={() => handleSelectWidget(item)}
            class="p-4 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-left hover:border-[var(--color-primary)] hover:shadow-md transition-all cursor-pointer flex flex-col justify-between space-y-2 group"
          >
            <div>
              <div class="flex items-center justify-between gap-2 mb-1">
                <span class="font-extrabold text-xs text-[var(--text-main)] group-hover:text-[var(--color-primary)]">
                  {item.title}
                </span>
                <Badge variant="default" class="text-[0.5625rem]">
                  {item.category}
                </Badge>
              </div>
              <p class="text-[0.6875rem] text-[var(--text-muted)] leading-tight">
                {item.description}
              </p>
            </div>

            <div class="flex items-center justify-between text-[0.625rem] text-[var(--text-soft)] pt-2 border-t border-[var(--border-subtle)]/60">
              <span>Standard: {item.defaultSize === 'full' ? 'Ganze Breite' : item.defaultSize === 'half' ? 'Halbe Spalte' : '1/3 Spalte'}</span>
              <span class="font-bold text-[var(--color-primary)] group-hover:underline">+ Hinzufügen</span>
            </div>
          </button>
        {/each}
      </div>

      <!-- Footer -->
      <div class="flex justify-end pt-2 border-t border-[var(--border-subtle)]">
        <Btn variant="secondary" size="sm" onclick={onclose}>
          Schließen
        </Btn>
      </div>

    </div>
  </div>
{/if}
