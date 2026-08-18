<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import type { PageId } from '../../types';

  let {
    open = false,
    onclose,
    onnavigate
  } = $props<{
    open: boolean;
    onclose: () => void;
    onnavigate: (view: PageId, groupKey?: string, metricCode?: string) => void;
  }>();

  let search = $state('');

  interface SearchItem {
    id: string;
    title: string;
    category: string;
    view: PageId;
    groupKey?: string;
    metricCode?: string;
    badge?: string;
  }

  const allItems: SearchItem[] = [
    { id: '1', title: 'Heute (Tages-Biostatus und Ringe)', category: 'Übersicht', view: 'dashboard' },
    { id: '2', title: 'Vitalparameter und Metrikenkatalog', category: 'Metriken', view: 'metrics-overview', badge: 'Katalog' },
    { id: '3', title: 'Kardiovaskuläre Vitalwerte (Blutdruck, Puls, HRV)', category: 'Metriken', view: 'metric-group-detail', groupKey: 'blood_pressure', badge: 'Gruppe' },
    { id: '4', title: 'Körperzusammensetzung (Gewicht, KFA, Muskelmasse)', category: 'Metriken', view: 'metric-group-detail', groupKey: 'body_composition', badge: 'Gruppe' },
    { id: '5', title: 'Systolischer Blutdruck (118 mmHg)', category: 'Metriken', view: 'metric-single-detail', groupKey: 'blood_pressure', metricCode: 'systolic_bp', badge: 'Einzelmetrik' },
    { id: '6', title: 'Körpergewicht (81.8 kg)', category: 'Metriken', view: 'metric-single-detail', groupKey: 'body_composition', metricCode: 'weight', badge: 'Einzelmetrik' },
    { id: '7', title: 'Workouts: Live-Einheit (Push Day A)', category: 'Training', view: 'workouts-active', badge: 'Live' },
    { id: '8', title: 'Workouts: Trainingspläne (PPL, Upper/Lower)', category: 'Training', view: 'workouts-plans', badge: '3 Pläne' },
    { id: '9', title: 'Workouts: Historie und Tonnage', category: 'Training', view: 'workouts-sessions', badge: 'Historie' },
    { id: '10', title: 'Workouts: Übungskatalog und Kraftkurven', category: 'Training', view: 'workouts-exercises', badge: '1RM' },
    { id: '11', title: 'Ernährung: Tagebuch und Makronährstoffe', category: 'Ernährung', view: 'food', badge: '1.840 kcal' },
    { id: '12', title: 'Ernährung: Rezeptdatenbank', category: 'Ernährung', view: 'food-recipes', badge: 'Rezepte' },
    { id: '13', title: 'Ernährung: Lebensmittelkatalog und Nährwerte', category: 'Ernährung', view: 'food-database', badge: 'Barcode' },
    { id: '14', title: 'Klinische Laborwerte und Biomarkermatrix', category: 'Medizin', view: 'labs', badge: 'ESC 2024' },
    { id: '15', title: 'Medikamente, Supplemente und Inventaralarm', category: 'Medizin', view: 'medications', badge: 'Nachbestellen' },
    { id: '16', title: 'Gewohnheiten, Streaks und Konsistenz', category: 'Habits', view: 'habits', badge: '3/4' },
    { id: '17', title: 'Tagebuch und Psychobiometrie (Valenz/Arousal)', category: 'Journal', view: 'journal', badge: 'E2EE' },
    { id: '18', title: 'Community: Challenges und Ranglisten', category: 'Community', view: 'community-leaderboard', badge: 'Gold #2' },
    { id: '19', title: 'Community: Verbindungen und ActivityPub Freigaben', category: 'Community', view: 'community-connections', badge: '3 Peers' },
    { id: '20', title: 'Community: Aktivitätsfeed befreundeter Profile', category: 'Community', view: 'community-feed', badge: 'Feed' },
    { id: '21', title: 'Community: Zugriffsprotokoll und Datenschutz', category: 'Community', view: 'community-audit', badge: 'DSGVO' },
    { id: '22', title: 'Community: Forschung und Open Science (Differential Privacy)', category: 'Community', view: 'open-science', badge: 'Studien' },
    { id: '23', title: 'Wissenschaftliche Analytik und Prognosen', category: 'Insights', view: 'insights', badge: 'Pearson r' },
    { id: '24', title: 'Gesundheitsempfehlungen und Coaching', category: 'Insights', view: 'coach', badge: '3 Tipps' },
    { id: '25', title: 'Erfolge und Meilensteine', category: 'Insights', view: 'achievements', badge: 'Lvl 12' },
    { id: '26', title: 'Einstellungen und Profil', category: 'System', view: 'settings', badge: 'Profil' },
    { id: '27', title: 'Systemadministration und Server-Status', category: 'System', view: 'admin', badge: 'Admin' },
    { id: '28', title: 'Datenqualitäts-Engine und Plausibilitäts-Sweep', category: 'System', view: 'admin', badge: 'Qualität' }
  ];

  let filtered = $derived(
    search.trim() === ''
      ? allItems
      : allItems.filter(
          i =>
            i.title.toLowerCase().includes(search.toLowerCase()) ||
            i.category.toLowerCase().includes(search.toLowerCase())
        )
  );

  function selectItem(item: SearchItem) {
    onnavigate(item.view, item.groupKey, item.metricCode);
    onclose();
  }
</script>

{#if open}
  <div
    class="fixed inset-0 bg-black/60 backdrop-blur-xs z-100 flex items-start justify-center pt-24 px-4"
    onclick={(e) => {
      if (e.target === e.currentTarget) onclose();
    }}
    role="presentation"
  >
    <div
      class="glass-panel rounded-3xl w-full max-w-xl shadow-2xl overflow-hidden animate-modal-pop"
    >
      <!-- Search Input -->
      <div class="flex items-center gap-3 px-4 py-3.5 border-b border-[var(--border-subtle)]/70">
        <Icon name="search" size={18} class="text-[var(--text-soft)]" />
        <input
          type="text"
          bind:value={search}
          placeholder="Wohin möchtest du springen? (z.B. 'Pläne', 'Sessions', '1RM', 'Rezepte', 'Community', 'Audit')..."
          class="w-full border-none bg-transparent text-sm text-[var(--text-main)] outline-none font-sans"
        />
        <span class="text-[0.6875rem] font-mono text-[var(--text-soft)]">[ESC]</span>
      </div>

      <!-- Results List -->
      <div class="max-h-96 overflow-y-auto p-2 space-y-1">
        {#each filtered as item}
          <button
            type="button"
            onclick={() => selectItem(item)}
            class="w-full text-left px-3.5 py-2.5 rounded-xl hover:bg-[var(--bg-surface-50)] flex items-center justify-between transition-colors cursor-pointer group"
          >
            <div class="flex items-center gap-3">
              <span class="text-xs font-semibold text-[var(--text-main)] group-hover:text-[var(--color-primary)]">
                {item.title}
              </span>
            </div>
            <div class="flex items-center gap-2">
              {#if item.badge}
                <Badge variant="primary" class="text-[0.625rem]">{item.badge}</Badge>
              {/if}
              <span class="text-[0.6875rem] font-mono text-[var(--text-soft)]">{item.category}</span>
            </div>
          </button>
        {/each}
      </div>
    </div>
  </div>
{/if}

<style>
  @keyframes cmdkScale {
    from { opacity: 0; transform: scale(0.96); }
    to { opacity: 1; transform: scale(1); }
  }
</style>
