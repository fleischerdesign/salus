<script lang="ts">
  import { page } from '$app/state';
  import Badge from '../ui/Badge.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import Toggle from '../ui/Toggle.svelte';
  import IntegrationsView from '../settings/IntegrationsView.svelte';

  export type SettingsTab =
    'account' | 'appearance' | 'sources' | 'privacy' | 'shares' | 'data-quality' | 'backup';

  let { initialTab = 'account' } = $props<{
    initialTab?: SettingsTab;
  }>();

  let activeTab = $derived<SettingsTab>(
    page.url.pathname.includes('/settings/app')
      ? 'appearance'
      : page.url.pathname.includes('/settings/sources')
        ? 'sources'
        : page.url.pathname.includes('/settings/privacy')
          ? 'privacy'
          : page.url.pathname.includes('/settings/shares')
            ? 'shares'
            : page.url.pathname.includes('/settings/data-quality')
              ? 'data-quality'
              : page.url.pathname.includes('/settings/backup')
                ? 'backup'
                : initialTab
  );

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
    {
      id: 'google',
      name: 'Google Workspace SSO',
      connected: true,
      email: 'philipp.fleischer@gmail.com'
    },
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
      updateStatus = {
        checked: true,
        version: 'v2.4.0 • Salus Core ist auf dem neuesten Stand',
        isLatest: true
      };
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
    activeShares = activeShares.filter((s) => s.id !== id);
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
    {
      name: 'Physiologische Herzfrequenz-Grenzen',
      range: '30 – 240 bpm',
      action: 'Artefakt-Warnung'
    },
    {
      name: 'Plausibler Blutdruckbereich',
      range: '60/40 – 260/160 mmHg',
      action: 'Plausibilitäts-Check'
    },
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

  const navigationTabs: { id: SettingsTab; label: string; path: string; badge?: string }[] = [
    { id: 'account', label: 'Konto und Profil', path: '/settings/account' },
    { id: 'appearance', label: 'Erscheinungsbild', path: '/settings/app' },
    { id: 'sources', label: 'Sensoren und Quellen', path: '/settings/sources', badge: '3' },
    { id: 'privacy', label: 'Datenschutz und E2EE', path: '/settings/privacy' },
    { id: 'shares', label: 'Arzt-Freigaben', path: '/settings/shares', badge: '2' },
    { id: 'data-quality', label: 'Datenqualität', path: '/settings/data-quality' },
    { id: 'backup', label: 'Datensicherung', path: '/settings/backup' }
  ];
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Benutzer- und Systemeinstellungen</h1>
      <p class="mt-0.5 text-sm text-[var(--text-muted)]">
        Biometrisches Profil, Zero-Knowledge E2EE, Sensoren, Freigaben und Datensicherung
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Offline-fähig</Badge>
    </div>
  </div>

  <!-- Primary Sub-Navigation Tabs with Soft Mask Fades -->
  <div class="relative w-full overflow-hidden">
    <div
      class="no-scrollbar scroll-mask-x flex gap-2 overflow-x-auto rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-1.5 px-1 py-1.5 select-none"
    >
      {#each navigationTabs as tab}
        <a
          href={tab.path}
          class="flex shrink-0 cursor-pointer items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
          tab.id
            ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
            : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        >
          <span>{tab.label}</span>
          {#if tab.badge}
            <Badge variant="default" class="text-[0.5625rem] font-bold">{tab.badge}</Badge>
          {/if}
        </a>
      {/each}
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 1: KONTO & PROFIL                                       -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'account'}
    <div class="space-y-5">
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <!-- Stammdaten & Zeitzone -->
        <div
          class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
        >
          <h3 class="flex items-center gap-2 text-sm font-extrabold text-[var(--text-main)]">
            <span>Biometrisches Profil und Zeitzone</span>
          </h3>

          <div class="space-y-3 text-xs">
            <Input label="Anzeigename" bind:value={displayName} />

            <div class="grid grid-cols-2 gap-3">
              <Input label="Benutzername" value={username} disabled={true} />
              <Input label="Körpergröße" type="number" unit="cm" bind:value={heightCm} />
            </div>

            <Select label="Sprache (Locale)" bind:value={selectedLocale} options={localeOptions} />

            <div>
              <div class="mb-1 flex items-center justify-between">
                <span class="font-bold text-[var(--text-muted)]">Zeitzone</span>
                <button
                  type="button"
                  onclick={() =>
                    (selectedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone)}
                  class="cursor-pointer text-[0.6875rem] font-bold text-[var(--color-primary)] hover:underline"
                >
                  Geräte-Zeitzone übernehmen
                </button>
              </div>
              <Select bind:value={selectedTimezone} options={timezoneOptions} />
            </div>

            <div class="pt-1">
              <button
                type="button"
                onclick={() => alert('Profil gespeichert')}
                class="cursor-pointer rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
              >
                Profil speichern
              </button>
            </div>
          </div>
        </div>

        <!-- Passwort & OIDC Identity Providers -->
        <div class="space-y-5">
          <!-- Passwort ändern -->
          <div
            class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
          >
            <h3 class="text-sm font-extrabold text-[var(--text-main)]">Passwort ändern</h3>
            <div class="space-y-2.5 text-xs">
              <Input
                type="password"
                bind:value={currentPassword}
                placeholder="Aktuelles Passwort"
              />
              <Input
                type="password"
                bind:value={newPassword}
                placeholder="Neues sicheres Passwort"
              />
              <Input
                type="password"
                bind:value={confirmPassword}
                placeholder="Neues Passwort bestätigen"
              />
              <button
                type="button"
                onclick={() => alert('Passwort geändert')}
                class="cursor-pointer rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-4 py-2 text-xs font-bold transition-all hover:bg-[var(--bg-surface-100)]"
              >
                Passwort aktualisieren
              </button>
            </div>
          </div>

          <!-- OAuth / OIDC Identity Providers -->
          <div
            class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
          >
            <h3 class="text-sm font-extrabold text-[var(--text-main)]">
              Verknüpfte Identitätsanbieter (SSO)
            </h3>
            <div class="space-y-2 text-xs">
              {#each oidcProviders as p}
                <div
                  class="flex items-center justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3"
                >
                  <div>
                    <span class="block font-extrabold text-[var(--text-main)]">{p.name}</span>
                    <span class="text-[0.625rem] text-[var(--text-soft)]"
                      >{p.email || 'Nicht verknüpft'}</span
                    >
                  </div>
                  <button
                    type="button"
                    onclick={() => (p.connected = !p.connected)}
                    class="cursor-pointer text-xs font-bold {p.connected
                      ? 'text-rose-500 hover:underline'
                      : 'text-[var(--color-primary)] hover:underline'}"
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
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <!-- Design & Farbmodi -->
        <div
          class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
        >
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">Design und Farbpaletten</h3>

          <div class="space-y-3 text-xs">
            <div>
              <span class="mb-1 block font-bold text-[var(--text-muted)]">Farbmodus</span>
              <div class="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onclick={() => (themeMode = 'light')}
                  class="cursor-pointer rounded-2xl border py-2.5 text-xs font-bold transition-all {themeMode ===
                  'light'
                    ? 'border-transparent bg-[var(--color-primary)] text-white'
                    : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)]'}"
                >
                  Hell
                </button>
                <button
                  type="button"
                  onclick={() => (themeMode = 'dark')}
                  class="cursor-pointer rounded-2xl border py-2.5 text-xs font-bold transition-all {themeMode ===
                  'dark'
                    ? 'border-transparent bg-[var(--color-primary)] text-white'
                    : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)]'}"
                >
                  Dunkel
                </button>
                <button
                  type="button"
                  onclick={() => (themeMode = 'system')}
                  class="cursor-pointer rounded-2xl border py-2.5 text-xs font-bold transition-all {themeMode ===
                  'system'
                    ? 'border-transparent bg-[var(--color-primary)] text-white'
                    : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)]'}"
                >
                  System
                </button>
              </div>
            </div>

            <Select
              label="Barrierefreiheit (Farbenblindheit)"
              bind:value={selectedColorblindMode}
              options={colorblindOptions}
            />

            <Select
              label="Toast-Meldungs-Position"
              bind:value={toastPosition}
              options={toastOptions}
            />
          </div>
        </div>

        <!-- OpenFoodFacts & Updates -->
        <div class="space-y-5">
          <div
            class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
          >
            <h3 class="text-sm font-extrabold text-[var(--text-main)]">
              OpenFoodFacts Barcode-Schnittstelle
            </h3>
            <div class="space-y-3 text-xs">
              <Toggle
                label="Direkte API-Abfrage"
                description="Barcode-Scanner ruft Live-Nährwerte ab"
                bind:checked={offDirectEnabled}
              />

              <Input label="OpenFoodFacts API-Key (Optional)" bind:value={offApiKey} />
            </div>
          </div>

          <!-- App Version & Update Checker -->
          <div
            class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
          >
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h3 class="text-sm font-extrabold text-[var(--text-main)]">Salus Core Version</h3>
                <span class="text-xs text-[var(--text-muted)]">{updateStatus.version}</span>
              </div>
              <button
                type="button"
                onclick={checkUpdates}
                disabled={isCheckingUpdate}
                class="cursor-pointer rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-3.5 py-1.5 text-xs font-bold transition-all hover:bg-[var(--bg-surface-100)]"
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
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <!-- E2EE Cryptographic Identity -->
        <div
          class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
        >
          <div class="flex items-center justify-between">
            <h3 class="flex items-center gap-2 text-sm font-extrabold text-[var(--text-main)]">
              <span>Asymmetrisches E2EE-Schlüsselpaar</span>
            </h3>
            <Badge variant="success">ECDH Curve25519</Badge>
          </div>
          <p class="text-xs text-[var(--text-muted)]">
            Ende-zu-Ende-Verschlüsselung nach Zero-Knowledge-Standard. Dein privater Schlüssel
            verlässt niemals dieses Gerät.
          </p>

          <div class="space-y-3 text-xs">
            <div>
              <span class="mb-1 block font-bold text-[var(--text-muted)]"
                >Öffentlicher Schlüssel (Public Key)</span
              >
              <div
                class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-[0.6875rem] break-all text-[var(--text-soft)] tabular-nums"
              >
                {e2eePublicKey}
              </div>
            </div>

            <div>
              <span class="mb-1 block font-bold text-[var(--text-muted)]"
                >Schlüssel-Fingerabdruck</span
              >
              <span class="font-bold text-[var(--text-main)] tabular-nums"
                >{e2eeKeyFingerprint}</span
              >
            </div>

            <div class="flex gap-2 pt-1">
              <button
                type="button"
                onclick={() => alert('Neues Schlüsselpaar lokal im Browser generiert.')}
                class="cursor-pointer rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-3.5 py-1.5 text-xs font-bold hover:bg-[var(--bg-surface-100)]"
              >
                Schlüsselpaar erneuern
              </button>
            </div>
          </div>
        </div>

        <!-- Privacy & Federation Switches -->
        <div
          class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
        >
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">
            Föderation und Privatsphäre
          </h3>

          <div class="space-y-4 text-xs">
            <Toggle
              label="WebFinger und Föderations-Sichtbarkeit"
              description="Auffindbarkeit über philipp@salus.local im dezentralen Netzwerk"
              bind:checked={federatedSearchable}
            />

            <Toggle
              label="Anonyme Open-Science Synthese"
              description="K-Anonymisierte Kohorten-Forschung (k >= 5) zur medizinischen Prävention"
              bind:checked={anonymousOpenScience}
            />

            <Toggle
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
      <div
        class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
      >
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h3 class="text-base font-extrabold text-[var(--text-main)]">
              Aktive Arzt- und Forschungsfreigaben
            </h3>
            <p class="mt-0.5 text-xs text-[var(--text-muted)]">
              Asymmetrisch verschlüsselte Freigaben mit granularer Berechtigungssteuerung
            </p>
          </div>
          <button
            type="button"
            onclick={() => alert('Neue Arzt-Freigabe erstellen')}
            class="cursor-pointer rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
          >
            + Neue Freigabe erstellen
          </button>
        </div>

        <div class="space-y-3">
          {#each activeShares as share}
            <div
              class="flex flex-wrap items-start justify-between gap-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4"
            >
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-extrabold text-[var(--text-main)]"
                    >{share.recipientName}</span
                  >
                  <Badge
                    variant={share.status === 'active' ? 'success' : 'default'}
                    class="text-[0.625rem]"
                  >
                    {share.status === 'active' ? 'Aktiv' : 'Abgelaufen'}
                  </Badge>
                </div>
                <p class="text-xs text-[var(--text-muted)]">
                  {share.role} &bull; Gültig bis: {share.expiresAt}
                </p>
                <div
                  class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2 text-[0.6875rem] text-[var(--text-soft)]"
                >
                  Umfang: {share.scope} &bull; {share.accessCount} Zugriffe protokolliert
                </div>
              </div>

              <button
                type="button"
                onclick={() => revokeShare(share.id)}
                class="cursor-pointer rounded-xl border border-rose-500/30 px-3 py-1.5 text-xs font-bold text-rose-500 transition-all hover:bg-rose-500/10"
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
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <!-- Data Quality Sweeper -->
        <div
          class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
        >
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-extrabold text-[var(--text-main)]">
                Automatischer Daten-Plausibilitäts-Sweep
              </h3>
              <p class="mt-0.5 text-xs text-[var(--text-muted)]">
                Erkennt Messfehler, Sensor-Artefakte und unplausible Spikes
              </p>
            </div>
            <button
              type="button"
              onclick={runQualitySweep}
              disabled={isSweeping}
              class="cursor-pointer rounded-2xl bg-[var(--color-primary)] px-3.5 py-1.5 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
            >
              {isSweeping ? 'Prüfe...' : 'Jetzt prüfen'}
            </button>
          </div>

          <div class="grid grid-cols-3 gap-2 text-center text-xs">
            <div
              class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3"
            >
              <span class="block text-[0.625rem] text-[var(--text-muted)]">Geprüfte Werte</span>
              <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums"
                >{lastSweepResult.checkedRecords}</span
              >
            </div>
            <div
              class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3"
            >
              <span class="block text-[0.625rem] text-[var(--text-muted)]">Anomalien</span>
              <span class="text-sm font-extrabold text-emerald-500 tabular-nums"
                >{lastSweepResult.anomaliesFound}</span
              >
            </div>
            <div
              class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3"
            >
              <span class="block text-[0.625rem] text-[var(--text-muted)]"
                >Bereinigte Duplikate</span
              >
              <span class="text-sm font-extrabold text-[var(--color-primary)] tabular-nums"
                >{lastSweepResult.duplicatesResolved}</span
              >
            </div>
          </div>
        </div>

        <!-- Validation Rules Matrix -->
        <div
          class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
        >
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">
            Physiologische Validierungsregeln
          </h3>
          <div class="space-y-2 text-xs">
            {#each qualityRules as rule}
              <div
                class="flex items-center justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5"
              >
                <div>
                  <span class="block font-bold text-[var(--text-main)]">{rule.name}</span>
                  <span class="text-[0.625rem] text-[var(--text-muted)]">Bereich: {rule.range}</span
                  >
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
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <div
          class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
        >
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">
            Vollständiger Datenbank-Export
          </h3>
          <p class="text-xs text-[var(--text-muted)]">
            Exportiere alle deine biometrischen Daten, Workouts, Labore und Mahlzeiten als
            verschlüsseltes JSON-Archiv oder tabellarische CSV.
          </p>
          <div class="flex flex-wrap gap-2 pt-2">
            <button
              type="button"
              onclick={() => alert('JSON Export')}
              class="cursor-pointer rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
            >
              JSON-Komplettarchiv exportieren
            </button>
            <button
              type="button"
              onclick={() => alert('CSV Export')}
              class="cursor-pointer rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-4 py-2 text-xs font-bold transition-all hover:bg-[var(--bg-surface-100)]"
            >
              CSV Messwerte exportieren
            </button>
          </div>
        </div>

        <div
          class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
        >
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">Backup wiederherstellen</h3>
          <p class="text-xs text-[var(--text-muted)]">
            Importiere ein zuvor exportiertes Salus JSON-Backup. Vorhandene Daten werden mit der
            Server-Datenbank zusammengeführt.
          </p>
          <div class="pt-2">
            <button
              type="button"
              onclick={() => alert('JSON Import')}
              class="cursor-pointer rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-4 py-2 text-xs font-bold transition-all hover:bg-[var(--bg-surface-100)]"
            >
              JSON-Backup importieren
            </button>
          </div>
        </div>
      </div>

      <!-- IndexedDB Stats -->
      <div
        class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
      >
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-sm font-extrabold text-[var(--text-main)]">
              Lokaler Speicher- und Synchronisationsstatus
            </h2>
            <p class="mt-0.5 text-xs text-[var(--text-muted)]">
              Vollständige verschlüsselte Offline-Verfügbarkeit aller deiner Gesundheitsdaten
            </p>
          </div>
          <Badge variant="success">Synchronisiert</Badge>
        </div>

        <div class="w-full overflow-x-auto">
          <table class="w-full border-collapse text-left text-xs">
            <thead>
              <tr
                class="border-b border-[var(--border-subtle)] text-[0.625rem] tracking-wider text-[var(--text-muted)] uppercase"
              >
                <th class="px-3 py-2.5">Tabelle</th>
                <th class="px-3 py-2.5">Datensätze</th>
                <th class="px-3 py-2.5">Speichergröße</th>
                <th class="px-3 py-2.5 text-right">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)]">
              {#each dexieTables as t}
                <tr>
                  <td class="px-3 py-2.5 font-bold text-[var(--text-main)]">{t.name}</td>
                  <td class="px-3 py-2.5 font-bold text-[var(--color-primary)] tabular-nums"
                    >{t.rows}</td
                  >
                  <td class="px-3 py-2.5 text-[var(--text-muted)] tabular-nums">{t.size}</td>
                  <td class="px-3 py-2.5 text-right">
                    <Badge variant="default" class="text-[0.5625rem]"
                      >{t.status || 'Lokal gecacht'}</Badge
                    >
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
