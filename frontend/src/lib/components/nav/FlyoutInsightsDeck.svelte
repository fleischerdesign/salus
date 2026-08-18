<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';

  let { onselect } = $props<{
    onselect: (path: string) => void;
  }>();
</script>

<div class="p-1">
  <div
    class="mb-2.5 px-1 text-[0.6875rem] font-bold tracking-wider text-[var(--text-soft)] uppercase"
  >
    Analytik & Wissenschaftliche Erkenntnisse
  </div>
  <div class="grid grid-cols-1 gap-2.5 sm:grid-cols-2 md:grid-cols-3">
    <!-- 1. Analytik -->
    <button
      type="button"
      onclick={() => onselect('/analytics')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-left shadow-xs transition-all hover:border-[var(--color-primary)] hover:bg-[var(--bg-surface-0)]"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-[var(--text-main)] transition-colors group-hover:text-[var(--color-primary)]"
      >
        <Icon name="insights" class="text-[var(--color-primary)]" /> Analytik & Trends
      </span>
      <span class="text-[0.6875rem] text-[var(--text-muted)]"
        >Korrelationsmatrix, Was-wäre-wenn</span
      >
    </button>

    <!-- 2. KI-Coach -->
    <button
      type="button"
      onclick={() => onselect('/coach')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-left shadow-xs transition-all hover:border-[var(--color-primary)] hover:bg-[var(--bg-surface-0)]"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-[var(--text-main)] transition-colors group-hover:text-[var(--color-primary)]"
      >
        <Icon name="psychology" class="text-[var(--color-vital)]" /> Evidenz-Coach
      </span>
      <span class="text-[0.6875rem] text-[var(--text-muted)]"
        >Leitlinien-basierte Coaching-Tipps</span
      >
    </button>

    <!-- 3. Achievements -->
    <button
      type="button"
      onclick={() => onselect('/achievements')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-left shadow-xs transition-all hover:border-[var(--color-primary)] hover:bg-[var(--bg-surface-0)]"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-[var(--text-main)] transition-colors group-hover:text-[var(--color-primary)]"
      >
        <Icon name="emoji-events" class="text-[var(--color-circadian)]" /> Achievements & XP
      </span>
      <span class="text-[0.6875rem] text-[var(--text-muted)]"
        >Biometrische Meilensteine & Badges</span
      >
    </button>
  </div>
</div>
