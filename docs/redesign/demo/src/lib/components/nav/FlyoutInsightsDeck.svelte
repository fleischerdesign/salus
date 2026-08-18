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
    Wissenschaftliche Intelligenz
  </div>
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
    <!-- 1. Analytik -->
    <button
      type="button"
      onclick={() => onselect('insights')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3.5 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="insights" class="text-[var(--color-primary)]" /> Analytik
        </span>
        <Badge variant="primary">Pearson r</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Zeitreihen, Korrelationen, Simulationen</span>
    </button>

    <!-- 2. Empfehlungen -->
    <button
      type="button"
      onclick={() => onselect('coach')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3.5 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="sun" class="text-[var(--color-circadian)]" /> Empfehlungen
        </span>
        <Badge variant="activity">3 Tipps</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Evidenzbasierte Langlebigkeits-Tipps</span>
    </button>

    <!-- 3. Erfolge -->
    <button
      type="button"
      onclick={() => onselect('achievements')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3.5 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="sun" class="text-[var(--color-circadian)]" /> Erfolge
        </span>
        <Badge variant="default">Lvl 12</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Akademische Meilensteine, Rangstufen</span>
    </button>
  </div>
</div>
