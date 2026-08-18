<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import BiomarkerTable from '../labs/BiomarkerTable.svelte';
  import LabPanelCard from '../labs/LabPanelCard.svelte';
  import E2EEShareCard from '../labs/E2EEShareCard.svelte';
  import DoctorShareModal from '../labs/DoctorShareModal.svelte';

  export type LabsTab = 'matrix' | 'panels' | 'share';

  let {
    initialTab = 'matrix',
    onopenpdf,
    ontabchange
  } = $props<{
    initialTab?: LabsTab;
    onopenpdf?: () => void;
    ontabchange?: (tab: LabsTab) => void;
  }>();

  let activeTab = $state<LabsTab>('matrix');
  let isDoctorModalOpen = $state(false);

  $effect(() => {
    activeTab = initialTab;
  });

  function setTab(tab: LabsTab) {
    activeTab = tab;
    ontabchange?.(tab);
  }
</script>

<div class="space-y-6">
  <!-- Header with Fasting State & Actions -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <div class="flex items-center gap-2">
        <h1 class="text-2xl font-extrabold tracking-tight">Klinische Labordiagnostik</h1>
        <Badge variant="success">Nüchternblut (14h Fasten)</Badge>
      </div>
      <p class="text-xs sm:text-sm text-[var(--text-muted)] mt-0.5">
        Multi-Draw Zeitreihen, Organprofile nach ESC/EAS 2024 Leitlinien und ECDH-Arztfreigaben
      </p>
    </div>
    
    <div class="flex items-center gap-2 flex-wrap">
      <Btn variant="secondary" size="sm" onclick={() => isDoctorModalOpen = true}>
         Arzt-Freigabe (E2EE QR)
      </Btn>
      <Btn variant="secondary" size="sm" onclick={onopenpdf}>
        PDF-Arztbericht anzeigen
      </Btn>
    </div>
  </div>

  <!-- Sub-Navigation Tabs -->
  <div class="flex gap-2 bg-[var(--bg-surface-50)] p-1.5 rounded-2xl border border-[var(--border-subtle)] overflow-x-auto">
    <button
      type="button"
      onclick={() => setTab('matrix')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'matrix' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="chart" class="text-[var(--color-primary)]" />
      <span>Verlaufsmatrix</span>
      <Badge variant="success" class="text-[0.625rem]">Optimal</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('panels')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'panels' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="labs" class="text-[var(--color-vital)]" />
      <span>Organprofile</span>
      <Badge variant="default" class="text-[0.625rem]">3 Panels</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('share')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'share' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="insights" class="text-[var(--color-circadian)]" />
      <span>Arztfreigabe</span>
      <Badge variant="default" class="text-[0.625rem]">ECDH</Badge>
    </button>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 1: BIOMARKER-VERLAUFSMATRIX                            -->
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
  <!-- TAB 3: E2EE ARZT-FREIGABE                                  -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'share'}
    <div class="max-w-2xl mx-auto">
      <E2EEShareCard />
    </div>
  {/if}
</div>

<!-- Modal: Asymmetric E2EE Doctor Share (ECDH) -->
<DoctorShareModal
  open={isDoctorModalOpen}
  onclose={() => isDoctorModalOpen = false}
/>
