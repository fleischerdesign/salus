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
    Aktivität und Protokolle
  </div>
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-2.5">
    <!-- 1. Workouts -->
    <button
      type="button"
      onclick={() => onselect('workouts-active')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="dumbbell" class="text-[var(--color-activity)]" /> Workouts
        </span>
        <Badge variant="activity">Live</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Live-Einheit, Pläne, Kraftkurven</span>
    </button>

    <!-- 2. Ernährung -->
    <button
      type="button"
      onclick={() => onselect('food')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="food" class="text-[var(--color-activity)]" /> Ernährung
        </span>
        <Badge variant="activity">1.840 kcal</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Nährwerte, Rezepte, Barcodes</span>
    </button>

    <!-- 3. Fasten -->
    <button
      type="button"
      onclick={() => onselect('fasting')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="sun" class="text-[var(--color-circadian)]" /> Fasten
        </span>
        <Badge variant="activity">16:8</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Stoffwechselphasen, Autophagie</span>
    </button>

    <!-- 4. Gewohnheiten -->
    <button
      type="button"
      onclick={() => onselect('habits')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="check" class="text-[var(--color-success)]" /> Gewohnheiten
        </span>
        <Badge variant="success">3/4</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Streaks, Konsistenzmatrizen</span>
    </button>

    <!-- 5. Tagebuch -->
    <button
      type="button"
      onclick={() => onselect('journal')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="sun" class="text-[var(--color-circadian)]" /> Tagebuch
        </span>
        <Badge variant="default">E2EE</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Reflexion, Psychobiometrie</span>
    </button>
  </div>
</div>
