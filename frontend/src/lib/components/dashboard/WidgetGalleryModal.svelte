<script lang="ts">
  import { getAllWidgetManifests, type WidgetManifest } from '$lib/dashboard/widget-registry';
  import type { DashboardWidget, DashboardWidgetGroup } from '$lib/types/widget-groups';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Modal from '../ui/Modal.svelte';
  import Icon from '../ui/Icon.svelte';
  import { todayString } from '$lib/utils/datetime';

  interface Props {
    open: boolean;
    date?: string;
    targetGroup: DashboardWidgetGroup | null;
    onaddwidget: (widget: DashboardWidget, targetGroupId: string | null) => void;
    oncreategroup: () => void;
    onclose: () => void;
  }

  let {
    open = false,
    date = todayString(),
    targetGroup = null,
    onaddwidget,
    oncreategroup,
    onclose
  }: Props = $props();

  let selectedCategory = $state<string>('Alle');
  let searchQuery = $state<string>('');

  const categories = [
    { id: 'Alle', label: 'Alle' },
    { id: 'vitals', label: 'Vitalwerte' },
    { id: 'activity', label: 'Aktivität' },
    { id: 'sleep', label: 'Schlaf' },
    { id: 'nutrition', label: 'Ernährung' },
    { id: 'wellness', label: 'Gewohnheiten' },
    { id: 'special', label: 'Biorhythmus' },
    { id: 'layout', label: 'Layout & Gruppen' }
  ];

  const manifests = $derived(getAllWidgetManifests());

  let filteredManifests = $derived(
    manifests.filter((m) => {
      const matchCat = selectedCategory === 'Alle' || selectedCategory === m.category;
      const matchSearch =
        !searchQuery ||
        m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (m.subtitle?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);
      return matchCat && matchSearch;
    })
  );

  let showGroupTemplate = $derived(
    !targetGroup &&
      (selectedCategory === 'Alle' || selectedCategory === 'layout') &&
      (!searchQuery || 'gruppe abschnitt layout'.includes(searchQuery.toLowerCase()))
  );

  function handleSelectWidget(m: WidgetManifest) {
    const newWidget: DashboardWidget = {
      id: `w_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      type: m.type,
      title: m.title,
      size: m.defaultSize === 'large' ? 'full' : m.defaultSize === 'small' ? 'compact' : 'half'
    };
    onaddwidget(newWidget, targetGroup ? targetGroup.id : null);
    onclose();
  }

  function handleSelectGroupTemplate() {
    onclose();
    oncreategroup();
  }
</script>

<Modal
  {open}
  title={targetGroup
    ? `Widget zu „${targetGroup.title}“ hinzufügen`
    : 'Salus Widget- und Layout-Galerie'}
  subtitle={targetGroup
    ? `Wähle ein Modul für den Abschnitt „${targetGroup.title}“`
    : 'Wähle ein Widget oder erstelle einen neuen Bereich für dein Dashboard'}
  icon="dashboard"
  size="xl"
  {onclose}
>
  <div class="space-y-5">
    <!-- Search Bar -->
    <div>
      <Input
        icon="search"
        placeholder="Nach Vitalwert, Schlaf, Fasten oder Name suchen..."
        bind:value={searchQuery}
      />
    </div>

    <!-- Category Filter Pills -->
    <div class="relative w-full overflow-hidden">
      <div class="no-scrollbar scroll-mask-x flex gap-2 overflow-x-auto px-1 py-1 select-none">
        {#each categories as cat}
          {#if !(targetGroup && cat.id === 'layout')}
            <button
              type="button"
              onclick={() => (selectedCategory = cat.id)}
              class="shrink-0 cursor-pointer rounded-xl px-3.5 py-1.5 text-xs font-bold whitespace-nowrap transition-all {selectedCategory ===
              cat.id
                ? 'bg-[var(--color-primary)] text-white shadow-xs'
                : 'border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
            >
              {cat.label}
            </button>
          {/if}
        {/each}
      </div>
    </div>

    <!-- Widget Grid Cards -->
    <div class="grid max-h-[58vh] grid-cols-1 gap-4 overflow-y-auto pr-1 md:grid-cols-2">
      <!-- 1. GROUP TEMPLATE CARD (if applicable) -->
      {#if showGroupTemplate}
        <div
          class="group flex flex-col justify-between space-y-3 rounded-3xl border-2 border-dashed border-[var(--color-primary)]/40 bg-[var(--color-primary)]/5 p-4.5 transition-all hover:border-[var(--color-primary)] hover:shadow-md"
        >
          <div>
            <div class="mb-1.5 flex items-center justify-between gap-2">
              <span class="text-xs font-extrabold text-[var(--color-primary)]">
                Neuer visueller Abschnitt (Gruppe)
              </span>
              <Badge variant="primary" class="text-[0.5625rem]">Layout</Badge>
            </div>
            <p class="text-[0.6875rem] leading-tight text-[var(--text-muted)]">
              Erstelle einen zusammenhängenden Bereich mit 1, 2 oder 3 Spalten zur thematischen
              Bündelung von Widgets.
            </p>
          </div>

          <!-- Mini Layout Visual Preview -->
          <div
            class="flex h-24 items-center justify-center rounded-2xl border border-[var(--color-primary)]/20 bg-[var(--bg-surface-0)]/80 p-3"
          >
            <div class="grid w-full grid-cols-3 gap-1.5">
              <div
                class="h-14 rounded-xl border border-dashed border-[var(--color-primary)]/40 bg-[var(--color-primary-soft)]/20"
              ></div>
              <div
                class="h-14 rounded-xl border border-dashed border-[var(--color-primary)]/40 bg-[var(--color-primary-soft)]/20"
              ></div>
              <div
                class="h-14 rounded-xl border border-dashed border-[var(--color-primary)]/40 bg-[var(--color-primary-soft)]/20"
              ></div>
            </div>
          </div>

          <div
            class="flex items-center justify-between border-t border-[var(--border-subtle)]/60 pt-2"
          >
            <span class="text-[0.625rem] text-[var(--text-muted)]">Raster-Container</span>
            <button
              type="button"
              onclick={handleSelectGroupTemplate}
              class="cursor-pointer rounded-xl bg-[var(--color-primary)] px-3 py-1.5 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90 active:scale-95"
            >
              + Gruppe erstellen
            </button>
          </div>
        </div>
      {/if}

      <!-- 2. DYNAMIC REGISTRY WIDGETS WITH LIVE PREVIEW -->
      {#each filteredManifests as m}
        <div
          class="group flex flex-col justify-between space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-4.5 transition-all hover:border-[var(--color-primary)] hover:shadow-md"
        >
          <div>
            <div class="mb-1 flex items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <div
                  class="flex h-7 w-7 items-center justify-center rounded-lg shadow-2xs"
                  style="background-color: color-mix(in srgb, {m.iconColor} 12%, transparent); color: {m.iconColor};"
                >
                  <Icon name={m.icon} size="sm" />
                </div>
                <span
                  class="text-xs font-extrabold text-[var(--text-main)] group-hover:text-[var(--color-primary)]"
                >
                  {m.title}
                </span>
              </div>
              <Badge variant="default" class="text-[0.5625rem] capitalize">
                {m.category}
              </Badge>
            </div>
            <p class="text-[0.6875rem] leading-tight text-[var(--text-muted)]">
              {m.description}
            </p>
          </div>

          <!-- LIVE EMBEDDED WIDGET PREVIEW (Interactive Safe) -->
          <div
            class="pointer-events-none overflow-hidden rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)]/40 p-1 shadow-2xs select-none"
          >
            <div class="w-full">
              <m.component {date} preview={true} />
            </div>
          </div>

          <!-- Card Action Footer -->
          <div
            class="flex items-center justify-between border-t border-[var(--border-subtle)]/60 pt-2"
          >
            <span class="text-[0.625rem] text-[var(--text-muted)]">
              {m.defaultSize === 'large'
                ? 'Volle Breite'
                : m.defaultSize === 'small'
                  ? 'Kompakt'
                  : 'Standard'}
            </span>
            <button
              type="button"
              onclick={() => handleSelectWidget(m)}
              class="cursor-pointer rounded-xl bg-[var(--color-primary)] px-3 py-1.5 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90 active:scale-95"
            >
              {targetGroup ? `+ Zu „${targetGroup.title}“` : '+ Auf Dashboard'}
            </button>
          </div>
        </div>
      {/each}
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-3">
      <span class="text-xs text-[var(--text-muted)]">
        {filteredManifests.length + (showGroupTemplate ? 1 : 0)} Module verfügbar
      </span>
      <Btn variant="secondary" size="md" onclick={onclose}>Schließen</Btn>
    </div>
  </div>
</Modal>
