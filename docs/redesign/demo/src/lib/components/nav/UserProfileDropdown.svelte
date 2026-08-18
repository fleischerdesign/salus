<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import type { PageId } from '../../types';

  let {
    onnavigate,
    onopenonboarding,
    onclose
  } = $props<{
    onnavigate: (view: PageId) => void;
    onopenonboarding: () => void;
    onclose: () => void;
  }>();

  function select(view: PageId) {
    onnavigate(view);
    onclose();
  }

  function handleLogout() {
    if (confirm('Möchtest du dich wirklich abmelden? Lokale Daten bleiben sicher gespeichert.')) {
      onclose();
    }
  }
</script>

<div
  class="w-64 glass-panel rounded-3xl p-2 shadow-2xl text-xs text-[var(--text-main)] space-y-1 animate-slide-down"
>
  <!-- User Profile Header -->
  <div class="p-3 bg-[var(--bg-surface-50)]/50 border border-[var(--border-subtle)]/70 rounded-2xl flex items-center gap-3">
    <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-[var(--color-primary)] to-[var(--color-activity)] text-white font-extrabold text-sm flex items-center justify-center shadow-xs shrink-0">
      P
    </div>
    <div class="overflow-hidden flex-1">
      <span class="font-extrabold text-sm text-[var(--text-main)] truncate block">Philipp Fleischer</span>
      <span class="text-[0.6875rem] text-[var(--text-muted)] truncate block">philipp@salus.local</span>
    </div>
  </div>

  <!-- Navigation Action Items -->
  <div class="space-y-0.5 pt-1">
    <button
      type="button"
      onclick={() => select('settings')}
      class="w-full text-left px-3 py-2 rounded-xl hover:bg-[var(--bg-surface-50)]/80 flex items-center gap-2.5 transition-colors cursor-pointer text-xs font-semibold text-[var(--text-main)]"
    >
      <Icon name="sun" size={16} class="text-[var(--color-primary)] opacity-80" />
      <span class="flex-1">Einstellungen</span>
    </button>

    <button
      type="button"
      onclick={() => select('admin')}
      class="w-full text-left px-3 py-2 rounded-xl hover:bg-[var(--bg-surface-50)]/80 flex items-center gap-2.5 transition-colors cursor-pointer text-xs font-semibold text-[var(--text-main)]"
    >
      <Icon name="labs" size={16} class="text-[var(--color-vital)] opacity-80" />
      <span class="flex-1">Administration</span>
    </button>

    <button
      type="button"
      onclick={() => { onopenonboarding(); onclose(); }}
      class="w-full text-left px-3 py-2 rounded-xl hover:bg-[var(--bg-surface-50)]/80 flex items-center gap-2.5 transition-colors cursor-pointer text-xs font-semibold text-[var(--text-main)]"
    >
      <Icon name="sparkles" size={16} class="text-[var(--color-circadian)] opacity-80" />
      <span class="flex-1">Einführung und Tour</span>
    </button>
  </div>
</div>
