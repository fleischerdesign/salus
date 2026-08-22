<script lang="ts">
  import { page } from '$app/state';
  import Icon from '../ui/Icon.svelte';
  import Btn from '../ui/Btn.svelte';
  import BiomarkerTable from '../labs/BiomarkerTable.svelte';
  import LabPanelCard from '../labs/LabPanelCard.svelte';
  import E2EEShareCard from '../labs/E2EEShareCard.svelte';
  import DoctorShareModal from '../labs/DoctorShareModal.svelte';

  export type LabsTab = 'matrix' | 'panels' | 'share';

  let { initialTab = 'matrix', onopenpdf } = $props<{
    initialTab?: LabsTab;
    onopenpdf?: () => void;
  }>();

  let activeTab = $derived<LabsTab>(
    page.url.pathname.includes('/labs/panels')
      ? 'panels'
      : page.url.pathname.includes('/labs/share')
        ? 'share'
        : page.url.pathname.includes('/labs/matrix')
          ? 'matrix'
          : initialTab
  );

  let isDoctorModalOpen = $state(false);
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Laborwerte</h1>
      <p class="mt-0.5 text-xs text-text-muted sm:text-sm">
        Laborwert-Verlauf, Organprofile und Befund-Freigabe für Behandler
      </p>
    </div>

    <div class="flex flex-wrap items-center gap-2">
      <Btn variant="secondary" size="sm" onclick={() => (isDoctorModalOpen = true)}>
        Arzt-Freigabe
      </Btn>
      <Btn variant="secondary" size="sm" onclick={onopenpdf}>PDF-Arztbericht</Btn>
    </div>
  </div>

  <!-- Sub-Navigation Tabs -->
  <div
    class="flex gap-2 overflow-x-auto rounded-2xl border border-border-subtle bg-surface-50 p-1.5"
  >
    <a
      href="/labs/matrix"
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
      'matrix'
        ? 'bg-surface-0 text-primary shadow-sm'
        : 'text-text-muted hover:text-text-main'}"
    >
      <Icon name="show-chart" />
      <span>Laborwert-Verlauf</span>
    </a>

    <a
      href="/labs/panels"
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
      'panels'
        ? 'bg-surface-0 text-primary shadow-sm'
        : 'text-text-muted hover:text-text-main'}"
    >
      <Icon name="biotech" />
      <span>Organprofile</span>
    </a>

    <a
      href="/labs/share"
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
      'share'
        ? 'bg-surface-0 text-primary shadow-sm'
        : 'text-text-muted hover:text-text-main'}"
    >
      <Icon name="insights" />
      <span>Arzt-Freigabe</span>
    </a>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 1: LABORWERT-VERLAUF                                   -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'matrix'}
    <BiomarkerTable />
  {/if}

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 2: ORGAN-SYSTEM PANELS                                 -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'panels'}
    <LabPanelCard />
  {/if}

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 3: ARZT-FREIGABE                                       -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'share'}
    <div class="mx-auto max-w-2xl">
      <E2EEShareCard />
    </div>
  {/if}
</div>

<!-- Modal: Arzt-Freigabe -->
<DoctorShareModal open={isDoctorModalOpen} onclose={() => (isDoctorModalOpen = false)} />
