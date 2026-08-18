<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import type { PageId } from '../../types';

  let { onselect } = $props<{
    onselect: (view: PageId) => void;
  }>();
</script>

<div class="p-1">
  <div class="text-[0.6875rem] font-bold text-[var(--text-soft)] uppercase tracking-wider mb-2.5 px-1">
    Klinische Diagnostik
  </div>
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5">
    <!-- 1. Vitalparameter -->
    <button
      type="button"
      onclick={() => onselect('metrics-overview')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="sun" class="text-[var(--color-circadian)]" /> Vitalparameter
        </span>
        <Badge variant="primary">5 Gruppen</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Katalog, 7-Tage-Trend, Historie</span>
    </button>

    <!-- 2. Laborwerte -->
    <button
      type="button"
      onclick={() => onselect('labs')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="labs" class="text-[var(--color-vital)]" /> Laborwerte
        </span>
        <Badge variant="success">Optimal</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Biomarker, Organprofile, Arztbericht</span>
    </button>

    <!-- 3. Medikamente -->
    <button
      type="button"
      onclick={() => onselect('medications')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="labs" class="text-[var(--color-vital)]" /> Medikamente
        </span>
        <Badge variant="vital">1 Nachbestellen</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Einnahmeplan, Dosierung, Inventar</span>
    </button>

    <!-- 4. Gesundheitsziele -->
    <button
      type="button"
      onclick={() => onselect('goals')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="chart" class="text-[var(--color-primary)]" /> Gesundheitsziele
        </span>
        <Badge variant="default">4 Ziele</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Fortschritt, statistische Prognosen</span>
    </button>
  </div>
</div>
