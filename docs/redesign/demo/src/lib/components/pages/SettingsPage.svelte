<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import TextInput from '../ui/TextInput.svelte';
  import SelectDropdown from '../ui/SelectDropdown.svelte';
  import ToggleSwitch from '../ui/ToggleSwitch.svelte';
  import IntegrationsView from '../settings/IntegrationsView.svelte';

  export type SettingsTab =
    | 'account'
    | 'appearance'
    | 'sources'
    | 'privacy'
    | 'shares'
    | 'data-quality'
    | 'backup';

  let { initialTab = 'account' } = $props<{
    initialTab?: SettingsTab;
  }>();

  let activeTab = $state<SettingsTab>('account');

  $effect(() => {
    activeTab = initialTab;
  });

  // ─── 1. ACCOUNT & PROFILE STATE ───
  let displayName = $state('Philipp Fleischer');
  let username = $state('philipp');
  let heightCm = $state(184);
  let selectedLocale = $state('de');
  let selectedTimezone = $state('Europe/Berlin');

  const localeOptions = [
    { value: 'de', label: 'Deutsch (DE)' },
    { value: 'en', label: 'English (US)' },
    { value: 'fr', label: 'Français' }
  ];

  const timezoneOptions = [
    { value: 'Europe/Berlin', label: 'Europe/Berlin (Mitteleuropäische Zeit)' },
    { value: 'Europe/Zurich', label: 'Europe/Zurich (Schweiz)' },
    { value: 'Europe/Vienna', label: 'Europe/Vienna (Österreich)' },
    { value: 'America/New_York', label: 'America/New_York (US Ostküste)' },
    { value: 'UTC', label: 'UTC (Koordiniert)' }
  ];

  let currentPassword = $state('');
  let newPassword = $state('');
  let confirmPassword = $state('');

  let oidcProviders = $state([
    { id: 'google', name: 'Google Workspace SSO', connected: true, email: 'philipp.fleischer@gmail.com' },
    { id: 'github', name: 'GitHub OAuth', connected: true, email: 'github.com/philipp' },
    { id: 'oidc_corp', name: 'Klinik / OIDC Enterprise', connected: false, email: '' }
  ]);

  // ─── 2. APPEARANCE & APP STATE ───
  let themeMode = $state<'light' | 'dark' | 'system'>('system');
  let selectedColorblindMode = $state('none');
  let toastPosition = $state('bottom-right');

  const colorblindOptions = [
    { value: 'none', label: 'Standard (Dezenter wissenschaftlicher Kontrast)' },
    { value: 'protanopia', label: 'Protanopie (Rotsehschwäche-Optimierung)' },
    { value: 'deuteranopia', label: 'Deuteranopie (Grünsehschwäche-Optimierung)' },
    { value: 'tritanopia', label: 'Tritanopie (Blausehschwäche-Optimierung)' }
  ];

  const toastOptions = [
    { value: 'bottom-right', label: 'Unten Rechts (Standard)' },
    { value: 'top-right', label: 'Oben Rechts' },
    { value: 'bottom-center', label: 'Unten Mitte' }
  ];

  let offDirectEnabled = $state(true);
  let offApiKey = $state('salus_usr_off_9981');
  let isCheckingUpdate = $state(false);
  let updateStatus = $state<{ checked: boolean; version: string; isLatest: boolean }>({
    checked: true,
    version: 'v2.4.0 • Salus Core ist auf dem neuesten Stand',
    isLatest: true
  });

  function checkUpdates() {
    isCheckingUpdate = true;
    setTimeout(() => {
      isCheckingUpdate = false;
      updateStatus = { checked: true, version: 'v2.4.0 • Salus Core ist auf dem neuesten Stand' };
    }, 800);
  }

  // ─── 4. PRIVACY & E2EE STATE ───
  let e2eePublicKey = $state('04c3a89e1b2f778d91a24bc098e721a95e4d2a1b9c8e7f6a5b4c3d2e1f0a9b8c7');
  let e2eeKeyFingerprint = $state('SHA256:7f8a9b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a');
  let federatedSearchable = $state(true);
  let anonymousOpenScience = $state(true);
  let auditLoggingEnabled = $state(true);

  // ─── 5. SHARES & MEDICAL ACCESS STATE ───
  interface ActiveShare {
    id: string;
    recipientName: string;
    role: string;
    scope: string;
    expiresAt: string;
    status: 'active' | 'expired';
    accessCount: number;
  }

  let activeShares = $state<ActiveShare[]>([
    {
      id: 'sh-1',
      recipientName: 'Dr. med. Christian Weber (Kardiologie Charité)',
      role: 'Facharzt',
      scope: 'EKG, Blutdruck, ESC 2024 Profile, Laborwerte',
      expiresAt: '24.12.2026',
      status: 'active',
      accessCount: 14
    },
    {
      id: 'sh-2',
      recipientName: 'Praxis Dr. med. Elisabeth Roth (Präventivmedizin)',
      role: 'Hausärztin',
      scope: 'Glukose CGM, Stoffwechsel, BIA Körperanalyse',
      expiresAt: '15.10.2026',
      status: 'active',
      accessCount: 8
    },
    {
      id: 'sh-3',
      recipientName: 'LMU München (Circadian Study 2026)',
      role: 'Open Science Forschung',
      scope: 'Anonymisierte Schlafhypnogramme und HRV',
      expiresAt: '01.06.2026',
      status: 'expired',
      accessCount: 3
    }
  ]);

  function revokeShare(id: string) {
    activeShares = activeShares.filter(s => s.id !== id);
  }

  // ─── 6. DATA QUALITY & SWEEP STATE ───
  let isSweeping = $state(false);
  let lastSweepResult = $state({
    sweptAt: 'Heute 06:00 Uhr',
    checkedRecords: 3840,
    anomaliesFound: 2,
    duplicatesResolved: 5
  });

  const qualityRules = [
    { name: 'Physiologische Herzfrequenz-Grenzen', range: '30 – 240 bpm', action: 'Artefakt-Warnung' },
    { name: 'Plausibler Blutdruckbereich', range: '60/40 – 260/160 mmHg', action: 'Plausibilitäts-Check' },
    { name: 'Kontinuierliche Glukose (CGM)', range: '40 – 400 mg/dL', action: 'Hypo/Hyper-Alarm' },
    { name: 'Körpergewicht EMA Glättung', range: '±2.5 kg / 24h', action: 'Ausreißer-Dämpfung' }
  ];

  function runQualitySweep() {
    isSweeping = true;
    setTimeout(() => {
      isSweeping = false;
      lastSweepResult = {
        sweptAt: 'Gerade eben',
        checkedRecords: 3845,
        anomaliesFound: 0,
        duplicatesResolved: 0
      };
    }, 1000);
  }

  // ─── 7. BACKUP & EXPORT STATE ───
  const dexieTables = [
    { name: 'measurement', rows: 1840, size: '295 KB' },
    { name: 'workout_log_entry', rows: 840, size: '120 KB' },
    { name: 'meal_item', rows: 680, size: '115 KB' },
    { name: 'lab_result', rows: 180, size: '32 KB' },
    { name: 'outbox (Unified Sync Queue)', rows: 0, size: '0 KB', status: 'Geleert' }
  ];

  // ─── 8. ADMIN CONSOLE STATE ───
  let serverStats = $state({
    uptime: '18 Tage, 4 Stunden',
    dbEngine: 'SQLite (WAL-Mode, StaticPool)',
    dbSize: '4.8 MB',
    activeUsers: 1,
    schedulerJobs: 6,
    eventBusSubscribers: 2
  });

  const schedulerJobsList = [
    { name: 'DataQualitySweepJob', cron: '0 4 * * *', nextRun: 'Morgen 04:00', status: 'Aktiv' },
    { name: 'CircadianScoreRecalculationJob', cron: '*/30 * * * *', nextRun: 'In 12 Min', status: 'Aktiv' },
    { name: 'InsightsCoachingGenerationJob', cron: '0 6 * * 1', nextRun: 'Montag 06:00', status: 'Aktiv' },
    { name: 'SyncPushLogPruningJob', cron: '0 0 * * *', nextRun: 'Heute 24:00', status: 'Aktiv' }
  ];

  const navigationTabs: { id: SettingsTab; label: string; badge?: string }[] = [
    { id: 'account', label: 'Konto und Profil' },
    { id: 'appearance', label: 'Erscheinungsbild' },
    { id: 'sources', label: 'Sensoren und Quellen', badge: '3' },
    { id: 'privacy', label: 'Datenschutz und E2EE' },
    { id: 'shares', label: 'Arzt-Freigaben', badge: '2' },
    { id: 'data-quality', label: 'Datenqualität' },
    { id: 'backup', label: 'Datensicherung' }
  ];
</script>

<div class="space-y-6">
  
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Benutzer- und Systemeinstellungen</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Biometrisches Profil, Zero-Knowledge E2EE, Sensoren, Freigaben und Datensicherung
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Offline-fähig</Badge>
    </div>
  </div>

  <!-- Primary Sub-Navigation Tabs with Soft Mask Fades -->
  <div class="relative w-full overflow-hidden">
    <div class="flex gap-2 overflow-x-auto py-1.5 px-1 bg-[var(--bg-surface-50)] p-1.5 rounded-2xl border border-[var(--border-subtle)] no-scrollbar scroll-mask-x select-none">
      {#each navigationTabs as tab}
        <button
          type="button"
          onclick={() => activeTab = tab.id}
          class="px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer transition-all whitespace-nowrap shrink-0 {activeTab === tab.id ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        >
          <span>{tab.label}</span>
          {#if tab.badge}
            <Badge variant="default" class="text-[0.5625rem] font-bold">{tab.badge}</Badge>
          {/if}
        </button>
      {/each}
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 1: KONTO & PROFIL                                       -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'account'}
    <div class="space-y-5">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        <!-- Stammdaten & Zeitzone -->
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
          <h3 class="text-sm font-extrabold text-[var(--text-main)] flex items-center gap-2">
            <span>Biometrisches Profil und Zeitzone</span>
          </h3>

          <div class="space-y-3 text-xs">
            <TextInput
              label="Anzeigename"
              bind:value={displayName}
            />

            <div class="grid grid-cols-2 gap-3">
              <TextInput
                label="Benutzername"
                value={username}
                disabled={true}
              />
              <TextInput
                label="Körpergröße"
                type="number"
                unit="cm"
                bind:value={heightCm}
              />
            </div>

            <SelectDropdown
              label="Sprache (Locale)"
              bind:value={selectedLocale}
              options={localeOptions}
            />

            <div>
              <div class="flex justify-between items-center mb-1">
                <span class="font-bold text-[var(--text-muted)]">Zeitzone</span>
                <button type="button" onclick={() => selectedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone} class="text-[var(--color-primary)] hover:underline text-[0.6875rem] font-bold cursor-pointer">
                  Geräte-Zeitzone übernehmen
                </button>
              </div>
              <SelectDropdown
                bind:value={selectedTimezone}
                options={timezoneOptions}
              />
            </div>

            <div class="pt-1">
              <button type="button" onclick={() => alert('Profil gespeichert')} class="px-4 py-2 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs">
                Profil speichern
              </button>
            </div>
          </div>
        </div>

        <!-- Passwort & OIDC Identity Providers -->
        <div class="space-y-5">
          <!-- Passwort ändern -->
          <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
            <h3 class="text-sm font-extrabold text-[var(--text-main)]">Passwort ändern</h3>
            <div class="space-y-2.5 text-xs">
              <TextInput type="password" bind:value={currentPassword} placeholder="Aktuelles Passwort" />
              <TextInput type="password" bind:value={newPassword} placeholder="Neues sicheres Passwort" />
              <TextInput type="password" bind:value={confirmPassword} placeholder="Neues Passwort bestätigen" />
              <button type="button" onclick={() => alert('Passwort geändert')} class="px-4 py-2 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold hover:bg-[var(--bg-surface-100)] transition-all cursor-pointer">
                Passwort aktualisieren
              </button>
            </div>
          </div>

          <!-- OAuth / OIDC Identity Providers -->
          <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-3">
            <h3 class="text-sm font-extrabold text-[var(--text-main)]">Verknüpfte Identitätsanbieter (SSO)</h3>
            <div class="space-y-2 text-xs">
              {#each oidcProviders as p}
                <div class="flex items-center justify-between p-3 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)]">
                  <div>
                    <span class="font-extrabold text-[var(--text-main)] block">{p.name}</span>
                    <span class="text-[0.625rem] text-[var(--text-soft)]">{p.email || 'Nicht verknüpft'}</span>
                  </div>
                  <button
                    type="button"
                    onclick={() => p.connected = !p.connected}
                    class="text-xs font-bold cursor-pointer {p.connected ? 'text-rose-500 hover:underline' : 'text-[var(--color-primary)] hover:underline'}"
                  >
                    {p.connected ? 'Trennen' : 'Verknüpfen'}
                  </button>
                </div>
              {/each}
            </div>
          </div>
        </div>

      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 2: APPEARANCE & APP PREFERENCES                         -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'appearance'}
    <div class="space-y-5">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        <!-- Design & Farbmodi -->
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">Design und Farbpaletten</h3>

          <div class="space-y-3 text-xs">
            <div>
              <span class="block font-bold text-[var(--text-muted)] mb-1">Farbmodus</span>
              <div class="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onclick={() => themeMode = 'light'}
                  class="py-2.5 rounded-2xl border text-xs font-bold cursor-pointer transition-all {themeMode === 'light' ? 'bg-[var(--color-primary)] text-white border-transparent' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
                >
                  Hell
                </button>
                <button
                  type="button"
                  onclick={() => themeMode = 'dark'}
                  class="py-2.5 rounded-2xl border text-xs font-bold cursor-pointer transition-all {themeMode === 'dark' ? 'bg-[var(--color-primary)] text-white border-transparent' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
                >
                  Dunkel
                </button>
                <button
                  type="button"
                  onclick={() => themeMode = 'system'}
                  class="py-2.5 rounded-2xl border text-xs font-bold cursor-pointer transition-all {themeMode === 'system' ? 'bg-[var(--color-primary)] text-white border-transparent' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
                >
                  System
                </button>
              </div>
            </div>

            <SelectDropdown
              label="Barrierefreiheit (Farbenblindheit)"
              bind:value={selectedColorblindMode}
              options={colorblindOptions}
            />

            <SelectDropdown
              label="Toast-Meldungs-Position"
              bind:value={toastPosition}
              options={toastOptions}
            />
          </div>
        </div>

        <!-- OpenFoodFacts & Updates -->
        <div class="space-y-5">
          <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
            <h3 class="text-sm font-extrabold text-[var(--text-main)]">OpenFoodFacts Barcode-Schnittstelle</h3>
            <div class="space-y-3 text-xs">
              <ToggleSwitch
                label="Direkte API-Abfrage"
                description="Barcode-Scanner ruft Live-Nährwerte ab"
                bind:checked={offDirectEnabled}
              />

              <TextInput
                label="OpenFoodFacts API-Key (Optional)"
                bind:value={offApiKey}
              />
            </div>
          </div>

          <!-- App Version & Update Checker -->
          <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-3">
            <div class="flex items-center justify-between flex-wrap gap-2">
              <div>
                <h3 class="text-sm font-extrabold text-[var(--text-main)]">Salus Core Version</h3>
                <span class="text-xs text-[var(--text-muted)]">{updateStatus.version}</span>
              </div>
              <button
                type="button"
                onclick={checkUpdates}
                disabled={isCheckingUpdate}
                class="px-3.5 py-1.5 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold hover:bg-[var(--bg-surface-100)] transition-all cursor-pointer"
              >
                {isCheckingUpdate ? 'Prüfe...' : 'Auf Updates prüfen'}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 3: SENSORS & INTEGRATIONS                               -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'sources'}
    <IntegrationsView />

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 4: DATENSCHUTZ & E2EE                                   -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'privacy'}
    <div class="space-y-5">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        <!-- E2EE Cryptographic Identity -->
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-extrabold text-[var(--text-main)] flex items-center gap-2">
              <span>Asymmetrisches E2EE-Schlüsselpaar</span>
            </h3>
            <Badge variant="success">ECDH Curve25519</Badge>
          </div>
          <p class="text-xs text-[var(--text-muted)]">
            Ende-zu-Ende-Verschlüsselung nach Zero-Knowledge-Standard. Dein privater Schlüssel verlässt niemals dieses Gerät.
          </p>

          <div class="space-y-3 text-xs">
            <div>
              <span class="block font-bold text-[var(--text-muted)] mb-1">Öffentlicher Schlüssel (Public Key)</span>
              <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl break-all tabular-nums text-[var(--text-soft)] text-[0.6875rem]">
                {e2eePublicKey}
              </div>
            </div>

            <div>
              <span class="block font-bold text-[var(--text-muted)] mb-1">Schlüssel-Fingerabdruck</span>
              <span class="font-bold text-[var(--text-main)] tabular-nums">{e2eeKeyFingerprint}</span>
            </div>

            <div class="pt-1 flex gap-2">
              <button type="button" onclick={() => alert('Neues Schlüsselpaar lokal im Browser generiert.')} class="px-3.5 py-1.5 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold hover:bg-[var(--bg-surface-100)] cursor-pointer">
                Schlüsselpaar erneuern
              </button>
            </div>
          </div>
        </div>

        <!-- Privacy & Federation Switches -->
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">Föderation und Privatsphäre</h3>
          
          <div class="space-y-4 text-xs">
            <ToggleSwitch
              label="WebFinger und Föderations-Sichtbarkeit"
              description="Auffindbarkeit über philipp@salus.local im dezentralen Netzwerk"
              bind:checked={federatedSearchable}
            />

            <ToggleSwitch
              label="Anonyme Open-Science Synthese"
              description="K-Anonymisierte Kohorten-Forschung (k >= 5) zur medizinischen Prävention"
              bind:checked={anonymousOpenScience}
            />

            <ToggleSwitch
              label="Kryptografisches Audit-Log"
              description="Unveränderliche Zugriffsprotokolle für alle Datenabfragen führen"
              bind:checked={auditLoggingEnabled}
            />
          </div>
        </div>

      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 5: ARZT-FREIGABEN (SHARES)                              -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'shares'}
    <div class="space-y-5">
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <h3 class="text-base font-extrabold text-[var(--text-main)]">Aktive Arzt- und Forschungsfreigaben</h3>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">Asymmetrisch verschlüsselte Freigaben mit granularer Berechtigungssteuerung</p>
          </div>
          <button type="button" onclick={() => alert('Neue Arzt-Freigabe erstellen')} class="px-4 py-2 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs">
            + Neue Freigabe erstellen
          </button>
        </div>

        <div class="space-y-3">
          {#each activeShares as share}
            <div class="p-4 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] flex items-start justify-between gap-4 flex-wrap">
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-extrabold text-[var(--text-main)]">{share.recipientName}</span>
                  <Badge variant={share.status === 'active' ? 'success' : 'default'} class="text-[0.625rem]">
                    {share.status === 'active' ? 'Aktiv' : 'Abgelaufen'}
                  </Badge>
                </div>
                <p class="text-xs text-[var(--text-muted)]">{share.role} &bull; Gültig bis: {share.expiresAt}</p>
                <div class="p-2 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[0.6875rem] text-[var(--text-soft)]">
                  Umfang: {share.scope} &bull; {share.accessCount} Zugriffe protokolliert
                </div>
              </div>

              <button
                type="button"
                onclick={() => revokeShare(share.id)}
                class="px-3 py-1.5 rounded-xl border border-rose-500/30 text-rose-500 hover:bg-rose-500/10 text-xs font-bold cursor-pointer transition-all"
              >
                Freigabe widerrufen
              </button>
            </div>
          {/each}
        </div>
      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 6: DATENQUALITÄT & SWEEP                                -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'data-quality'}
    <div class="space-y-5">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        <!-- Data Quality Sweeper -->
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-extrabold text-[var(--text-main)]">Automatischer Daten-Plausibilitäts-Sweep</h3>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Erkennt Messfehler, Sensor-Artefakte und unplausible Spikes</p>
            </div>
            <button
              type="button"
              onclick={runQualitySweep}
              disabled={isSweeping}
              class="px-3.5 py-1.5 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs"
            >
              {isSweeping ? 'Prüfe...' : 'Jetzt prüfen'}
            </button>
          </div>

          <div class="grid grid-cols-3 gap-2 text-center text-xs">
            <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
              <span class="text-[0.625rem] text-[var(--text-muted)] block">Geprüfte Werte</span>
              <span class="font-extrabold text-sm text-[var(--text-main)] tabular-nums">{lastSweepResult.checkedRecords}</span>
            </div>
            <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
              <span class="text-[0.625rem] text-[var(--text-muted)] block">Anomalien</span>
              <span class="font-extrabold text-sm text-emerald-500 tabular-nums">{lastSweepResult.anomaliesFound}</span>
            </div>
            <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
              <span class="text-[0.625rem] text-[var(--text-muted)] block">Bereinigte Duplikate</span>
              <span class="font-extrabold text-sm text-[var(--color-primary)] tabular-nums">{lastSweepResult.duplicatesResolved}</span>
            </div>
          </div>
        </div>

        <!-- Validation Rules Matrix -->
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-3">
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">Physiologische Validierungsregeln</h3>
          <div class="space-y-2 text-xs">
            {#each qualityRules as rule}
              <div class="p-2.5 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] flex items-center justify-between">
                <div>
                  <span class="font-bold text-[var(--text-main)] block">{rule.name}</span>
                  <span class="text-[0.625rem] text-[var(--text-muted)]">Bereich: {rule.range}</span>
                </div>
                <Badge variant="default" class="text-[0.5625rem]">{rule.action}</Badge>
              </div>
            {/each}
          </div>
        </div>

      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 7: BACKUP & DATENSICHERUNG                              -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'backup'}
    <div class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-3">
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">Vollständiger Datenbank-Export</h3>
          <p class="text-xs text-[var(--text-muted)]">
            Exportiere alle deine biometrischen Daten, Workouts, Labore und Mahlzeiten als verschlüsseltes JSON-Archiv oder tabellarische CSV.
          </p>
          <div class="flex gap-2 flex-wrap pt-2">
            <button type="button" onclick={() => alert('JSON Export')} class="px-4 py-2 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs">
               JSON-Komplettarchiv exportieren
            </button>
            <button type="button" onclick={() => alert('CSV Export')} class="px-4 py-2 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold hover:bg-[var(--bg-surface-100)] transition-all cursor-pointer">
               CSV Messwerte exportieren
            </button>
          </div>
        </div>

        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-3">
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">Backup wiederherstellen</h3>
          <p class="text-xs text-[var(--text-muted)]">
            Importiere ein zuvor exportiertes Salus JSON-Backup. Vorhandene Daten werden mit der Server-Datenbank zusammengeführt.
          </p>
          <div class="pt-2">
            <button type="button" onclick={() => alert('JSON Import')} class="px-4 py-2 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold hover:bg-[var(--bg-surface-100)] transition-all cursor-pointer">
               JSON-Backup importieren
            </button>
          </div>
        </div>
      </div>

      <!-- IndexedDB Stats -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-sm font-extrabold text-[var(--text-main)]">Lokaler Speicher- und Synchronisationsstatus</h2>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">Vollständige verschlüsselte Offline-Verfügbarkeit aller deiner Gesundheitsdaten</p>
          </div>
          <Badge variant="success">Synchronisiert</Badge>
        </div>

        <div class="w-full overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.625rem]">
                <th class="py-2.5 px-3">Tabelle</th>
                <th class="py-2.5 px-3">Datensätze</th>
                <th class="py-2.5 px-3">Speichergröße</th>
                <th class="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)]">
              {#each dexieTables as t}
                <tr>
                  <td class="py-2.5 px-3 font-bold text-[var(--text-main)]">{t.name}</td>
                  <td class="py-2.5 px-3 text-[var(--color-primary)] font-bold tabular-nums">{t.rows}</td>
                  <td class="py-2.5 px-3 text-[var(--text-muted)] tabular-nums">{t.size}</td>
                  <td class="py-2.5 px-3 text-right">
                    <Badge variant="default" class="text-[0.5625rem]">{t.status || 'Lokal gecacht'}</Badge>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  {/if}

</div>

