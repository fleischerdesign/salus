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
    Community und Föderation
  </div>
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-2.5">
    <!-- 1. Challenges -->
    <button
      type="button"
      onclick={() => onselect('community-leaderboard')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="sun" class="text-[var(--color-circadian)]" /> Challenges
        </span>
        <Badge variant="primary">2 Aktiv</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Wettbewerbe, Einladungscodes, Ränge</span>
    </button>

    <!-- 2. Verbindungen -->
    <button
      type="button"
      onclick={() => onselect('community-connections')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="labs" class="text-[var(--color-primary)]" /> Verbindungen
        </span>
        <Badge variant="success">3 Peers</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Peer-to-Peer, granulare Freigaben</span>
    </button>

    <!-- 3. Aktivitätsfeed -->
    <button
      type="button"
      onclick={() => onselect('community-feed')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="insights" class="text-[var(--color-activity)]" /> Aktivitätsfeed
        </span>
        <Badge variant="default">Live</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Meilensteine befreundeter Profile</span>
    </button>

    <!-- 4. Forschung (Open Science) -->
    <button
      type="button"
      onclick={() => onselect('open-science')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="labs" class="text-[var(--color-primary)]" /> Forschung
        </span>
        <Badge variant="primary">Open Science</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Differential Privacy, Studien</span>
    </button>

    <!-- 5. Zugriffsprotokoll -->
    <button
      type="button"
      onclick={() => onselect('community-audit')}
      class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col gap-1 hover:bg-[var(--bg-surface-0)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-xs"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="labs" class="text-[var(--color-vital)]" /> Zugriffsprotokoll
        </span>
        <Badge variant="default">DSGVO</Badge>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Kryptographischer Audit-Trail</span>
    </button>
  </div>
</div>
