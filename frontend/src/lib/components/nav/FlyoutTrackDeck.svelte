<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';

  let { onselect } = $props<{
    onselect: (path: string) => void;
  }>();
</script>

<div class="p-1">
  <div class="mb-2.5 px-1 text-[0.6875rem] font-bold tracking-wider text-text-soft uppercase">
    Aktivität und Protokolle
  </div>
  <div class="grid grid-cols-1 gap-2.5 sm:grid-cols-2 md:grid-cols-5">
    <!-- 1. Workouts -->
    <button
      type="button"
      onclick={() => onselect('/workouts')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-border-subtle bg-surface-50 p-3 text-left shadow-xs transition-all hover:border-primary hover:bg-surface-0"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-text-main transition-colors group-hover:text-primary"
      >
        <Icon name="fitness-center" class="text-activity" /> Workouts
      </span>
      <span class="text-[0.6875rem] text-text-muted">Live-Einheit, Pläne, Kraftkurven</span>
    </button>

    <!-- 2. Ernährung -->
    <button
      type="button"
      onclick={() => onselect('/food')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-border-subtle bg-surface-50 p-3 text-left shadow-xs transition-all hover:border-primary hover:bg-surface-0"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-text-main transition-colors group-hover:text-primary"
      >
        <Icon name="restaurant" class="text-activity" /> Ernährung
      </span>
      <span class="text-[0.6875rem] text-text-muted">Nährwerte, Rezepte, Barcodes</span>
    </button>

    <!-- 3. Fasten -->
    <button
      type="button"
      onclick={() => onselect('/fasting')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-border-subtle bg-surface-50 p-3 text-left shadow-xs transition-all hover:border-primary hover:bg-surface-0"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-text-main transition-colors group-hover:text-primary"
      >
        <Icon name="timer" class="text-circadian" /> Fasten
      </span>
      <span class="text-[0.6875rem] text-text-muted">Stoffwechselphasen, Autophagie</span>
    </button>

    <!-- 4. Gewohnheiten -->
    <button
      type="button"
      onclick={() => onselect('/habits')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-border-subtle bg-surface-50 p-3 text-left shadow-xs transition-all hover:border-primary hover:bg-surface-0"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-text-main transition-colors group-hover:text-primary"
      >
        <Icon name="check-circle" class="text-success" /> Gewohnheiten
      </span>
      <span class="text-[0.6875rem] text-text-muted">Streaks, Konsistenzmatrizen</span>
    </button>

    <!-- 5. Tagebuch -->
    <button
      type="button"
      onclick={() => onselect('/journal')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-border-subtle bg-surface-50 p-3 text-left shadow-xs transition-all hover:border-primary hover:bg-surface-0"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-text-main transition-colors group-hover:text-primary"
      >
        <Icon name="edit-note" class="text-circadian" /> Tagebuch
      </span>
      <span class="text-[0.6875rem] text-text-muted">Reflexion, Psychobiometrie</span>
    </button>
  </div>
</div>
