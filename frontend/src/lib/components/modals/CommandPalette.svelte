<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import { goto } from '$app/navigation';

  let { open = false, onclose } = $props<{
    open: boolean;
    onclose: () => void;
  }>();

  let search = $state('');

  interface SearchItem {
    id: string;
    title: string;
    category: string;
    path: string;
    badge?: string;
  }

  const allItems: SearchItem[] = [
    {
      id: '1',
      title: 'Dashboard (Tages-Biostatus, Widgets, Ringe)',
      category: 'Übersicht',
      path: '/'
    },
    {
      id: '2',
      title: 'Vitalparameter & Metrikenkatalog',
      category: 'Klinik',
      path: '/entries',
      badge: 'Katalog'
    },
    {
      id: '3',
      title: 'Workouts: Live-Einheit & Satz-Logging',
      category: 'Training',
      path: '/workouts',
      badge: 'Live'
    },
    {
      id: '4',
      title: 'Ernährung: Tagebuch, Makros & Mahlzeiten',
      category: 'Ernährung',
      path: '/food',
      badge: 'Tagebuch'
    },
    {
      id: '5',
      title: 'Fasten: 16:8 Stoffwechselphasen & Autophagie',
      category: 'Fasten',
      path: '/fasting',
      badge: '16:8'
    },
    {
      id: '6',
      title: 'Klinische Laborwerte & Biomarker-Matrix',
      category: 'Klinik',
      path: '/labs',
      badge: 'PDF'
    },
    {
      id: '7',
      title: 'Medikamente, Supplemente & Vorratsalarm',
      category: 'Klinik',
      path: '/medications',
      badge: 'Plan'
    },
    {
      id: '8',
      title: 'Gewohnheiten, Streaks & Konsistenzmatrix',
      category: 'Habits',
      path: '/habits',
      badge: 'Streaks'
    },
    {
      id: '9',
      title: 'Tagebuch & Psychobiometrie (E2EE)',
      category: 'Journal',
      path: '/journal',
      badge: 'E2EE'
    },
    {
      id: '10',
      title: 'Therapieziele & EMA-Prognosen',
      category: 'Klinik',
      path: '/goals',
      badge: 'Ziele'
    },
    {
      id: '11',
      title: 'Analytik & Pearson-Korrelationsmatrix',
      category: 'Insights',
      path: '/analytics',
      badge: 'Trends'
    },
    {
      id: '12',
      title: 'Evidenz-Coach & Klinische Empfehlungen',
      category: 'Insights',
      path: '/coach',
      badge: 'Coach'
    },
    {
      id: '13',
      title: 'Achievements, XP & Biometrische Level',
      category: 'Insights',
      path: '/achievements',
      badge: 'Level'
    },
    {
      id: '14',
      title: 'Community: Challenges & Ranglisten',
      category: 'Community',
      path: '/community',
      badge: 'Rangliste'
    },
    {
      id: '15',
      title: 'Einstellungen, Zeitzonen & Profil',
      category: 'System',
      path: '/settings',
      badge: 'Profil'
    },
    {
      id: '16',
      title: 'Systemadministration & Server-Status',
      category: 'System',
      path: '/admin',
      badge: 'Admin'
    }
  ];

  let filtered = $derived(
    search.trim() === ''
      ? allItems
      : allItems.filter(
          (i) =>
            i.title.toLowerCase().includes(search.toLowerCase()) ||
            i.category.toLowerCase().includes(search.toLowerCase())
        )
  );

  function selectItem(item: SearchItem) {
    goto(item.path);
    onclose();
  }
</script>

{#if open}
  <div
    class="fixed inset-0 z-100 flex items-start justify-center bg-black/60 px-4 pt-24 backdrop-blur-xs"
    onclick={(e) => {
      if (e.target === e.currentTarget) onclose();
    }}
    role="presentation"
  >
    <div
      class="glass-panel animate-modal-pop w-full max-w-xl overflow-hidden rounded-3xl text-text-main shadow-2xl"
    >
      <!-- Search Input -->
      <div class="flex items-center gap-3 border-b border-border-subtle/70 px-4 py-3.5">
        <Icon name="search" size="md" class="text-text-soft" />
        <input
          type="text"
          bind:value={search}
          placeholder="Wohin möchtest du springen? (z.B. 'Workouts', 'Ernährung', 'Labor', 'Analytik')..."
          class="w-full border-none bg-transparent font-sans text-sm text-text-main outline-none"
        />
        <span class="font-mono text-[0.6875rem] text-text-soft">[ESC]</span>
      </div>

      <!-- Results List -->
      <div class="max-h-96 space-y-1 overflow-y-auto p-2">
        {#each filtered as item}
          <button
            type="button"
            onclick={() => selectItem(item)}
            class="flex w-full cursor-pointer items-center justify-between gap-3 rounded-2xl p-2.5 text-left text-xs transition-colors hover:bg-surface-50"
          >
            <div>
              <span class="block text-xs font-bold text-text-main">{item.title}</span>
              <span class="text-[0.625rem] font-medium text-text-soft">{item.category}</span>
            </div>
            {#if item.badge}
              <Badge variant="default">{item.badge}</Badge>
            {/if}
          </button>
        {/each}
      </div>
    </div>
  </div>
{/if}
