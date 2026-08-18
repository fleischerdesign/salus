<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import OpenSciencePage from './OpenSciencePage.svelte';

  export type CommunityTab = 'leaderboard' | 'connections' | 'feed' | 'audit' | 'open_science';

  let {
    initialTab = 'leaderboard',
    ontabchange
  } = $props<{
    initialTab?: CommunityTab;
    ontabchange?: (tab: CommunityTab) => void;
  }>();

  let activeTab = $state<CommunityTab>('leaderboard');

  $effect(() => {
    activeTab = initialTab;
  });

  function setTab(tab: CommunityTab) {
    activeTab = tab;
    ontabchange?.(tab);
  }

  // ─── LEADERBOARD STATE ───
  interface Challenge {
    id: string;
    name: string;
    sourceDataType: 'steps' | 'workouts' | 'sleep' | 'water' | 'fasting';
    timeFrame: 'Rolling 7 Tage' | 'Rolling 30 Tage';
    participants: number;
    userRank: number;
    userScore: string;
    unit: string;
    isCreator: boolean;
    members: Array<{ rank: number; name: string; handle: string; instance: string; score: string; isYou?: boolean }>;
  }

  let challenges = $state<Challenge[]>([
    {
      id: 'c1',
      name: 'DACH 10.000 Schritte Challenge',
      sourceDataType: 'steps',
      timeFrame: 'Rolling 7 Tage',
      participants: 8,
      userRank: 2,
      userScore: '74.280',
      unit: 'Schritte',
      isCreator: true,
      members: [
        { rank: 1, name: 'Dr. med. Longevity', handle: '@longevity_doc', instance: 'charite.de', score: '82.450 Schritte' },
        { rank: 2, name: 'Philipp (Du)', handle: '@philipp', instance: 'salus.local', score: '74.280 Schritte', isYou: true },
        { rank: 3, name: 'Sarah Biohacker', handle: '@sarah_bio', instance: 'zurich.health', score: '69.100 Schritte' },
        { rank: 4, name: 'Marc Physio', handle: '@marc_fit', instance: 'tum.de', score: '61.400 Schritte' }
      ]
    },
    {
      id: 'c2',
      name: 'Autophagie & Fasten-Disziplin',
      sourceDataType: 'fasting',
      timeFrame: 'Rolling 30 Tage',
      participants: 5,
      userRank: 1,
      userScore: '480',
      unit: 'Std',
      isCreator: false,
      members: [
        { rank: 1, name: 'Philipp (Du)', handle: '@philipp', instance: 'salus.local', score: '480 Std (16:8)', isYou: true },
        { rank: 2, name: 'KetoScientist', handle: '@ketomaster', instance: 'stanford.edu', score: '462 Std' },
        { rank: 3, name: 'Elena Fasting', handle: '@elena_f', instance: 'berlin.bio', score: '420 Std' }
      ]
    }
  ]);

  let selectedChallenge = $state<Challenge>(challenges[0]);
  let inviteCode = $state('');
  let createName = $state('');
  let createMetric = $state<'steps' | 'workouts' | 'sleep' | 'water' | 'fasting'>('steps');
  let createTimeframe = $state<'weekly' | 'monthly'>('weekly');

  function handleJoinCode() {
    if (!inviteCode) return;
    alert(`Challenge mit Code "${inviteCode}" erfolgreich beigetreten!`);
    inviteCode = '';
  }

  function handleCreateChallenge() {
    if (!createName) return;
    const newC: Challenge = {
      id: 'c' + (challenges.length + 1),
      name: createName,
      sourceDataType: createMetric,
      timeFrame: createTimeframe === 'weekly' ? 'Rolling 7 Tage' : 'Rolling 30 Tage',
      participants: 1,
      userRank: 1,
      userScore: '0',
      unit: createMetric === 'steps' ? 'Schritte' : 'Std',
      isCreator: true,
      members: [{ rank: 1, name: 'Philipp (Du)', handle: '@philipp', instance: 'salus.local', score: '0', isYou: true }]
    };
    challenges.push(newC);
    selectedChallenge = newC;
    createName = '';
    alert('Neue Challenge erfolgreich erstellt!');
  }

  // ─── CONNECTIONS & P2P STATE ───
  interface PeerConnection {
    id: string;
    handle: string;
    displayName: string;
    instance: string;
    status: 'mutual' | 'incoming' | 'outgoing' | 'pending';
    isRemote: boolean;
    sharedMetrics: Array<{ name: string; level: string; direction: 'in' | 'out' }>;
    lastSync: string;
  }

  let peers = $state<PeerConnection[]>([
    {
      id: 'p1',
      handle: '@dr_longevity',
      displayName: 'Dr. med. Longevity',
      instance: 'charite.de',
      status: 'mutual',
      isRemote: true,
      sharedMetrics: [
        { name: 'Kardiovaskulär (Blutdruck, HRV)', level: 'Tagesmittelwert', direction: 'out' },
        { name: 'Schlaf & Erholung', level: 'Vollständige Rohdaten', direction: 'out' },
        { name: 'Aktivität (Schritte)', level: 'Tagesmittelwert', direction: 'in' }
      ],
      lastSync: 'vor 5 Minuten'
    },
    {
      id: 'p2',
      handle: '@sarah_bio',
      displayName: 'Sarah Biohacker',
      instance: 'zurich.health',
      status: 'outgoing',
      isRemote: true,
      sharedMetrics: [
        { name: 'Aktivität & Tonnage', level: 'Aggregiert', direction: 'out' }
      ],
      lastSync: 'vor 2 Stunden'
    },
    {
      id: 'p3',
      handle: '@marc_fit',
      displayName: 'Marc Physio',
      instance: 'tum.de',
      status: 'pending',
      isRemote: true,
      sharedMetrics: [
        { name: 'Workouts & 1RM', level: 'Anfrage ausstehend', direction: 'in' }
      ],
      lastSync: 'Anfrage offen'
    }
  ]);

  let newPeerHandle = $state('');

  function handleInvitePeer() {
    if (!newPeerHandle) return;
    alert(`Verbindungsanfrage an ${newPeerHandle} über ActivityPub / WebFinger gesendet!`);
    newPeerHandle = '';
  }

  // ─── ACTIVITY FEED STATE ───
  const feedItems = [
    {
      id: 'f1',
      user: 'Dr. med. Longevity',
      handle: '@dr_longevity@charite.de',
      action: 'hat 30 Tage Fasten-Streak abgeschlossen',
      metric: 'Autophagie: 16:8 konsistent',
      time: 'vor 18 Minuten',
      likes: 4
    },
    {
      id: 'f2',
      user: 'Philipp (Du)',
      handle: '@philipp@salus.local',
      action: 'hat ein neues 1RM im Bankdrücken aufgestellt',
      metric: '143.0 kg (+15.3%)',
      time: 'vor 2 Stunden',
      likes: 6
    },
    {
      id: 'f3',
      user: 'Sarah Biohacker',
      handle: '@sarah_bio@zurich.health',
      action: 'hat die 10.000 Schritte Challenge für August erreicht',
      metric: 'Ø 11.420 Schritte / Tag',
      time: 'vor 4 Stunden',
      likes: 3
    }
  ];

  // ─── AUDIT ACCESS LOG STATE ───
  const auditLogs = [
    { id: 'a1', timestamp: '14.08.2026 17:45', peer: '@dr_longevity@charite.de', metric: 'Blutdruck (Systolisch/Diastolisch)', level: 'Tagesmittelwert', ip: '141.20.18.9 (Charité Berlin)' },
    { id: 'a2', timestamp: '14.08.2026 14:12', peer: '@dr_longevity@charite.de', metric: 'Schlafdauer & Erholungs-Score', level: 'Rohdaten', ip: '141.20.18.9 (Charité Berlin)' },
    { id: 'a3', timestamp: '13.08.2026 09:30', peer: '@sarah_bio@zurich.health', metric: 'Schritt-Challenge Aggregat', level: 'Aggregiert', ip: '195.176.255.4 (ETH Zürich)' }
  ];
</script>

<div class="space-y-6">
  <!-- Page Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Community und Föderation</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Datenschutzkonforme Peer-Freigaben und dezentrale Challenges via ActivityPub
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Föderation: Aktiv (@philipp@salus.local)</Badge>
    </div>
  </div>

  <!-- Primary Sub-Navigation Tabs -->
  <div class="flex gap-2 bg-[var(--bg-surface-50)] p-1.5 rounded-2xl border border-[var(--border-subtle)] overflow-x-auto">
    <button
      type="button"
      onclick={() => setTab('leaderboard')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'leaderboard' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="sun" class="text-[var(--color-circadian)]" />
      <span>Challenges</span>
      <Badge variant="primary" class="text-[0.625rem]">{challenges.length}</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('connections')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'connections' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="labs" class="text-[var(--color-primary)]" />
      <span>Verbindungen</span>
      <Badge variant="default" class="text-[0.625rem]">{peers.length}</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('feed')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'feed' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="insights" class="text-[var(--color-activity)]" />
      <span>Aktivitätsfeed</span>
    </button>

    <button
      type="button"
      onclick={() => setTab('audit')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'audit' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="labs" class="text-[var(--color-vital)]" />
      <span>Zugriffsprotokoll</span>
    </button>

    <button
      type="button"
      onclick={() => setTab('open_science')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'open_science' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="labs" class="text-[var(--color-primary)]" />
      <span>Forschung</span>
      <Badge variant="primary" class="text-[0.625rem]">Open Science</Badge>
    </button>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 1: CHALLENGES & LEADERBOARDS                           -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'leaderboard'}
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
      
      <!-- Left: Active Challenge List & Detail (8-Col) -->
      <div class="lg:col-span-8 space-y-4">
        <!-- Challenge Selector Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {#each challenges as c}
            <button
              type="button"
              onclick={() => selectedChallenge = c}
              class="text-left bg-[var(--bg-surface-0)] border rounded-2xl p-4 transition-all cursor-pointer shadow-[var(--shadow-card)] {selectedChallenge.id === c.id ? 'border-[var(--color-primary)] ring-2 ring-[var(--color-primary)]/20' : 'border-[var(--border-subtle)] hover:border-[var(--border-strong)]'}"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs font-bold text-[var(--text-main)]">{c.name}</span>
                <Badge variant="default" class="text-[0.625rem]">{c.timeFrame}</Badge>
              </div>
              <p class="text-[0.6875rem] text-[var(--text-muted)]">{c.participants} Teilnehmer • {c.sourceDataType}</p>

              <div class="mt-3 pt-2 border-t border-[var(--border-subtle)] flex justify-between items-center text-xs font-mono">
                <span>Dein Rang: <strong class="text-[var(--color-primary)] font-bold">#{c.userRank}</strong></span>
                <span>Score: <strong class="text-[var(--text-main)]">{c.userScore} {c.unit}</strong></span>
              </div>
            </button>
          {/each}
        </div>

        <!-- Selected Challenge Leaderboard Table -->
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
          <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
            <div>
              <div class="flex items-center gap-2">
                <h2 class="text-base font-extrabold text-[var(--text-main)]">{selectedChallenge.name}</h2>
                <Badge variant="success">Aktiv</Badge>
              </div>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">{selectedChallenge.timeFrame} • Einladungscode: <code class="font-mono bg-[var(--bg-surface-50)] px-1.5 py-0.5 rounded text-[var(--color-primary)]">SALUS-{selectedChallenge.id.toUpperCase()}-2026</code></p>
            </div>
            <Btn variant="secondary" size="sm" onclick={() => alert('Einladungslink in Zwischenablage kopiert!')}>
              Teilnehmer einladen
            </Btn>
          </div>

          <!-- Members Podium List -->
          <div class="space-y-2.5">
            {#each selectedChallenge.members as m}
              <div
                class="flex items-center justify-between p-3.5 rounded-xl border transition-all {m.isYou ? 'bg-[var(--color-primary-soft)]/20 border-[var(--color-primary)] shadow-xs' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)]'}"
              >
                <div class="flex items-center gap-3">
                  <span class="w-7 h-7 rounded-full flex items-center justify-center font-mono font-extrabold text-xs {m.rank === 1 ? 'bg-amber-400 text-black shadow-xs' : m.rank === 2 ? 'bg-slate-300 text-black' : m.rank === 3 ? 'bg-amber-700 text-white' : 'bg-[var(--bg-surface-100)] text-[var(--text-muted)]'}">
                    {m.rank === 1 ? 'Rang 1' : m.rank === 2 ? 'Rang 2' : m.rank === 3 ? 'Rang 3' : `#${m.rank}`}
                  </span>
                  <div>
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-bold text-[var(--text-main)]">{m.name}</span>
                      {#if m.isYou}
                        <Badge variant="primary" class="text-[0.5625rem]">Du</Badge>
                      {/if}
                    </div>
                    <span class="text-[0.6875rem] text-[var(--text-soft)] font-mono">{m.handle}@{m.instance}</span>
                  </div>
                </div>

                <div class="font-mono text-sm font-bold text-[var(--text-main)]">
                  {m.score}
                </div>
              </div>
            {/each}
          </div>
        </div>
      </div>

      <!-- Right: Join Code & Create Challenge Forms (4-Col) -->
      <div class="lg:col-span-4 space-y-4">
        <!-- Join via Code Card -->
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
          <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)] mb-2">
            <Icon name="sun" class="text-[var(--color-primary)]" />
            <span>Challenge beitreten</span>
          </div>
          <p class="text-xs text-[var(--text-muted)] mb-3">
            Gib den 8-stelligen Einladungscode eines Freundes ein:
          </p>
          <div class="space-y-2">
            <input
              type="text"
              placeholder="z.B. A1B2-C3D4..."
              bind:value={inviteCode}
              class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-xs font-mono uppercase text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
            />
            <Btn variant="primary" class="w-full" onclick={handleJoinCode}>
              Mit Code beitreten
            </Btn>
          </div>
        </div>

        <!-- Create Challenge Card -->
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
          <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)] mb-2">
            <Icon name="plus" class="text-[var(--color-activity)]" />
            <span>Neue Challenge erstellen</span>
          </div>
          <div class="space-y-3">
            <div>
              <label for="ch-name" class="block text-xs font-semibold text-[var(--text-muted)] mb-1">Name der Challenge</label>
              <input
                id="ch-name"
                type="text"
                placeholder="z.B. Herbst Step-Cup..."
                bind:value={createName}
                class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
              />
            </div>
            <div>
              <label for="ch-metric" class="block text-xs font-semibold text-[var(--text-muted)] mb-1">Metrik-Typ</label>
              <select
                id="ch-metric"
                bind:value={createMetric}
                class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
              >
                <option value="steps">Schritte (Steps)</option>
                <option value="workouts">Workouts & Kraftsport</option>
                <option value="sleep">Schlafdauer & Erholung</option>
                <option value="water">Wasserhaushalt (Hydration)</option>
                <option value="fasting">Intervallfasten</option>
              </select>
            </div>
            <div>
              <label for="ch-time" class="block text-xs font-semibold text-[var(--text-muted)] mb-1">Zeitraum</label>
              <select
                id="ch-time"
                bind:value={createTimeframe}
                class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
              >
                <option value="weekly">Rolling 7 Tage (Wöchentlich)</option>
                <option value="monthly">Rolling 30 Tage (Monatlich)</option>
              </select>
            </div>
            <Btn variant="primary" class="w-full" onclick={handleCreateChallenge}>
              Challenge starten
            </Btn>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 2: P2P CONNECTIONS & FREIGABEN                         -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'connections'}
    <div class="space-y-5">
      <!-- Peer Invite Card -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
          <div>
            <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
              <Icon name="labs" class="text-[var(--color-primary)]" />
              <span>Neuen Peer einladen (P2P Data Sharing)</span>
            </div>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">
              Gib das Handle deines Freundes oder Arztes ein (z. B. <code class="font-mono">@name</code> oder föderiert <code class="font-mono">@name:domain.com</code>)
            </p>
          </div>
        </div>

        <div class="flex gap-2 max-w-lg">
          <input
            type="text"
            placeholder="@benutzername oder @dr_arzt:klinik.de..."
            bind:value={newPeerHandle}
            class="flex-1 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl px-3.5 py-2 text-xs text-[var(--text-main)] font-mono outline-none focus:border-[var(--color-primary)]"
          />
          <Btn variant="primary" size="sm" onclick={handleInvitePeer}>
            Einladung senden
          </Btn>
        </div>
      </div>

      <!-- Active Peer Connections Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        {#each peers as p}
          <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] flex flex-col justify-between">
            <div>
              <div class="flex items-start justify-between mb-2">
                <div>
                  <h3 class="text-sm font-bold text-[var(--text-main)]">{p.displayName}</h3>
                  <span class="text-xs text-[var(--text-muted)] font-mono">{p.handle}@{p.instance}</span>
                </div>
                <Badge variant={p.status === 'mutual' ? 'success' : p.status === 'pending' ? 'vital' : 'primary'}>
                  {p.status === 'mutual' ? 'Beidseitig' : p.status === 'pending' ? 'Ausstehend' : 'Ausgehend'}
                </Badge>
              </div>

              <!-- Shared Metrics Pills -->
              <div class="space-y-1.5 my-3">
                <span class="text-[0.6875rem] text-[var(--text-soft)] uppercase font-mono block">Geteilte Metriken:</span>
                {#each p.sharedMetrics as m}
                  <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-lg p-2 text-xs flex justify-between items-center">
                    <span class="font-semibold text-[var(--text-main)]">{m.name}</span>
                    <span class="text-[0.625rem] font-mono text-[var(--text-muted)]">{m.level}</span>
                  </div>
                {/each}
              </div>
            </div>

            <div class="pt-3 border-t border-[var(--border-subtle)] flex items-center justify-between text-xs">
              <span class="text-[0.6875rem] text-[var(--text-soft)] font-mono">{p.lastSync}</span>
              <button type="button" class="text-[var(--color-vital)] text-xs hover:underline cursor-pointer" onclick={() => alert('Freigabe widerrufen')}>
                Widerrufen
              </button>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 3: FEDERATED ACTIVITY FEED                             -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'feed'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] max-w-2xl mx-auto space-y-4">
      <div class="flex items-center justify-between pb-3 border-b border-[var(--border-subtle)]">
        <span class="text-sm font-bold">Aktivitäts-Feed deiner Verbindungen</span>
        <span class="text-xs text-[var(--text-muted)] font-mono">Live via ActivityPub</span>
      </div>

      <div class="space-y-4">
        {#each feedItems as item}
          <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-4 space-y-2">
            <div class="flex items-center justify-between">
              <div>
                <span class="text-xs font-bold text-[var(--color-primary)]">{item.user}</span>
                <span class="text-[0.6875rem] text-[var(--text-soft)] font-mono ml-1">{item.handle}</span>
              </div>
              <span class="text-[0.6875rem] text-[var(--text-soft)] font-mono">{item.time}</span>
            </div>
            <p class="text-xs font-semibold text-[var(--text-main)]">{item.action}</p>
            <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-lg p-2 text-xs font-mono text-[var(--color-success)] font-bold inline-block">
              {item.metric}
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 4: PRIVACY & AUDIT ACCESS LOG                          -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'audit'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] space-y-4">
      <div class="flex items-center justify-between pb-3 border-b border-[var(--border-subtle)]">
        <div>
          <span class="text-sm font-bold">Kryptographisches Zugriffs-Protokoll (Audit Log)</span>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">Lückenlose Protokollierung aller Remote-Datenabfragen auf deine pseudonymisierten Daten</p>
        </div>
        <Badge variant="success">DSGVO / GDPR Konform</Badge>
      </div>

      <div class="w-full overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.6875rem]">
              <th class="py-2.5 px-3">Zeitstempel</th>
              <th class="py-2.5 px-3">Anfragender Peer</th>
              <th class="py-2.5 px-3">Abgefragte Metrik</th>
              <th class="py-2.5 px-3">Aggregations-Stufe</th>
              <th class="py-2.5 px-3">IP / Server-Instanz</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border-subtle)] font-mono">
            {#each auditLogs as log}
              <tr>
                <td class="py-2.5 px-3 text-[var(--text-soft)]">{log.timestamp}</td>
                <td class="py-2.5 px-3 font-bold text-[var(--color-primary)]">{log.peer}</td>
                <td class="py-2.5 px-3 font-sans font-semibold text-[var(--text-main)]">{log.metric}</td>
                <td class="py-2.5 px-3 font-sans"><Badge variant="default">{log.level}</Badge></td>
                <td class="py-2.5 px-3 text-[var(--text-soft)] text-[0.6875rem]">{log.ip}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {:else if activeTab === 'open_science'}
    <OpenSciencePage />
  {/if}
</div>
