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

  const categories = [
    'Alle',
    'Layout',
    'Kardiovaskulär',
    'Stoffwechsel',
    'Erholung',
    'Körper',
    'Aktivität',
    'Lifestyle'
  ];

  let filteredCatalog = $derived(
    WIDGET_CATALOG.filter((w) => {
      // In group mode, hide the group template
      if (targetGroup && w.isGroupTemplate) return false;
      const matchCat = selectedCategory === 'Alle' || w.category === selectedCategory;
      const matchSearch =
        !searchQuery ||
        w.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        w.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchSearch;
    })
  );

  function handleSelect(item: (typeof WIDGET_CATALOG)[0]) {
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

<Modal
  {open}
  title={targetGroup
    ? `Widget zu „${targetGroup.title}“ hinzufügen`
    : 'Salus Widget- und Layout-Galerie'}
  subtitle={targetGroup
    ? `Wähle ein Modul für den Abschnitt „${targetGroup.title}“`
    : 'Wähle ein loses Widget oder erstelle eine neue Gruppe für dein Dashboard'}
  icon="wb-sunny"
  size="xl"
  {onclose}
>
  <div class="space-y-5">
    <!-- Search Bar -->
    <div>
      <Input
        icon="search"
        placeholder="Nach Metrik, Layout oder Name suchen..."
        bind:value={searchQuery}
      />
    </div>

    <!-- Category Filter Pills with Smooth Gradient Edge Fades & Hidden Scrollbar -->
    <div class="relative w-full overflow-hidden">
      <!-- Scrollable Track with Mask Fade -->
      <div class="no-scrollbar scroll-mask-x flex gap-2 overflow-x-auto px-1 py-1 select-none">
        {#each categories as cat}
          {#if !(targetGroup && cat === 'Layout')}
            <button
              type="button"
              onclick={() => (selectedCategory = cat)}
              class="shrink-0 cursor-pointer rounded-xl px-3.5 py-1.5 text-xs font-bold whitespace-nowrap transition-all {selectedCategory ===
              cat
                ? 'bg-[var(--color-primary)] text-white shadow-xs'
                : 'border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
            >
              {cat === 'Layout' ? 'Layout und Gruppen' : cat}
            </button>
          {/if}
        {/each}
      </div>
    </div>

    <!-- Widget Grid Cards with Micro-Previews -->
    <div class="grid max-h-[52vh] grid-cols-1 gap-3.5 overflow-y-auto pr-1 md:grid-cols-2">
      {#each filteredCatalog as item}
        <div
          class="group flex flex-col justify-between space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-4 transition-all hover:border-[var(--color-primary)] hover:shadow-md {item.isGroupTemplate
            ? 'border-[var(--color-primary)]/40 bg-[var(--color-primary)]/5'
            : ''}"
        >
          <!-- Card Header -->
          <div>
            <div class="mb-1 flex items-center justify-between gap-2">
              <span
                class="text-xs font-extrabold text-[var(--text-main)] group-hover:text-[var(--color-primary)]"
              >
                {item.title}
              </span>
              <Badge
                variant={item.isGroupTemplate ? 'primary' : 'default'}
                class="text-[0.5625rem]"
              >
                {item.category}
              </Badge>
            </div>
            <p class="text-[0.6875rem] leading-tight text-[var(--text-muted)]">
              {item.description}
            </p>
          </div>

          <!-- LIVE VISUAL MICRO-PREVIEW -->
          <div
            class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5 text-xs"
          >
            <!-- LAYOUT TEMPLATE PREVIEW -->
            {#if item.isGroupTemplate}
              <div class="flex w-full items-center justify-between">
                <div>
                  <span class="block text-xs font-bold text-[var(--text-main)]"
                    >Neuer Abschnitt</span
                  >
                  <span class="text-[0.625rem] text-[var(--text-muted)]"
                    >1, 2 oder 3 Spalten Raster</span
                  >
                </div>
                <div class="flex gap-1">
                  <div
                    class="h-5 w-3.5 rounded-xs border border-[var(--color-primary)]/60 bg-[var(--color-primary)]/40"
                  ></div>
                  <div
                    class="h-5 w-3.5 rounded-xs border border-[var(--color-primary)]/60 bg-[var(--color-primary)]/40"
                  ></div>
                </div>
              </div>

              <!-- CARDIO: BLOOD PRESSURE -->
            {:else if item.type === 'blood_pressure_dial'}
              <div class="w-full space-y-1">
                <div class="flex items-center justify-between text-[0.6875rem]">
                  <span class="font-bold text-[var(--text-main)]">118 / 76 mmHg</span>
                  <span class="text-[0.625rem] font-bold text-emerald-500">Optimal (ESC 2024)</span>
                </div>
                <div class="flex h-1.5 overflow-hidden rounded-full bg-[var(--border-subtle)]">
                  <div class="h-full w-[50%] bg-emerald-500"></div>
                  <div class="h-full w-[20%] bg-teal-400"></div>
                  <div class="h-full w-[15%] bg-amber-400"></div>
                  <div class="h-full flex-1 bg-rose-500"></div>
                </div>
              </div>

              <!-- METABOLISM: CGM WAVE -->
            {:else if item.type === 'cgm_wave'}
              <div class="flex w-full items-center justify-between">
                <div>
                  <span class="text-sm font-bold text-[var(--text-main)]">84 mg/dL</span>
                  <span class="block text-[0.625rem] font-semibold text-emerald-500"
                    >&rarr; Stabil</span
                  >
                </div>
                <div class="h-6 w-20">
                  <svg viewBox="0 0 100 30" class="h-full w-full">
                    <path
                      d="M 0 20 Q 30 15 50 8 T 100 18"
                      fill="none"
                      stroke="#10b981"
                      stroke-width="2"
                    />
                  </svg>
                </div>
              </div>

              <!-- RECOVERY: BATTERY -->
            {:else if item.type === 'recovery_battery'}
              <div class="flex w-full items-center justify-between">
                <div class="flex items-center gap-2">
                  <div
                    class="flex h-6 w-6 items-center justify-center rounded-full border-2 border-emerald-500 text-[0.625rem] font-bold text-emerald-500"
                  >
                    88
                  </div>
                  <span class="text-xs font-bold text-[var(--text-main)]">Erholungs-Score</span>
                </div>
                <span class="text-[0.625rem] font-bold text-emerald-500">Strain 14–17</span>
              </div>

              <!-- CARDIO: RHR SPARKLINE -->
            {:else if item.type === 'rhr_sparkline'}
              <div class="flex w-full items-center justify-between">
                <div>
                  <span class="text-sm font-bold text-[var(--text-main)]">64 bpm</span>
                  <span class="block text-[0.625rem] font-semibold text-emerald-500"
                    >↘ -3 bpm Trend</span
                  >
                </div>
                <div class="h-5 w-16">
                  <svg viewBox="0 0 100 30" class="h-full w-full">
                    <path
                      d="M 0 25 L 30 20 L 70 12 L 100 12"
                      fill="none"
                      stroke="#059669"
                      stroke-width="2"
                    />
                  </svg>
                </div>
              </div>

              <!-- BODY: BIA SPECTRUM -->
            {:else if item.type === 'bia_spectrum'}
              <div class="w-full space-y-1">
                <div class="flex justify-between text-[0.6875rem]">
                  <span class="font-bold text-[var(--text-main)]">81.8 kg</span>
                  <span class="text-[0.625rem] font-bold text-cyan-500">KFA 13.8%</span>
                </div>
                <div class="flex h-1.5 overflow-hidden rounded-full bg-[var(--border-subtle)]">
                  <div class="h-full w-[86%] bg-[var(--color-primary)]"></div>
                  <div class="h-full w-[14%] bg-amber-400"></div>
                </div>
              </div>

              <!-- ACTIVITY: HISTOGRAM -->
            {:else if item.type === 'activity_histogram'}
              <div class="flex w-full items-center justify-between">
                <span class="text-xs font-bold text-[var(--text-main)]">10.420 Schritte</span>
                <div class="flex h-4 items-end gap-0.5">
                  <div class="h-2 w-1 bg-orange-400"></div>
                  <div class="h-4 w-1 bg-orange-500"></div>
                  <div class="h-2.5 w-1 bg-orange-400"></div>
                  <div class="h-3.5 w-1 bg-orange-500"></div>
                </div>
              </div>

              <!-- OTHER WIDGETS -->
            {:else}
              <div
                class="flex w-full items-center justify-between text-[0.6875rem] text-[var(--text-muted)]"
              >
                <span class="font-semibold text-[var(--text-main)]">{item.title}</span>
                <span class="text-[0.625rem] font-bold text-[var(--color-primary)]"
                  >Voll interaktiv</span
                >
              </div>
            {/if}
          </div>

          <!-- Card Action Footer -->
          <div
            class="flex items-center justify-between border-t border-[var(--border-subtle)]/60 pt-2"
          >
            <span class="text-[0.625rem] text-[var(--text-soft)]">
              {item.isGroupTemplate
                ? 'Layout-Vorlage'
                : `Layout: ${item.defaultSize === 'full' ? 'Ganze Spalte' : item.defaultSize === 'half' ? 'Halbe Spalte' : 'Kompakt'}`}
            </span>
            <button
              type="button"
              onclick={() => handleSelect(item)}
              class="cursor-pointer rounded-xl bg-[var(--color-primary)] px-3 py-1 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
            >
              {item.isGroupTemplate
                ? '+ Gruppe anlegen'
                : targetGroup
                  ? `+ Zu „${targetGroup.title}“`
                  : '+ Auf Dashboard'}
            </button>
          </div>
        </div>
      {/each}
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-3">
      <span class="text-xs text-[var(--text-muted)]">
        {filteredCatalog.length} Module verfügbar
      </span>
      <Btn variant="secondary" size="md" onclick={onclose}>Schließen</Btn>
    </div>
  </div>
</Modal>
