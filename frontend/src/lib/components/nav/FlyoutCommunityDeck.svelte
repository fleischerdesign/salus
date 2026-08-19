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
    Community &amp; Föderation
  </div>
  <div class="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
    <!-- 1. Challenges & Ranglisten -->
    <button
      type="button"
      onclick={() => onselect('/community/leaderboard')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-left shadow-xs transition-all hover:border-[var(--color-primary)] hover:bg-[var(--bg-surface-0)]"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-[var(--text-main)] transition-colors group-hover:text-[var(--color-primary)]"
      >
        <Icon name="wb-sunny" class="text-[var(--color-circadian)]" /> Challenges &amp; Ranglisten
      </span>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Wettbewerbe, Medaillen, Codes</span>
    </button>

    <!-- 2. Freunde & Verbindungen -->
    <button
      type="button"
      onclick={() => onselect('/community/connections')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-left shadow-xs transition-all hover:border-[var(--color-primary)] hover:bg-[var(--bg-surface-0)]"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-[var(--text-main)] transition-colors group-hover:text-[var(--color-primary)]"
      >
        <Icon name="groups" class="text-[var(--color-primary)]" /> Freunde &amp; Verbindungen
      </span>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">P2P, ActivityPub Freigaben</span>
    </button>

    <!-- 3. Aktivitätsfeed -->
    <button
      type="button"
      onclick={() => onselect('/community/feed')}
      class="group flex cursor-pointer flex-col gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-left shadow-xs transition-all hover:border-[var(--color-primary)] hover:bg-[var(--bg-surface-0)]"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold text-[var(--text-main)] transition-colors group-hover:text-[var(--color-primary)]"
      >
        <Icon name="insights" class="text-[var(--color-activity)]" /> Aktivitätsfeed
      </span>
      <span class="text-[0.6875rem] text-[var(--text-muted)]"
        >Meilensteine befreundeter Profile</span
      >
    </button>
  </div>
</div>
