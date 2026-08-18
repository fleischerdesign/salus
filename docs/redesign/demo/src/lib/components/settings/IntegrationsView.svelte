<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  // 1. Wearable Connectors
  let connectors = $state([
    { id: 'apple', name: 'Apple HealthKit', status: 'connected', lastSync: 'Vor 15 Min', icon: 'sun', color: 'text-rose-500', desc: 'Schritte, Ruhepuls, Schlafphasen' },
    { id: 'oura', name: 'Oura Ring Gen 3', status: 'connected', lastSync: 'Heute 07:12', icon: 'sun', color: 'text-slate-400', desc: 'HRV, Bereitschaft, Körpertemperatur' },
    { id: 'withings', name: 'Withings Body Scan', status: 'connected', lastSync: 'Gestern 08:30', icon: 'labs', color: 'text-cyan-500', desc: 'Gewicht, KFA, Segmentale Muskelmasse' },
    { id: 'garmin', name: 'Garmin Connect', status: 'disconnected', lastSync: 'Nie', icon: 'dumbbell', color: 'text-blue-500', desc: 'GPS-Läufe, VO2max, Trainingslast' },
    { id: 'whoop', name: 'Whoop 4.0', status: 'disconnected', lastSync: 'Nie', icon: 'chart', color: 'text-amber-500', desc: 'Belastungs-Score, Erholungs-Score' },
    { id: 'homeassistant', name: 'Home Assistant Webhook', status: 'connected', lastSync: 'Vor 2 Min', icon: 'labs', color: 'text-sky-400', desc: 'Umgebungslicht, Raumklima, Schlaf-Trigger' }
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
    { id: 'tok-1', name: 'iOS Shortcut Sync Push', tokenPrefix: 'salus_pat_9a4f...', scope: 'write:measurements, read:metrics', createdAt: '10.06.2026', lastUsed: 'Vor 15 Min' },
    { id: 'tok-2', name: 'Home Assistant Automations', tokenPrefix: 'salus_pat_1b8c...', scope: 'read:circadian, write:measurements', createdAt: '01.07.2026', lastUsed: 'Vor 2 Min' }
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
    { metric: 'Körpergewicht', rank1: 'Withings Body Scan', rank2: 'Apple HealthKit', rank3: 'Manuelle Eingabe' },
    { metric: 'Ruheherzfrequenz & HRV', rank1: 'Oura Ring Gen 3', rank2: 'Apple HealthKit', rank3: 'Manuelle Messung' },
    { metric: 'Tägliche Schritte', rank1: 'Apple HealthKit', rank2: 'Garmin Connect', rank3: 'Manuelle Erfassung' },
    { metric: 'Schlafdauer & Phasen', rank1: 'Oura Ring Gen 3', rank2: 'Apple HealthKit', rank3: 'Manuelles Tagebuch' }
  ]);
</script>

<div class="space-y-6">
  <!-- Section 1: Wearables & Hardware -->
  <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-sm font-bold text-[var(--text-main)]">Verbundene Wearables und Sensoren</h3>
        <p class="text-xs text-[var(--text-muted)] mt-0.5">Automatische Datenerfassung über native Schnittstellen</p>
      </div>
      <Badge variant="success">3 Aktive Verbindungen</Badge>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
      {#each connectors as c}
        <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3.5 flex flex-col justify-between gap-3">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-2">
              <Icon name={c.icon} class={c.color} />
              <div>
                <h4 class="text-xs font-bold text-[var(--text-main)]">{c.name}</h4>
                <span class="text-[0.625rem] text-[var(--text-soft)]">{c.desc}</span>
              </div>
            </div>
            <Badge variant={c.status === 'connected' ? 'success' : 'default'} class="text-[0.5625rem]">
              {c.status === 'connected' ? 'Aktiv' : 'Getrennt'}
            </Badge>
          </div>

          <div class="flex items-center justify-between pt-1 text-[0.625rem] border-t border-[var(--border-subtle)]">
            <span class="text-[var(--text-soft)]">Sync: {c.lastSync}</span>
            <button
              type="button"
              onclick={() => c.status = c.status === 'connected' ? 'disconnected' : 'connected'}
              class="font-semibold text-[var(--color-primary)] hover:underline cursor-pointer"
            >
              {c.status === 'connected' ? 'Trennen' : 'Verbinden'}
            </button>
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Section 2: Multi-Source Priority Matrix (ADR Source Deduplication) -->
  <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] space-y-4">
    <div>
      <h3 class="text-sm font-bold text-[var(--text-main)]">Multi-Quellen Prioritätsmatrix</h3>
      <p class="text-xs text-[var(--text-muted)] mt-0.5">
        Definiert die Vorrang-Reihenfolge bei gleichzeitigen Messwerten mehrerer Sensoren (ADR Source Engine)
      </p>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left text-xs border-collapse">
        <thead>
          <tr class="border-b border-[var(--border-subtle)] text-[var(--text-soft)] uppercase tracking-wider text-[0.625rem]">
            <th class="py-2.5 px-3">Metrik</th>
            <th class="py-2.5 px-3">Priorität 1 (Primär)</th>
            <th class="py-2.5 px-3">Priorität 2 (Sekundär)</th>
            <th class="py-2.5 px-3">Priorität 3 (Fallback)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)]">
          {#each sourcePriorities as sp}
            <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
              <td class="py-3 px-3 font-bold text-[var(--text-main)]">{sp.metric}</td>
              <td class="py-3 px-3">
                <span class="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-500 font-bold text-[0.6875rem]">Rang 1 {sp.rank1}</span>
              </td>
              <td class="py-3 px-3">
                <span class="px-2 py-0.5 rounded-md bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)] font-semibold text-[0.6875rem]">Rang 2 {sp.rank2}</span>
              </td>
              <td class="py-3 px-3">
                <span class="px-2 py-0.5 rounded-md bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-soft)] font-medium text-[0.6875rem]">Rang 3 {sp.rank3}</span>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Section 3: Webhooks & API Tokens -->
  <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h3 class="text-sm font-bold text-[var(--text-main)]">Persönliche API-Tokens und Webhook-Endpunkte</h3>
        <p class="text-xs text-[var(--text-muted)] mt-0.5">Automatisierte Ingestion via REST API und Webhooks</p>
      </div>
    </div>

    <!-- Active Tokens Table -->
    <div class="overflow-x-auto">
      <table class="w-full text-left text-xs border-collapse">
        <thead>
          <tr class="border-b border-[var(--border-subtle)] text-[var(--text-soft)] uppercase tracking-wider text-[0.625rem]">
            <th class="py-2.5 px-3">Token-Name</th>
            <th class="py-2.5 px-3">Präfix</th>
            <th class="py-2.5 px-3">Berechtigungs-Scope</th>
            <th class="py-2.5 px-3">Zuletzt Verwendet</th>
            <th class="py-2.5 px-3 text-right">Aktion</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)]">
          {#each tokens as t}
            <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
              <td class="py-3 px-3 font-semibold text-[var(--text-main)]">{t.name}</td>
              <td class="py-3 px-3 font-semibold text-[var(--color-primary)] tabular-nums">{t.tokenPrefix}</td>
              <td class="py-3 px-3 text-[var(--text-soft)] tabular-nums">{t.scope}</td>
              <td class="py-3 px-3 text-[var(--text-muted)]">{t.lastUsed}</td>
              <td class="py-3 px-3 text-right">
                <button type="button" onclick={() => tokens = tokens.filter(tok => tok.id !== t.id)} class="text-rose-400 hover:text-rose-600 font-semibold cursor-pointer">
                  Widerrufen
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <!-- New Token Form -->
    <div class="pt-2 flex flex-col sm:flex-row items-center gap-2 border-t border-[var(--border-subtle)]">
      <input
        type="text"
        placeholder="Token-Name (z.B. Oura Automations)..."
        bind:value={newTokenName}
        class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl px-3.5 py-2 text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)] flex-1 w-full"
      />
      <select
        bind:value={newTokenScope}
        class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl px-3.5 py-2 text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)] w-full sm:w-auto"
      >
        <option value="write:measurements">write:measurements (Schreibrechte)</option>
        <option value="read:metrics">read:metrics (Nur Lesen)</option>
        <option value="admin">Full Admin (Vollzugriff)</option>
      </select>
      <Btn variant="primary" size="sm" class="w-full sm:w-auto" onclick={createToken}>
        + Token generieren
      </Btn>
    </div>
  </div>
</div>
