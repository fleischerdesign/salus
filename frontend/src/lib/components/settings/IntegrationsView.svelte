<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';

  const tokenScopeOptions = [
    { value: 'write:measurements', label: 'write:measurements (Schreibrechte)' },
    { value: 'read:metrics', label: 'read:metrics (Nur Lesen)' },
    { value: 'admin', label: 'Full Admin (Vollzugriff)' }
  ];

  // 1. Wearable Connectors
  let connectors = $state([
    {
      id: 'apple',
      name: 'Apple HealthKit',
      status: 'connected',
      lastSync: 'Vor 15 Min',
      icon: 'favorite',
      color: 'text-rose-500',
      desc: 'Schritte, Ruhepuls, Schlafphasen'
    },
    {
      id: 'oura',
      name: 'Oura Ring Gen 3',
      status: 'connected',
      lastSync: 'Heute 07:12',
      icon: 'bedtime',
      color: 'text-slate-400',
      desc: 'HRV, Bereitschaft, Körpertemperatur'
    },
    {
      id: 'withings',
      name: 'Withings Body Scan',
      status: 'connected',
      lastSync: 'Gestern 08:30',
      icon: 'monitor-heart',
      color: 'text-cyan-500',
      desc: 'Gewicht, KFA, Segmentale Muskelmasse'
    },
    {
      id: 'garmin',
      name: 'Garmin Connect',
      status: 'disconnected',
      lastSync: 'Nie',
      icon: 'fitness-center',
      color: 'text-blue-500',
      desc: 'GPS-Läufe, VO2max, Trainingslast'
    },
    {
      id: 'whoop',
      name: 'Whoop 4.0',
      status: 'disconnected',
      lastSync: 'Nie',
      icon: 'show-chart',
      color: 'text-amber-500',
      desc: 'Belastungs-Score, Erholungs-Score'
    },
    {
      id: 'homeassistant',
      name: 'Home Assistant Webhook',
      status: 'connected',
      lastSync: 'Vor 2 Min',
      icon: 'hub',
      color: 'text-sky-400',
      desc: 'Umgebungslicht, Raumklima, Schlaf-Trigger'
    }
  ]);

  // 2. Personal API Tokens
  interface ApiToken {
    id: string;
    name: string;
    tokenPrefix: string;
    scope: string;
    createdAt: string;
    lastUsed: string;
  }

  let tokens = $state<ApiToken[]>([
    {
      id: 'tok-1',
      name: 'iOS Shortcut Sync Push',
      tokenPrefix: 'salus_pat_9a4f...',
      scope: 'write:measurements, read:metrics',
      createdAt: '10.06.2026',
      lastUsed: 'Vor 15 Min'
    },
    {
      id: 'tok-2',
      name: 'Home Assistant Automations',
      tokenPrefix: 'salus_pat_1b8c...',
      scope: 'read:circadian, write:measurements',
      createdAt: '01.07.2026',
      lastUsed: 'Vor 2 Min'
    }
  ]);

  let newTokenName = $state('');
  let newTokenScope = $state('write:measurements');

  function createToken() {
    if (!newTokenName) return;
    tokens.push({
      id: `tok-${tokens.length + 1}`,
      name: newTokenName,
      tokenPrefix: `salus_pat_${Math.random().toString(36).substring(2, 6)}...`,
      scope: newTokenScope,
      createdAt: 'Heute',
      lastUsed: 'Noch nie'
    });
    newTokenName = '';
    alert('Neuer API-Token generiert. Bitte kopiere ihn sicher.');
  }

  // 3. Multi-Source Priority Matrix (user_source_preference)
  let sourcePriorities = $state([
    {
      metric: 'Körpergewicht',
      rank1: 'Withings Body Scan',
      rank2: 'Apple HealthKit',
      rank3: 'Manuelle Eingabe'
    },
    {
      metric: 'Ruheherzfrequenz & HRV',
      rank1: 'Oura Ring Gen 3',
      rank2: 'Apple HealthKit',
      rank3: 'Manuelle Messung'
    },
    {
      metric: 'Tägliche Schritte',
      rank1: 'Apple HealthKit',
      rank2: 'Garmin Connect',
      rank3: 'Manuelle Erfassung'
    },
    {
      metric: 'Schlafdauer & Phasen',
      rank1: 'Oura Ring Gen 3',
      rank2: 'Apple HealthKit',
      rank3: 'Manuelles Tagebuch'
    }
  ]);
</script>

<div class="space-y-6">
  <!-- Section 1: Wearables & Hardware -->
  <div
    class="space-y-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
  >
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-sm font-bold text-[var(--text-main)]">Verbundene Wearables und Sensoren</h3>
        <p class="mt-0.5 text-xs text-[var(--text-muted)]">
          Automatische Datenerfassung über native Schnittstellen
        </p>
      </div>
      <Badge variant="success">3 Aktive Verbindungen</Badge>
    </div>

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3">
      {#each connectors as c}
        <div
          class="flex flex-col justify-between gap-3 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-2">
              <Icon name={c.icon} class={c.color} />
              <div>
                <h4 class="text-xs font-bold text-[var(--text-main)]">{c.name}</h4>
                <span class="text-[0.625rem] text-[var(--text-soft)]">{c.desc}</span>
              </div>
            </div>
            <Badge
              variant={c.status === 'connected' ? 'success' : 'default'}
              class="text-[0.5625rem]"
            >
              {c.status === 'connected' ? 'Aktiv' : 'Getrennt'}
            </Badge>
          </div>

          <div
            class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-1 text-[0.625rem]"
          >
            <span class="text-[var(--text-soft)]">Sync: {c.lastSync}</span>
            <button
              type="button"
              onclick={() => (c.status = c.status === 'connected' ? 'disconnected' : 'connected')}
              class="cursor-pointer font-semibold text-[var(--color-primary)] hover:underline"
            >
              {c.status === 'connected' ? 'Trennen' : 'Verbinden'}
            </button>
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Section 2: Multi-Source Priority Matrix (ADR Source Deduplication) -->
  <div
    class="space-y-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
  >
    <div>
      <h3 class="text-sm font-bold text-[var(--text-main)]">Multi-Quellen Prioritätsmatrix</h3>
      <p class="mt-0.5 text-xs text-[var(--text-muted)]">
        Definiert die Vorrang-Reihenfolge bei gleichzeitigen Messwerten mehrerer Sensoren (ADR
        Source Engine)
      </p>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full border-collapse text-left text-xs">
        <thead>
          <tr
            class="border-b border-[var(--border-subtle)] text-[0.625rem] tracking-wider text-[var(--text-soft)] uppercase"
          >
            <th class="px-3 py-2.5">Metrik</th>
            <th class="px-3 py-2.5">Priorität 1 (Primär)</th>
            <th class="px-3 py-2.5">Priorität 2 (Sekundär)</th>
            <th class="px-3 py-2.5">Priorität 3 (Fallback)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)]">
          {#each sourcePriorities as sp}
            <tr class="transition-colors hover:bg-[var(--bg-surface-50)]">
              <td class="px-3 py-3 font-bold text-[var(--text-main)]">{sp.metric}</td>
              <td class="px-3 py-3">
                <span
                  class="rounded-md bg-emerald-500/10 px-2 py-0.5 text-[0.6875rem] font-bold text-emerald-500"
                  >Rang 1 {sp.rank1}</span
                >
              </td>
              <td class="px-3 py-3">
                <span
                  class="rounded-md border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2 py-0.5 text-[0.6875rem] font-semibold text-[var(--text-muted)]"
                  >Rang 2 {sp.rank2}</span
                >
              </td>
              <td class="px-3 py-3">
                <span
                  class="rounded-md border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2 py-0.5 text-[0.6875rem] font-medium text-[var(--text-soft)]"
                  >Rang 3 {sp.rank3}</span
                >
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Section 3: Webhooks & API Tokens -->
  <div
    class="space-y-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
  >
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h3 class="text-sm font-bold text-[var(--text-main)]">
          Persönliche API-Tokens und Webhook-Endpunkte
        </h3>
        <p class="mt-0.5 text-xs text-[var(--text-muted)]">
          Automatisierte Ingestion via REST API und Webhooks
        </p>
      </div>
    </div>

    <!-- Active Tokens Table -->
    <div class="overflow-x-auto">
      <table class="w-full border-collapse text-left text-xs">
        <thead>
          <tr
            class="border-b border-[var(--border-subtle)] text-[0.625rem] tracking-wider text-[var(--text-soft)] uppercase"
          >
            <th class="px-3 py-2.5">Token-Name</th>
            <th class="px-3 py-2.5">Präfix</th>
            <th class="px-3 py-2.5">Berechtigungs-Scope</th>
            <th class="px-3 py-2.5">Zuletzt Verwendet</th>
            <th class="px-3 py-2.5 text-right">Aktion</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)]">
          {#each tokens as t}
            <tr class="transition-colors hover:bg-[var(--bg-surface-50)]">
              <td class="px-3 py-3 font-semibold text-[var(--text-main)]">{t.name}</td>
              <td class="px-3 py-3 font-semibold text-[var(--color-primary)] tabular-nums"
                >{t.tokenPrefix}</td
              >
              <td class="px-3 py-3 text-[var(--text-soft)] tabular-nums">{t.scope}</td>
              <td class="px-3 py-3 text-[var(--text-muted)]">{t.lastUsed}</td>
              <td class="px-3 py-3 text-right">
                <button
                  type="button"
                  onclick={() => (tokens = tokens.filter((tok) => tok.id !== t.id))}
                  class="cursor-pointer font-semibold text-rose-400 hover:text-rose-600"
                >
                  Widerrufen
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <!-- New Token Form -->
    <div
      class="flex flex-col items-center gap-2 border-t border-[var(--border-subtle)] pt-2 sm:flex-row"
    >
      <div class="w-full flex-1">
        <Input placeholder="Token-Name (z.B. Oura Automations)..." bind:value={newTokenName} />
      </div>
      <div class="w-full sm:w-64">
        <Select bind:value={newTokenScope} options={tokenScopeOptions} />
      </div>
      <Btn variant="primary" size="md" class="h-10 w-full shrink-0 sm:w-auto" onclick={createToken}>
        + Token generieren
      </Btn>
    </div>
  </div>
</div>
