<script lang="ts">
  import { WIDGET_CATALOG, type DashboardWidget, type DashboardWidgetGroup, type WidgetType } from '../../types/widget-groups';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  let {
    open = false,
    targetGroup = null,
    onaddwidget,
    oncreategroup,
    onclose
  } = $props<{
    open: boolean;
    targetGroup: DashboardWidgetGroup | null;
    onaddwidget: (widget: DashboardWidget, targetGroupId: string | null) => void;
    oncreategroup: () => void;
    onclose: () => void;
  }>();

  let selectedCategory = $state<string>('Alle');
  let searchQuery = $state<string>('');

  const categories = ['Alle', 'Layout', 'Kardiovaskulär', 'Stoffwechsel', 'Erholung', 'Körper', 'Aktivität', 'Lifestyle'];

  let filteredCatalog = $derived(
    WIDGET_CATALOG.filter(w => {
      // In group mode, hide the group template
      if (targetGroup && w.isGroupTemplate) return false;
      const matchCat = selectedCategory === 'Alle' || w.category === selectedCategory;
      const matchSearch = !searchQuery || w.title.toLowerCase().includes(searchQuery.toLowerCase()) || w.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchSearch;
    })
  );

  function handleSelect(item: typeof WIDGET_CATALOG[0]) {
    if (item.isGroupTemplate) {
      onclose();
      oncreategroup();
      return;
    }

    const newWidget: DashboardWidget = {
      id: `w_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      type: item.type,
      title: item.title,
      size: item.defaultSize
    };
    onaddwidget(newWidget, targetGroup ? targetGroup.id : null);
    onclose();
  }
</script>

{#if open}
  <div class="fixed inset-0 bg-black/75 backdrop-blur-md z-60 flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-3xl w-full shadow-2xl space-y-5 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Clean Modal Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center font-bold shrink-0">
            <Icon name="sun" size={22} />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base font-extrabold text-[var(--text-main)]">
                {targetGroup ? `Widget zu „${targetGroup.title}“ hinzufügen` : 'Salus Widget- und Layout-Galerie'}
              </h2>
              {#if targetGroup}
                <Badge variant="primary" class="font-bold">Gruppe: {targetGroup.title}</Badge>
              {:else}
                <Badge variant="success" class="font-bold">Dashboard-Root</Badge>
              {/if}
            </div>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">
              {targetGroup ? `Wähle ein Modul für den Abschnitt „${targetGroup.title}“` : 'Wähle ein loses Widget oder erstelle eine neue Gruppe für dein Dashboard'}
            </p>
          </div>
        </div>

        <button
          type="button"
          onclick={onclose}
          class="w-8 h-8 rounded-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center text-lg cursor-pointer transition-colors"
          title="Schließen"
          aria-label="Schließen"
        >
          &times;
        </button>
      </div>

      <!-- Search Bar -->
      <div>
        <input
          type="text"
          placeholder="Nach Metrik, Layout oder Name suchen..."
          bind:value={searchQuery}
          class="w-full px-4 py-2.5 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
        />
      </div>

      <!-- Category Filter Pills with Smooth Gradient Edge Fades & Hidden Scrollbar -->
      <div class="relative w-full overflow-hidden">
        <!-- Scrollable Track with Mask Fade -->
        <div class="flex gap-2 overflow-x-auto py-1 px-1 no-scrollbar scroll-mask-x select-none">
          {#each categories as cat}
            {#if !(targetGroup && cat === 'Layout')}
              <button
                type="button"
                onclick={() => selectedCategory = cat}
                class="px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap cursor-pointer transition-all shrink-0 {selectedCategory === cat ? 'bg-[var(--color-primary)] text-white shadow-xs' : 'bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
              >
                {cat === 'Layout' ? 'Layout und Gruppen' : cat}
              </button>
            {/if}
          {/each}
        </div>
      </div>

      <!-- Widget Grid Cards with Micro-Previews -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5 max-h-[52vh] overflow-y-auto pr-1">
        {#each filteredCatalog as item}
          <div
            class="p-4 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] hover:border-[var(--color-primary)] hover:shadow-md transition-all flex flex-col justify-between space-y-3 group {item.isGroupTemplate ? 'border-[var(--color-primary)]/40 bg-[var(--color-primary)]/5' : ''}"
          >
            <!-- Card Header -->
            <div>
              <div class="flex items-center justify-between gap-2 mb-1">
                <span class="font-extrabold text-xs text-[var(--text-main)] group-hover:text-[var(--color-primary)]">
                  {item.title}
                </span>
                <Badge variant={item.isGroupTemplate ? 'primary' : 'default'} class="text-[0.5625rem]">
                  {item.category}
                </Badge>
              </div>
              <p class="text-[0.6875rem] text-[var(--text-muted)] leading-tight">
                {item.description}
              </p>
            </div>

            <!-- LIVE VISUAL MICRO-PREVIEW -->
            <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 flex items-center justify-between text-xs">
              <!-- LAYOUT TEMPLATE PREVIEW -->
              {#if item.isGroupTemplate}
                <div class="w-full flex items-center justify-between">
                  <div>
                    <span class="font-bold text-[var(--text-main)] text-xs block">Neuer Abschnitt</span>
                    <span class="text-[0.625rem] text-[var(--text-muted)]">1, 2 oder 3 Spalten Raster</span>
                  </div>
                  <div class="flex gap-1">
                    <div class="w-3.5 h-5 rounded-xs bg-[var(--color-primary)]/40 border border-[var(--color-primary)]/60"></div>
                    <div class="w-3.5 h-5 rounded-xs bg-[var(--color-primary)]/40 border border-[var(--color-primary)]/60"></div>
                  </div>
                </div>

              <!-- CARDIO: BLOOD PRESSURE -->
              {:else if item.type === 'blood_pressure_dial'}
                <div class="w-full space-y-1">
                  <div class="flex justify-between items-center text-[0.6875rem]">
                    <span class="font-bold text-[var(--text-main)]">118 / 76 mmHg</span>
                    <span class="text-emerald-500 font-bold text-[0.625rem]">Optimal (ESC 2024)</span>
                  </div>
                  <div class="h-1.5 rounded-full overflow-hidden flex bg-[var(--border-subtle)]">
                    <div class="bg-emerald-500 w-[50%] h-full"></div>
                    <div class="bg-teal-400 w-[20%] h-full"></div>
                    <div class="bg-amber-400 w-[15%] h-full"></div>
                    <div class="bg-rose-500 flex-1 h-full"></div>
                  </div>
                </div>

              <!-- METABOLISM: CGM WAVE -->
              {:else if item.type === 'cgm_wave'}
                <div class="w-full flex items-center justify-between">
                  <div>
                    <span class="font-bold text-[var(--text-main)] text-sm">84 mg/dL</span>
                    <span class="text-emerald-500 text-[0.625rem] block font-semibold">&rarr; Stabil</span>
                  </div>
                  <div class="w-20 h-6">
                    <svg viewBox="0 0 100 30" class="w-full h-full">
                      <path d="M 0 20 Q 30 15 50 8 T 100 18" fill="none" stroke="#10b981" stroke-width="2" />
                    </svg>
                  </div>
                </div>

              <!-- RECOVERY: BATTERY -->
              {:else if item.type === 'recovery_battery'}
                <div class="w-full flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <div class="w-6 h-6 rounded-full border-2 border-emerald-500 text-emerald-500 font-bold text-[0.625rem] flex items-center justify-center">
                      88
                    </div>
                    <span class="font-bold text-[var(--text-main)] text-xs">Erholungs-Score</span>
                  </div>
                  <span class="text-emerald-500 text-[0.625rem] font-bold">Strain 14–17</span>
                </div>

              <!-- CARDIO: RHR SPARKLINE -->
              {:else if item.type === 'rhr_sparkline'}
                <div class="w-full flex items-center justify-between">
                  <div>
                    <span class="font-bold text-[var(--text-main)] text-sm">64 bpm</span>
                    <span class="text-emerald-500 text-[0.625rem] block font-semibold">↘ -3 bpm Trend</span>
                  </div>
                  <div class="w-16 h-5">
                    <svg viewBox="0 0 100 30" class="w-full h-full">
                      <path d="M 0 25 L 30 20 L 70 12 L 100 12" fill="none" stroke="#059669" stroke-width="2" />
                    </svg>
                  </div>
                </div>

              <!-- BODY: BIA SPECTRUM -->
              {:else if item.type === 'bia_spectrum'}
                <div class="w-full space-y-1">
                  <div class="flex justify-between text-[0.6875rem]">
                    <span class="font-bold text-[var(--text-main)]">81.8 kg</span>
                    <span class="text-cyan-500 font-bold text-[0.625rem]">KFA 13.8%</span>
                  </div>
                  <div class="h-1.5 rounded-full overflow-hidden flex bg-[var(--border-subtle)]">
                    <div class="bg-[var(--color-primary)] w-[86%] h-full"></div>
                    <div class="bg-amber-400 w-[14%] h-full"></div>
                  </div>
                </div>

              <!-- ACTIVITY: HISTOGRAM -->
              {:else if item.type === 'activity_histogram'}
                <div class="w-full flex items-center justify-between">
                  <span class="font-bold text-[var(--text-main)] text-xs">10.420 Schritte</span>
                  <div class="flex items-end gap-0.5 h-4">
                    <div class="w-1 h-2 bg-orange-400"></div>
                    <div class="w-1 h-4 bg-orange-500"></div>
                    <div class="w-1 h-2.5 bg-orange-400"></div>
                    <div class="w-1 h-3.5 bg-orange-500"></div>
                  </div>
                </div>

              <!-- OTHER WIDGETS -->
              {:else}
                <div class="w-full flex items-center justify-between text-[0.6875rem] text-[var(--text-muted)]">
                  <span class="font-semibold text-[var(--text-main)]">{item.title}</span>
                  <span class="text-[0.625rem] text-[var(--color-primary)] font-bold">Voll interaktiv</span>
                </div>
              {/if}
            </div>

            <!-- Card Action Footer -->
            <div class="flex items-center justify-between pt-2 border-t border-[var(--border-subtle)]/60">
              <span class="text-[0.625rem] text-[var(--text-soft)]">
                {item.isGroupTemplate ? 'Layout-Vorlage' : `Layout: ${item.defaultSize === 'full' ? 'Ganze Spalte' : item.defaultSize === 'half' ? 'Halbe Spalte' : 'Kompakt'}`}
              </span>
              <button
                type="button"
                onclick={() => handleSelect(item)}
                class="px-3 py-1 rounded-xl bg-[var(--color-primary)] text-white hover:opacity-90 text-xs font-bold transition-all cursor-pointer shadow-xs"
              >
                {item.isGroupTemplate ? '+ Gruppe anlegen' : targetGroup ? `+ Zu „${targetGroup.title}“` : '+ Auf Dashboard'}
              </button>
            </div>
          </div>
        {/each}
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between pt-3 border-t border-[var(--border-subtle)]">
        <span class="text-xs text-[var(--text-muted)]">
          {filteredCatalog.length} Module verfügbar
        </span>
        <Btn variant="secondary" size="sm" onclick={onclose}>
          Schließen
        </Btn>
      </div>

    </div>
  </div>
{/if}
