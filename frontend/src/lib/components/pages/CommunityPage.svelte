<script lang="ts">
  import { localMode } from '$lib/db/local-mode.svelte';
  import { page } from '$app/state';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import EmptyState from '../ui/EmptyState.svelte';

  const challengeMetricOptions = [
    { value: 'steps', label: 'Schritte (Steps)' },
    { value: 'workouts', label: 'Workouts & Kraftsport' },
    { value: 'sleep', label: 'Schlafdauer & Erholung' },
    { value: 'water', label: 'Wasserhaushalt (Hydration)' },
    { value: 'fasting', label: 'Intervallfasten' }
  ];

  const challengeTimeframeOptions = [
    { value: 'weekly', label: 'Rolling 7 Tage (Wöchentlich)' },
    { value: 'monthly', label: 'Rolling 30 Tage (Monatlich)' }
  ];

  export type CommunityTab = 'leaderboard' | 'connections' | 'feed';

  let { initialTab = 'leaderboard' } = $props<{
    initialTab?: CommunityTab;
  }>();

  let activeTab = $derived<CommunityTab>(
    page.url.pathname.includes('/community/connections')
      ? 'connections'
      : page.url.pathname.includes('/community/feed')
        ? 'feed'
        : page.url.pathname.includes('/community/leaderboard')
          ? 'leaderboard'
          : initialTab
  );

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
    members: Array<{
      rank: number;
      name: string;
      handle: string;
      instance: string;
      score: string;
      isYou?: boolean;
    }>;
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
        {
          rank: 1,
          name: 'Dr. med. Longevity',
          handle: '@longevity_doc',
          instance: 'charite.de',
          score: '82.450 Schritte'
        },
        {
          rank: 2,
          name: 'Philipp (Du)',
          handle: '@philipp',
          instance: 'salus.local',
          score: '74.280 Schritte',
          isYou: true
        },
        {
          rank: 3,
          name: 'Sarah Biohacker',
          handle: '@sarah_bio',
          instance: 'zurich.health',
          score: '69.100 Schritte'
        },
        {
          rank: 4,
          name: 'Marc Physio',
          handle: '@marc_fit',
          instance: 'tum.de',
          score: '61.400 Schritte'
        }
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
        {
          rank: 1,
          name: 'Philipp (Du)',
          handle: '@philipp',
          instance: 'salus.local',
          score: '480 Std (16:8)',
          isYou: true
        },
        {
          rank: 2,
          name: 'KetoScientist',
          handle: '@ketomaster',
          instance: 'stanford.edu',
          score: '462 Std'
        },
        {
          rank: 3,
          name: 'Elena Fasting',
          handle: '@elena_f',
          instance: 'berlin.bio',
          score: '420 Std'
        }
      ]
    }
  ]);

  let selectedChallenge = $state<Challenge>(challenges[0]);
  let inviteCode = $state('');
  let createName = $state('');
  let createMetric = $state('steps');
  let createTimeframe = $state('weekly');

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
      sourceDataType: createMetric as 'steps' | 'workouts' | 'sleep' | 'water' | 'fasting',
      timeFrame: createTimeframe === 'weekly' ? 'Rolling 7 Tage' : 'Rolling 30 Tage',
      participants: 1,
      userRank: 1,
      userScore: '0',
      unit: createMetric === 'steps' ? 'Schritte' : 'Std',
      isCreator: true,
      members: [
        {
          rank: 1,
          name: 'Philipp (Du)',
          handle: '@philipp',
          instance: 'salus.local',
          score: '0',
          isYou: true
        }
      ]
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
      sharedMetrics: [{ name: 'Aktivität & Tonnage', level: 'Aggregiert', direction: 'out' }],
      lastSync: 'vor 2 Stunden'
    },
    {
      id: 'p3',
      handle: '@marc_fit',
      displayName: 'Marc Physio',
      instance: 'tum.de',
      status: 'pending',
      isRemote: true,
      sharedMetrics: [{ name: 'Workouts & 1RM', level: 'Anfrage ausstehend', direction: 'in' }],
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
  interface FeedItem {
    id: string;
    user: string;
    handle: string;
    action: string;
    metric: string;
    time: string;
    likes: number;
  }

  let feedItems = $state<FeedItem[]>([
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
  ]);
</script>

<div class="space-y-6">
  <!-- Page Header -->
  <div>
    <h1 class="text-2xl font-extrabold tracking-tight">Community &amp; Föderation</h1>
    <p class="mt-0.5 text-sm text-[var(--text-muted)]">
      Datenschutzkonforme Peer-Freigaben, dezentrale Gruppen-Challenges und Aktivitätsfeed via
      ActivityPub
    </p>
  </div>

  {#if localMode.active}
    <!-- Dedicated Local / Offline Mode Empty State -->
    <div
      class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-8 shadow-[var(--shadow-card)]"
    >
      <EmptyState
        icon="cloud-off"
        title="Community im lokalen Modus nicht verfügbar"
        description="Dezentrale Challenges, der Aktivitätsfeed und Peer-to-Peer Freigaben erfordern ein verbundenes Server-Konto."
      >
        <Btn variant="primary" size="md" href="/auth/login">Server verbinden / Anmelden</Btn>
      </EmptyState>
    </div>
  {:else}
    <!-- Primary Sub-Navigation Tabs (Only when server mode) -->
    <div
      class="flex gap-2 overflow-x-auto rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-1.5"
    >
      <a
        href="/community/leaderboard"
        class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
        'leaderboard'
          ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
          : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      >
        <Icon name="wb-sunny" class="text-[var(--color-circadian)]" />
        <span>Challenges &amp; Ranglisten</span>
      </a>

      <a
        href="/community/connections"
        class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
        'connections'
          ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
          : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      >
        <Icon name="groups" class="text-[var(--color-primary)]" />
        <span>Freunde &amp; Verbindungen</span>
      </a>

      <a
        href="/community/feed"
        class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
        'feed'
          ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
          : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      >
        <Icon name="insights" class="text-[var(--color-activity)]" />
        <span>Aktivitätsfeed</span>
      </a>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- TAB 1: CHALLENGES & LEADERBOARDS                           -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if activeTab === 'leaderboard'}
      <div class="grid grid-cols-1 gap-5 lg:grid-cols-12">
        <!-- Left: Active Challenge List & Detail (8-Col) -->
        <div class="space-y-4 lg:col-span-8">
          <!-- Challenge Selector Cards -->
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {#each challenges as c}
              <button
                type="button"
                onclick={() => (selectedChallenge = c)}
                class="cursor-pointer rounded-2xl border bg-[var(--bg-surface-0)] p-4 text-left shadow-[var(--shadow-card)] transition-all {selectedChallenge.id ===
                c.id
                  ? 'border-[var(--color-primary)] ring-2 ring-[var(--color-primary)]/20'
                  : 'border-[var(--border-subtle)] hover:border-[var(--border-strong)]'}"
              >
                <div class="mb-1 flex items-center justify-between">
                  <span class="text-xs font-bold text-[var(--text-main)]">{c.name}</span>
                  <Badge variant="default" class="text-[0.625rem]">{c.timeFrame}</Badge>
                </div>
                <p class="text-[0.6875rem] text-[var(--text-muted)]">
                  {c.participants} Teilnehmer • {c.sourceDataType}
                </p>

                <div
                  class="mt-3 flex items-center justify-between border-t border-[var(--border-subtle)] pt-2 text-xs"
                >
                  <span
                    >Dein Rang: <strong class="font-bold text-[var(--color-primary)]"
                      >#{c.userRank}</strong
                    ></span
                  >
                  <span
                    >Score: <strong class="font-semibold text-[var(--text-main)]"
                      >{c.userScore} {c.unit}</strong
                    ></span
                  >
                </div>
              </button>
            {/each}
          </div>

          <!-- Selected Challenge Leaderboard Table -->
          <div
            class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
          >
            <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
              <div>
                <div class="flex items-center gap-2">
                  <h2 class="text-base font-extrabold text-[var(--text-main)]">
                    {selectedChallenge.name}
                  </h2>
                  <Badge variant="success">Aktiv</Badge>
                </div>
                <p class="mt-0.5 text-xs text-[var(--text-muted)]">
                  {selectedChallenge.timeFrame} • Einladungscode:
                  <span
                    class="rounded-md border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-1.5 py-0.5 font-semibold text-[var(--color-primary)]"
                    >SALUS-{selectedChallenge.id.toUpperCase()}-2026</span
                  >
                </p>
              </div>
              <Btn
                variant="secondary"
                size="sm"
                onclick={() => alert('Einladungslink in Zwischenablage kopiert!')}
              >
                Teilnehmer einladen
              </Btn>
            </div>

            <!-- Members Podium List -->
            <div class="space-y-2.5">
              {#each selectedChallenge.members as m}
                <div
                  class="flex items-center justify-between rounded-xl border p-3.5 transition-all {m.isYou
                    ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)]/20 shadow-xs'
                    : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)]'}"
                >
                  <div class="flex items-center gap-3">
                    <span
                      class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-black {m.rank ===
                      1
                        ? 'bg-amber-400 text-black shadow-xs'
                        : m.rank === 2
                          ? 'bg-slate-300 text-black'
                          : m.rank === 3
                            ? 'bg-amber-700 text-white'
                            : 'bg-[var(--bg-surface-100)] font-bold text-[var(--text-muted)]'}"
                    >
                      {m.rank === 1 ? '1' : m.rank === 2 ? '2' : m.rank === 3 ? '3' : `#${m.rank}`}
                    </span>
                    <div>
                      <div class="flex items-center gap-2">
                        <span class="text-xs font-bold text-[var(--text-main)]">{m.name}</span>
                        {#if m.isYou}
                          <Badge variant="primary" class="text-[0.5625rem]">Du</Badge>
                        {/if}
                      </div>
                      <span class="text-[0.6875rem] text-[var(--text-soft)]"
                        >{m.handle}@{m.instance}</span
                      >
                    </div>
                  </div>

                  <div class="text-sm font-extrabold text-[var(--text-main)]">
                    {m.score}
                  </div>
                </div>
              {/each}
            </div>
          </div>
        </div>

        <!-- Right: Join Code & Create Challenge Forms (4-Col) -->
        <div class="space-y-4 lg:col-span-4">
          <!-- Join via Code Card -->
          <div
            class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
          >
            <div class="mb-2 flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
              <Icon name="wb-sunny" class="text-[var(--color-primary)]" />
              <span>Challenge beitreten</span>
            </div>
            <p class="mb-3 text-xs text-[var(--text-muted)]">
              Gib den 8-stelligen Einladungscode eines Freundes ein:
            </p>
            <div class="space-y-3">
              <Input placeholder="z. B. SALUS-C1-2026..." bind:value={inviteCode} />
              <Btn variant="primary" size="sm" class="w-full" onclick={handleJoinCode}>
                Mit Code beitreten
              </Btn>
            </div>
          </div>

          <!-- Create Challenge Card -->
          <div
            class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
          >
            <div class="mb-2 flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
              <Icon name="add" class="text-[var(--color-activity)]" />
              <span>Neue Challenge erstellen</span>
            </div>
            <div class="space-y-3">
              <Input
                label="Name der Challenge"
                placeholder="z. B. Herbst Step-Cup..."
                bind:value={createName}
              />
              <Select
                label="Metrik-Typ"
                bind:value={createMetric}
                options={challengeMetricOptions}
              />
              <Select
                label="Zeitraum"
                bind:value={createTimeframe}
                options={challengeTimeframeOptions}
              />
              <Btn variant="primary" size="sm" class="w-full" onclick={handleCreateChallenge}>
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
        <div
          class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
        >
          <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
            <div>
              <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
                <Icon name="groups" class="text-[var(--color-primary)]" />
                <span>Neuen Peer einladen (P2P Data Sharing)</span>
              </div>
              <p class="mt-0.5 text-xs text-[var(--text-muted)]">
                Gib das Handle deines Freundes oder Arztes ein (z. B. <span
                  class="font-medium text-[var(--text-main)]">@name</span
                >
                oder föderiert
                <span class="font-medium text-[var(--text-main)]">@name@klinik.de</span>)
              </p>
            </div>
          </div>

          <div class="flex max-w-lg items-end gap-2">
            <div class="flex-1">
              <Input
                placeholder="@benutzername oder @dr_arzt@klinik.de..."
                bind:value={newPeerHandle}
              />
            </div>
            <Btn variant="primary" size="md" onclick={handleInvitePeer}>Einladung senden</Btn>
          </div>
        </div>

        <!-- Active Peer Connections Grid -->
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          {#each peers as p}
            <div
              class="flex flex-col justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
            >
              <div>
                <div class="mb-2 flex items-start justify-between">
                  <div>
                    <h3 class="text-sm font-bold text-[var(--text-main)]">{p.displayName}</h3>
                    <span class="text-xs text-[var(--text-muted)]">{p.handle}@{p.instance}</span>
                  </div>
                  <Badge
                    variant={p.status === 'mutual'
                      ? 'success'
                      : p.status === 'pending'
                        ? 'vital'
                        : 'primary'}
                  >
                    {p.status === 'mutual'
                      ? 'Beidseitig'
                      : p.status === 'pending'
                        ? 'Ausstehend'
                        : 'Ausgehend'}
                  </Badge>
                </div>

                <!-- Shared Metrics Pills -->
                <div class="my-3 space-y-1.5">
                  <span
                    class="block text-[0.6875rem] font-semibold tracking-wider text-[var(--text-soft)] uppercase"
                    >Geteilte Metriken:</span
                  >
                  {#each p.sharedMetrics as m}
                    <div
                      class="flex items-center justify-between rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2 text-xs"
                    >
                      <span class="font-semibold text-[var(--text-main)]">{m.name}</span>
                      <span class="text-[0.6875rem] font-medium text-[var(--text-muted)]"
                        >{m.level}</span
                      >
                    </div>
                  {/each}
                </div>
              </div>

              <div
                class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-3 text-xs"
              >
                <span class="text-[0.6875rem] font-medium text-[var(--text-soft)]"
                  >{p.lastSync}</span
                >
                <button
                  type="button"
                  class="cursor-pointer text-xs font-semibold text-[var(--color-vital)] hover:underline"
                  onclick={() => alert('Freigabe widerrufen')}
                >
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
      <div
        class="mx-auto max-w-2xl space-y-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
      >
        <div class="flex items-center justify-between border-b border-[var(--border-subtle)] pb-3">
          <span class="text-sm font-bold">Aktivitäts-Feed deiner Verbindungen</span>
          <span class="text-xs font-medium text-[var(--text-muted)]">Live via ActivityPub</span>
        </div>

        <div class="space-y-4">
          {#each feedItems as item}
            <div
              class="space-y-2 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4"
            >
              <div class="flex items-center justify-between">
                <div>
                  <span class="text-xs font-bold text-[var(--color-primary)]">{item.user}</span>
                  <span class="ml-1 text-[0.6875rem] text-[var(--text-soft)]">{item.handle}</span>
                </div>
                <span class="text-[0.6875rem] text-[var(--text-soft)]">{item.time}</span>
              </div>
              <p class="text-xs font-semibold text-[var(--text-main)]">{item.action}</p>
              <div
                class="inline-block rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] px-2.5 py-1 text-xs font-bold text-[var(--color-success)]"
              >
                {item.metric}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</div>
