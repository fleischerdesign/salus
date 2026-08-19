<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';

  let { onselect } = $props<{
    onselect: (path: string) => void;
  }>();
</script>

<div class="p-1">
  <div class="mb-2.5 px-1 text-[0.6875rem] font-bold tracking-wider text-text-soft uppercase">
    Klinik &amp; Vitaldaten
  </div>
  <div class="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
    <!-- 1. Laborwerte -->
    <button
      type="button"
      onclick={() => onselect('/labs')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-border-subtle bg-surface-50 p-3 text-left shadow-xs transition-all hover:border-primary hover:bg-surface-0"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-text-main transition-colors group-hover:text-primary"
      >
        <Icon name="science" class="text-vital" /> Labor &amp; Blutbild
      </span>
      <span class="text-[0.6875rem] text-text-muted">Biomarker, Panels, Arzt-Freigabe</span>
    </button>

    <!-- 2. Medikamente -->
    <button
      type="button"
      onclick={() => onselect('/medications')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-border-subtle bg-surface-50 p-3 text-left shadow-xs transition-all hover:border-primary hover:bg-surface-0"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-text-main transition-colors group-hover:text-primary"
      >
        <Icon name="medication" class="text-primary" /> Medikamente
      </span>
      <span class="text-[0.6875rem] text-text-muted">Einnahmeplan, Vorrats-Tracker</span>
    </button>

    <!-- 3. Metriken & Ziele -->
    <button
      type="button"
      onclick={() => onselect('/entries')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-border-subtle bg-surface-50 p-3 text-left shadow-xs transition-all hover:border-primary hover:bg-surface-0"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-text-main transition-colors group-hover:text-primary"
      >
        <Icon name="monitoring" class="text-vital" /> Metriken &amp; Ziele
      </span>
      <span class="text-[0.6875rem] text-text-muted">Vitaldaten, Sollwerte &amp; Prognosen</span>
    </button>
  </div>
</div>
