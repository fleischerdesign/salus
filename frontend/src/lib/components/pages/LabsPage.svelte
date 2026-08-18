<script lang="ts">
  import { page } from '$app/state';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
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
  <!-- Header with Fasting State & Actions -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <div class="flex items-center gap-2">
        <h1 class="text-2xl font-extrabold tracking-tight">Klinische Labordiagnostik</h1>
        <Badge variant="success">Nüchternblut (14h Fasten)</Badge>
      </div>
      <p class="mt-0.5 text-xs text-[var(--text-muted)] sm:text-sm">
        Multi-Draw Zeitreihen, Organprofile nach ESC/EAS 2024 Leitlinien und ECDH-Arztfreigaben
      </p>
    </div>

    <div class="flex flex-wrap items-center gap-2">
      <Btn variant="secondary" size="sm" onclick={() => (isDoctorModalOpen = true)}>
        Arzt-Freigabe (E2EE QR)
      </Btn>
      <Btn variant="secondary" size="sm" onclick={onopenpdf}>PDF-Arztbericht anzeigen</Btn>
    </div>
  </div>

  <!-- Sub-Navigation Tabs -->
  <div
    class="flex gap-2 overflow-x-auto rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-1.5"
  >
    <a
      href="/labs/matrix"
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
      'matrix'
        ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
        : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="show-chart" class="text-[var(--color-primary)]" />
      <span>Verlaufsmatrix</span>
      <Badge variant="success" class="text-[0.625rem]">Optimal</Badge>
    </a>

    <a
      href="/labs/panels"
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
      'panels'
        ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
        : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="labs" class="text-[var(--color-vital)]" />
      <span>Organprofile</span>
      <Badge variant="default" class="text-[0.625rem]">3 Panels</Badge>
    </a>

    <a
      href="/labs/share"
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
      'share'
        ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
        : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="insights" class="text-[var(--color-circadian)]" />
      <span>Arztfreigabe</span>
      <Badge variant="default" class="text-[0.625rem]">ECDH</Badge>
    </a>
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
    <div class="mx-auto max-w-2xl">
      <E2EEShareCard />
    </div>
  {/if}
</div>

<!-- Modal: Asymmetric E2EE Doctor Share (ECDH) -->
<DoctorShareModal open={isDoctorModalOpen} onclose={() => (isDoctorModalOpen = false)} />
