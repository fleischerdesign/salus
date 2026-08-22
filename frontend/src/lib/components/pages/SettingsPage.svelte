<script lang="ts">
  import { page } from '$app/state';
  import Badge from '../ui/Badge.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import Toggle from '../ui/Toggle.svelte';
  import HueRing from '../ui/HueRing.svelte';
  import Icon from '../ui/Icon.svelte';
  import IntegrationsView from '../settings/IntegrationsView.svelte';
  import { theme, ACCENT_HUES } from '$stores/theme.svelte';

  export type SettingsTab =
    'account' | 'appearance' | 'security' | 'sources' | 'notifications' | 'shares' | 'data';

  let { initialTab = 'account' } = $props<{
    initialTab?: SettingsTab;
  }>();

  let activeTab = $derived<SettingsTab>(
    page.url.pathname.includes('/settings/app')
      ? 'appearance'
      : page.url.pathname.includes('/settings/security') ||
          page.url.pathname.includes('/settings/privacy')
        ? 'security'
        : page.url.pathname.includes('/settings/sources')
          ? 'sources'
          : page.url.pathname.includes('/settings/notifications')
            ? 'notifications'
            : page.url.pathname.includes('/settings/shares')
              ? 'shares'
              : page.url.pathname.includes('/settings/data')
                ? 'data'
                : initialTab
  );

  // ─── 1. ACCOUNT: Display Name, Biometrie, Zeitzone, Sprache ───
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

  // ─── 3. SECURITY: Passwort, App-Sperre, SSO ───
  let currentPassword = $state('');
  let newPassword = $state('');
  let confirmPassword = $state('');

  let biometricLock = $state(true);
  let sessionLock = $state(true);

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

  // ─── 5. NOTIFICATIONS: Toast- und Sync-Benachrichtigungen ───
  let toastPosition = $state('bottom-right');

  const toastOptions = [
    { value: 'bottom-right', label: 'Unten Rechts (Standard)' },
    { value: 'top-right', label: 'Oben Rechts' },
    { value: 'bottom-center', label: 'Unten Mitte' }
  ];

  let healthSyncNotifications = $state(true);
  let backgroundSyncNotifications = $state(true);
  let systemStatusNotifications = $state(true);

  // ─── 6. SHARES & MEDICAL ACCESS STATE ───
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

  // ─── 7. DATA: Export, Import, lokaler IndexedDB Speicher ───
  const dexieTables = [
    { name: 'measurement', rows: 1840, size: '295 KB' },
    { name: 'workout_set', rows: 840, size: '120 KB' },
    { name: 'meal_item', rows: 680, size: '115 KB' },
    { name: 'lab_result', rows: 180, size: '32 KB' },
    { name: 'outbox (Unified Sync Queue)', rows: 0, size: '0 KB', status: 'Geleert' }
  ];

  const navigationTabs: {
    id: SettingsTab;
    label: string;
    path: string;
    icon: string;
    badge?: string;
  }[] = [
    { id: 'account', label: 'Profil', path: '/settings/account', icon: 'person' },
    { id: 'appearance', label: 'Erscheinungsbild', path: '/settings/app', icon: 'palette' },
    { id: 'security', label: 'Sicherheit', path: '/settings/security', icon: 'lock' },
    { id: 'sources', label: 'Quellen', path: '/settings/sources', icon: 'sensors', badge: '3' },
    {
      id: 'notifications',
      label: 'Benachrichtigungen',
      path: '/settings/notifications',
      icon: 'notifications'
    },
    { id: 'shares', label: 'Freigaben', path: '/settings/shares', icon: 'share', badge: '2' },
    { id: 'data', label: 'Daten', path: '/settings/data', icon: 'database' }
  ];
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Benutzer- und Systemeinstellungen</h1>
      <p class="mt-0.5 text-sm text-text-muted">
        Profil, Erscheinungsbild, Sicherheit, Quellen, Benachrichtigungen, Freigaben und Daten
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Offline-fähig</Badge>
    </div>
  </div>

  <!-- Primary Sub-Navigation Tabs with Soft Mask Fades -->
  <div class="relative w-full overflow-hidden">
    <div
      class="no-scrollbar scroll-mask-x flex gap-2 overflow-x-auto rounded-2xl border border-border-subtle bg-surface-50 p-1.5 px-1 py-1.5 select-none"
    >
      {#each navigationTabs as tab}
        <a
          href={tab.path}
          aria-current={activeTab === tab.id ? 'page' : undefined}
          class="flex shrink-0 cursor-pointer items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
          tab.id
            ? 'bg-surface-0 text-primary shadow-sm'
            : 'text-text-muted hover:text-text-main'}"
        >
          <Icon name={tab.icon} size="sm" />
          <span>{tab.label}</span>
          {#if tab.badge}
            <Badge variant="default" class="text-[0.5625rem] font-bold">{tab.badge}</Badge>
          {/if}
        </a>
      {/each}
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 1: PROFIL                                              -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'account'}
    <div class="space-y-5">
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <!-- Anzeigename & Biometrie -->
        <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <h3 class="text-sm font-extrabold text-text-main">Anzeigename und Biometrie</h3>

          <div class="space-y-3 text-xs">
            <Input label="Anzeigename" bind:value={displayName} />

            <Input label="Benutzername" value={username} disabled={true} />

            <Input label="Körpergröße" type="number" unit="cm" bind:value={heightCm} />
          </div>
        </div>

        <!-- Zeitzone & Sprache -->
        <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <h3 class="text-sm font-extrabold text-text-main">Zeitzone und Sprache</h3>

          <div class="space-y-3 text-xs">
            <div>
              <div class="mb-1 flex items-center justify-between">
                <span class="font-bold text-text-muted">Zeitzone</span>
                <button
                  type="button"
                  onclick={() =>
                    (selectedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone)}
                  class="cursor-pointer text-[0.6875rem] font-bold text-primary hover:underline"
                >
                  Geräte-Zeitzone übernehmen
                </button>
              </div>
              <Select bind:value={selectedTimezone} options={timezoneOptions} />
            </div>

            <Select label="Sprache (Locale)" bind:value={selectedLocale} options={localeOptions} />
          </div>

          <div class="pt-1">
            <button
              type="button"
              onclick={() => alert('Profil gespeichert')}
              class="cursor-pointer rounded-2xl bg-primary px-4 py-2 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
            >
              Profil speichern
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- TAB 2: ERSCHEINUNGSBILD                                     -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'appearance'}
    <div class="space-y-5">
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <!-- Design & Farbmodi -->
        <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <h3 class="text-sm font-extrabold text-text-main">Design und Farbpaletten</h3>

          <div class="space-y-3 text-xs">
            <div>
              <span class="mb-1 block font-bold text-text-muted">Farbmodus</span>
              <div class="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onclick={() => theme.setMode('light')}
                  aria-pressed={theme.mode === 'light'}
                  class="cursor-pointer rounded-2xl border py-2.5 text-xs font-bold transition-all {theme.mode ===
                  'light'
                    ? 'border-transparent bg-primary text-white'
                    : 'border-border-subtle bg-surface-50 text-text-muted'}"
                >
                  Hell
                </button>
                <button
                  type="button"
                  onclick={() => theme.setMode('dark')}
                  aria-pressed={theme.mode === 'dark'}
                  class="cursor-pointer rounded-2xl border py-2.5 text-xs font-bold transition-all {theme.mode ===
                  'dark'
                    ? 'border-transparent bg-primary text-white'
                    : 'border-border-subtle bg-surface-50 text-text-muted'}"
                >
                  Dunkel
                </button>
                <button
                  type="button"
                  onclick={() => theme.setMode('system')}
                  aria-pressed={theme.mode === 'system'}
                  class="cursor-pointer rounded-2xl border py-2.5 text-xs font-bold transition-all {theme.mode ===
                  'system'
                    ? 'border-transparent bg-primary text-white'
                    : 'border-border-subtle bg-surface-50 text-text-muted'}"
                >
                  System
                </button>
              </div>
            </div>

            <Toggle
              label="Farbenblind-Modus"
              description="Verschiebt Statusfarben auf ein farbenblind-sicheres Spektrum (Erfolg wird blau dargestellt)"
              bind:checked={theme.colorblind}
              onchange={(checked) => theme.setColorblind(checked)}
            />
          </div>

          <!-- Akzentfarbe: Preset-Chips & HueRing -->
          <div class="space-y-3 pt-1">
            <span class="block text-sm font-extrabold text-text-main">Akzentfarbe</span>

            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <span class="mb-1.5 block font-bold text-text-muted">Farbverlauf</span>
                <div class="flex flex-wrap gap-1.5">
                  {#each ACCENT_HUES as preset}
                    <button
                      type="button"
                      aria-pressed={theme.accentHue === preset.hue}
                      aria-label={`Akzentfarbe: ${preset.name}`}
                      onclick={() => theme.setAccentHue(preset.hue)}
                      class="group flex cursor-pointer flex-col items-center gap-1 rounded-xl px-1.5 py-1.5 transition-all"
                    >
                      <span
                        class="block h-7 w-7 rounded-full border border-border-subtle shadow-sm transition-all {theme.accentHue ===
                        preset.hue
                          ? 'ring-2 ring-primary ring-offset-2 ring-offset-surface-0'
                          : 'group-hover:scale-110'}"
                        style="background: {preset.color}"
                      ></span>
                      <span
                        class="text-[0.625rem] font-bold {theme.accentHue === preset.hue
                          ? 'text-primary'
                          : 'text-text-muted'}"
                      >
                        {preset.name}
                      </span>
                    </button>
                  {/each}
                </div>
              </div>

              <div class="flex flex-col items-center gap-1.5">
                <HueRing
                  value={theme.accentHue}
                  onchange={(hue) => theme.previewAccentHue(hue)}
                  oncommit={(hue) => theme.setAccentHue(hue)}
                />
                <span class="text-[0.625rem] font-bold text-text-muted tabular-nums"
                  >{theme.accentHue}°</span
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- TAB 3: SICHERHEIT                                           -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'security'}
    <div class="space-y-5">
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <!-- Passwort ändern -->
        <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <h3 class="text-sm font-extrabold text-text-main">Passwort ändern</h3>
          <div class="space-y-2.5 text-xs">
            <Input type="password" bind:value={currentPassword} placeholder="Aktuelles Passwort" />
            <Input type="password" bind:value={newPassword} placeholder="Neues sicheres Passwort" />
            <Input
              type="password"
              bind:value={confirmPassword}
              placeholder="Neues Passwort bestätigen"
            />
            <button
              type="button"
              onclick={() => alert('Passwort geändert')}
              class="cursor-pointer rounded-2xl border border-border-subtle bg-surface-50 px-4 py-2 text-xs font-bold transition-all hover:bg-surface-100"
            >
              Passwort aktualisieren
            </button>
          </div>
        </div>

        <div class="space-y-5">
          <!-- Biometrische App-Sperre / Session Lock -->
          <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
            <h3 class="text-sm font-extrabold text-text-main">App-Sperre und Sitzungen</h3>

            <div class="space-y-4 text-xs">
              <Toggle
                label="Biometrische App-Sperre"
                description="Salus nur noch per Face ID, Touch ID oder Fingerabdruck entsperren"
                bind:checked={biometricLock}
              />

              <Toggle
                label="Session Lock"
                description="App automatisch sperren, wenn das Gerät in den Ruhezustand wechselt"
                bind:checked={sessionLock}
              />
            </div>
          </div>

          <!-- OAuth / OIDC Identity Providers -->
          <div class="space-y-3 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
            <h3 class="text-sm font-extrabold text-text-main">
              Verknüpfte Identitätsanbieter (SSO)
            </h3>
            <div class="space-y-2 text-xs">
              {#each oidcProviders as p}
                <div
                  class="flex items-center justify-between rounded-2xl border border-border-subtle bg-surface-50 p-3"
                >
                  <div>
                    <span class="block font-extrabold text-text-main">{p.name}</span>
                    <span class="text-[0.625rem] text-text-soft"
                      >{p.email || 'Nicht verknüpft'}</span
                    >
                  </div>
                  <button
                    type="button"
                    onclick={() => (p.connected = !p.connected)}
                    class="cursor-pointer text-xs font-bold {p.connected
                      ? 'text-rose-500 hover:underline'
                      : 'text-primary hover:underline'}"
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
    <!-- TAB 4: QUELLEN                                              -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'sources'}
    <IntegrationsView />

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- TAB 5: BENACHRICHTIGUNGEN                                   -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'notifications'}
    <div class="space-y-5">
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <!-- Toast-Meldungen -->
        <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <h3 class="text-sm font-extrabold text-text-main">Toast-Meldungen</h3>

          <div class="space-y-3 text-xs">
            <Select
              label="Toast-Meldungs-Position"
              bind:value={toastPosition}
              options={toastOptions}
            />
          </div>
        </div>

        <!-- Benachrichtigungen -->
        <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <h3 class="text-sm font-extrabold text-text-main">Benachrichtigungen</h3>

          <div class="space-y-4 text-xs">
            <Toggle
              label="Health-Sync-Benachrichtigungen"
              description="Melden, wenn neue Health-Daten von Sensoren synchronisiert wurden"
              bind:checked={healthSyncNotifications}
            />

            <Toggle
              label="Hintergrund-Sync-Benachrichtigungen"
              description="Benachrichtigen über abgeschlossene Synchronisierungen im Hintergrund"
              bind:checked={backgroundSyncNotifications}
            />

            <Toggle
              label="System-Status-Benachrichtigungen"
              description="Hinweise zu Wartung, Updates und Verbindungsstatus des Salus-Systems"
              bind:checked={systemStatusNotifications}
            />
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- TAB 6: FREIGABEN                                            -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'shares'}
    <div class="space-y-5">
      <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h3 class="text-base font-extrabold text-text-main">
              Aktive Arzt- und Klinische Freigaben
            </h3>
            <p class="mt-0.5 text-xs text-text-muted">
              Asymmetrisch verschlüsselte Freigaben mit granularer Berechtigungssteuerung
            </p>
          </div>
          <button
            type="button"
            onclick={() => alert('Neue Arzt-Freigabe erstellen')}
            class="cursor-pointer rounded-2xl bg-primary px-4 py-2 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
          >
            + Neue Freigabe erstellen
          </button>
        </div>

        <div class="space-y-3">
          {#each activeShares as share}
            <div
              class="flex flex-wrap items-start justify-between gap-4 rounded-2xl border border-border-subtle bg-surface-50 p-4"
            >
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-extrabold text-text-main">{share.recipientName}</span>
                  <Badge
                    variant={share.status === 'active' ? 'success' : 'default'}
                    class="text-[0.625rem]"
                  >
                    {share.status === 'active' ? 'Aktiv' : 'Abgelaufen'}
                  </Badge>
                </div>
                <p class="text-xs text-text-muted">
                  {share.role} &bull; Gültig bis: {share.expiresAt}
                </p>
                <div
                  class="rounded-xl border border-border-subtle bg-surface-0 p-2 text-[0.6875rem] text-text-soft"
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
    <!-- TAB 7: DATEN                                                -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'data'}
    <div class="space-y-6">
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <div class="space-y-3 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <h3 class="text-sm font-extrabold text-text-main">Vollständiger Daten-Export</h3>
          <p class="text-xs text-text-muted">
            Exportiere alle deine biometrischen Daten, Workouts, Labore und Mahlzeiten als
            JSON-Archiv oder tabellarische CSV.
          </p>
          <div class="flex flex-wrap gap-2 pt-2">
            <button
              type="button"
              onclick={() => alert('JSON Export')}
              class="cursor-pointer rounded-2xl bg-primary px-4 py-2 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
            >
              JSON-Komplettarchiv exportieren
            </button>
            <button
              type="button"
              onclick={() => alert('CSV Export')}
              class="cursor-pointer rounded-2xl border border-border-subtle bg-surface-50 px-4 py-2 text-xs font-bold transition-all hover:bg-surface-100"
            >
              CSV Messwerte exportieren
            </button>
          </div>
        </div>

        <div class="space-y-3 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <h3 class="text-sm font-extrabold text-text-main">Daten-Import</h3>
          <p class="text-xs text-text-muted">
            Importiere ein zuvor exportiertes Salus JSON-Backup. Vorhandene Daten werden mit der
            Server-Datenbank zusammengeführt.
          </p>
          <div class="pt-2">
            <button
              type="button"
              onclick={() => alert('JSON Import')}
              class="cursor-pointer rounded-2xl border border-border-subtle bg-surface-50 px-4 py-2 text-xs font-bold transition-all hover:bg-surface-100"
            >
              JSON-Backup importieren
            </button>
          </div>
        </div>
      </div>

      <!-- IndexedDB Stats -->
      <div class="space-y-3 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-sm font-extrabold text-text-main">
              Lokaler Speicher (IndexedDB) und Synchronisationsstatus
            </h2>
            <p class="mt-0.5 text-xs text-text-muted">
              Vollständige verschlüsselte Offline-Verfügbarkeit aller deiner Gesundheitsdaten
            </p>
          </div>
          <Badge variant="success">Synchronisiert</Badge>
        </div>

        <div class="w-full overflow-x-auto">
          <table class="w-full border-collapse text-left text-xs">
            <thead>
              <tr
                class="border-b border-border-subtle text-[0.625rem] tracking-wider text-text-muted uppercase"
              >
                <th class="px-3 py-2.5">Tabelle</th>
                <th class="px-3 py-2.5">Datensätze</th>
                <th class="px-3 py-2.5">Speichergröße</th>
                <th class="px-3 py-2.5 text-right">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border-subtle">
              {#each dexieTables as t}
                <tr>
                  <td class="px-3 py-2.5 font-bold text-text-main">{t.name}</td>
                  <td class="px-3 py-2.5 font-bold text-primary tabular-nums">{t.rows}</td>
                  <td class="px-3 py-2.5 text-text-muted tabular-nums">{t.size}</td>
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
