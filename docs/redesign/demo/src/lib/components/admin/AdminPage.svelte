<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import TextInput from '../ui/TextInput.svelte';
  import SelectDropdown from '../ui/SelectDropdown.svelte';

  export type AdminTab = 'data_quality' | 'users' | 'foods' | 'backups' | 'telemetry';

  let activeTab = $state<AdminTab>('data_quality');

  // ─── 1. USER MANAGEMENT DATA ───
  interface SalusUser {
    id: string;
    username: string;
    email: string;
    role: 'admin' | 'user';
    status: 'active' | 'inactive';
    lastActive: string;
    timezone: string;
  }

  let users = $state<SalusUser[]>([
    { id: 'u1', username: 'philipp', email: 'philipp@salus.local', role: 'admin', status: 'active', lastActive: 'Gerade eben', timezone: 'Europe/Berlin' },
    { id: 'u2', username: 'elena_biotech', email: 'elena@bioresearch.org', role: 'user', status: 'active', lastActive: 'Vor 2 Stunden', timezone: 'Europe/Zurich' },
    { id: 'u3', username: 'dr_weber', email: 'weber@kardiologie-praxis.de', role: 'user', status: 'active', lastActive: 'Gestern', timezone: 'Europe/Berlin' },
    { id: 'u4', username: 'marcus_run', email: 'marcus@sportlab.io', role: 'user', status: 'inactive', lastActive: 'Vor 14 Tagen', timezone: 'UTC' }
  ]);

  let newUserModal = $state(false);
  let newUsername = $state('');
  let newEmail = $state('');
  let newRole = $state<'admin' | 'user'>('user');

  function addUser() {
    if (!newUsername || !newEmail) return;
    users.push({
      id: `u${users.length + 1}`,
      username: newUsername,
      email: newEmail,
      role: newRole,
      status: 'active',
      lastActive: 'Neu angelegt',
      timezone: 'Europe/Berlin'
    });
    newUsername = '';
    newEmail = '';
    newUserModal = false;
  }

  // ─── 2. DATA QUALITY ENGINE DATA ───
  interface QualityAnomaly {
    id: string;
    entity: string;
    severity: 'critical' | 'warning' | 'info';
    rule: string;
    description: string;
    occurredAt: string;
    autoRepaired: boolean;
  }

  let anomalies = $state<QualityAnomaly[]>([
    {
      id: 'dq-101',
      entity: 'Measurement',
      severity: 'warning',
      rule: 'Systolischer < Diastolischer Blutdruck',
      description: 'Messwert 78/120 mmHg erkannt. Werte wurden durch Write-Time-Check plausibilisiert.',
      occurredAt: '14.08.2026 07:42',
      autoRepaired: true
    },
    {
      id: 'dq-102',
      entity: 'WorkoutLogEntry',
      severity: 'info',
      rule: 'Duplikat-Erkennung (Sync Push Dedup)',
      description: 'Zwei identische Sätze innerhalb von 200ms via Mehrfach-Push übermittelt. Zweiter Satz verworfen.',
      occurredAt: '13.08.2026 18:22',
      autoRepaired: true
    },
    {
      id: 'dq-103',
      entity: 'Measurement',
      severity: 'info',
      rule: 'Puls > 240 bpm (Extremwert)',
      description: 'Ruhepulsmessung von 260 bpm als Messartefakt markiert (Flag: data_quality_flag).',
      occurredAt: '11.08.2026 03:15',
      autoRepaired: true
    }
  ]);

  let isSweeping = $state(false);

  function triggerSweep() {
    isSweeping = true;
    setTimeout(() => {
      isSweeping = false;
      alert('Vollständiger Data-Quality-Sweep abgeschlossen: 2.960 Datensätze geprüft. 0 Inkonsistenzen gefunden.');
    }, 1200);
  }

  // ─── 3. GLOBAL FOODS MANAGEMENT ───
  let foodItems = $state([
    { id: 'f-1', name: 'Hähnchenbrustfilet roh', source: 'USDA Core', kcal: 110, protein: 23.0, carbs: 0.0, fat: 1.5, verified: true },
    { id: 'f-2', name: 'Haferflocken Vollkorn', source: 'OpenFoodFacts', kcal: 370, protein: 13.5, carbs: 58.7, fat: 7.0, verified: true },
    { id: 'f-3', name: 'Magerquark 0.2%', source: 'System Seeded', kcal: 68, protein: 12.5, carbs: 4.0, fat: 0.2, verified: true },
    { id: 'f-4', name: 'Whey Isolat Vanille', source: 'Custom Global', kcal: 380, protein: 85.0, carbs: 2.5, fat: 1.0, verified: false }
  ]);

  // ─── 4. SERVER BACKUPS ───
  let backups = $state([
    { id: 'bak-1', filename: 'salus_backup_2026-08-14_0300.sqlite.zst', size: '12.4 MB', type: 'Automatisch (Daily)', date: 'Heute 03:00 UTC' },
    { id: 'bak-2', filename: 'salus_backup_2026-08-13_0300.sqlite.zst', size: '12.1 MB', type: 'Automatisch (Daily)', date: 'Gestern 03:00 UTC' },
    { id: 'bak-3', filename: 'salus_manual_pre_migration_v2.sqlite.zst', size: '11.8 MB', type: 'Manuell', date: '10.08.2026' }
  ]);

  // ─── 5. SERVER TELEMETRY & SCHEDULER DATA ───
  const scheduledJobs = [
    { name: 'DataQualitySweepJob', interval: 'Alle 6 Stunden', lastRun: 'Vor 45 Min', status: 'Erfolgreich', nextRun: 'in 5h 15m' },
    { name: 'SyncPushLogCleanupJob', interval: 'Täglich um 03:00 UTC', lastRun: 'Heute 03:00', status: 'Erfolgreich', nextRun: 'Morgen 03:00' },
    { name: 'CircadianScheduleJob', interval: 'Stündlich', lastRun: 'Vor 12 Min', status: 'Erfolgreich', nextRun: 'in 48m' },
    { name: 'OpenScienceSynthesisJob', interval: 'Wöchentlich (Sonntag)', lastRun: '10.08.2026', status: 'Erfolgreich', nextRun: '17.08.2026' }
  ];
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Systemadministration und Instanzkontrolle</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Server-Telemetrie, Task-Scheduler, Datenvalidierung, Benutzerkonten und Backups
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="primary" class="text-xs">Salus Core v2.4.0</Badge>
    </div>
  </div>

  <!-- Primary Sub-Navigation Tabs -->
  <div class="flex gap-2 bg-[var(--bg-surface-50)] p-1.5 rounded-2xl border border-[var(--border-subtle)] overflow-x-auto">
    <button
      type="button"
      onclick={() => activeTab = 'data_quality'}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'data_quality' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="labs" class="text-[var(--color-vital)]" />
      <span>Datenqualitäts-Engine</span>
      <Badge variant="success" class="text-[0.625rem]">100% OK</Badge>
    </button>

    <button
      type="button"
      onclick={() => activeTab = 'users'}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'users' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="sun" class="text-[var(--color-circadian)]" />
      <span>Benutzerverwaltung</span>
      <Badge variant="default" class="text-[0.625rem]">{users.length} Konten</Badge>
    </button>

    <button
      type="button"
      onclick={() => activeTab = 'foods'}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'foods' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="food" class="text-[var(--color-activity)]" />
      <span>Globale Lebensmittel</span>
    </button>

    <button
      type="button"
      onclick={() => activeTab = 'backups'}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'backups' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="labs" class="text-[var(--text-soft)]" />
      <span>Server-Backups</span>
    </button>

    <button
      type="button"
      onclick={() => activeTab = 'telemetry'}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'telemetry' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="insights" class="text-[var(--color-primary)]" />
      <span>Telemetrie und Scheduler</span>
    </button>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 1: DATA QUALITY ENGINE                                  -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'data_quality'}
    <div class="space-y-5">
      <!-- Status Banner -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-6 shadow-[var(--shadow-card)] flex items-center justify-between flex-wrap gap-4">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center text-xl">
            <Icon name="check" size={24} />
          </div>
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Plausibilitäts-Prüfung: 100% Konform</h2>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">
              Letzter Sweep vor 45 Minuten. Alle Schreib-Transaktionen durchlaufen die Write-Time Validation.
            </p>
          </div>
        </div>
        <Btn variant="secondary" size="sm" onclick={triggerSweep} disabled={isSweeping}>
          {isSweeping ? 'Prüfung läuft...' : ' Manuellen Sweep ausführen'}
        </Btn>
      </div>

      <!-- Anomaly Audit Table -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <h3 class="text-sm font-bold text-[var(--text-main)] mb-4">Protokollierte Validierungs-Ereignisse</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-[var(--border-subtle)] text-[var(--text-soft)] uppercase tracking-wider text-[0.625rem]">
                <th class="py-2.5 px-3">Ereignis-ID</th>
                <th class="py-2.5 px-3">Entität</th>
                <th class="py-2.5 px-3">Regel</th>
                <th class="py-2.5 px-3">Befund / Maßnahme</th>
                <th class="py-2.5 px-3">Zeitstempel</th>
                <th class="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)]">
              {#each anomalies as a}
                <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
                  <td class="py-3 px-3 font-mono text-[var(--color-primary)]">{a.id}</td>
                  <td class="py-3 px-3 font-semibold">{a.entity}</td>
                  <td class="py-3 px-3">{a.rule}</td>
                  <td class="py-3 px-3 text-[var(--text-muted)] max-w-sm">{a.description}</td>
                  <td class="py-3 px-3 font-mono text-[var(--text-soft)]">{a.occurredAt}</td>
                  <td class="py-3 px-3 text-right">
                    <Badge variant="success">Automatisch Bereinigt</Badge>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 2: USER MANAGEMENT                                      -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'users'}
    <div class="space-y-5">
      <div class="flex justify-between items-center flex-wrap gap-3">
        <div>
          <h3 class="text-sm font-bold text-[var(--text-main)]">Registrierte Instanz-Benutzer</h3>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">Multi-User Berechtigungen und Zugriffsstatus</p>
        </div>
        <Btn variant="primary" size="sm" onclick={() => newUserModal = true}>
          + Benutzer anlegen
        </Btn>
      </div>

      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-[var(--border-subtle)] text-[var(--text-soft)] uppercase tracking-wider text-[0.625rem]">
                <th class="py-2.5 px-3">Benutzername</th>
                <th class="py-2.5 px-3">E-Mail</th>
                <th class="py-2.5 px-3">Rolle</th>
                <th class="py-2.5 px-3">Zeitzone</th>
                <th class="py-2.5 px-3">Letzte Aktivität</th>
                <th class="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)]">
              {#each users as u}
                <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
                  <td class="py-3 px-3 font-bold text-[var(--text-main)]">@{u.username}</td>
                  <td class="py-3 px-3 text-[var(--text-muted)]">{u.email}</td>
                  <td class="py-3 px-3">
                    <Badge variant={u.role === 'admin' ? 'primary' : 'default'}>{u.role}</Badge>
                  </td>
                  <td class="py-3 px-3 text-[var(--text-soft)]">{u.timezone}</td>
                  <td class="py-3 px-3 text-[var(--text-muted)]">{u.lastActive}</td>
                  <td class="py-3 px-3 text-right">
                    <Badge variant={u.status === 'active' ? 'success' : 'vital'}>{u.status}</Badge>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 3: GLOBAL FOODS CATALOG (ADMIN)                         -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'foods'}
    <div class="space-y-5">
      <div class="flex justify-between items-center flex-wrap gap-3">
        <div>
          <h3 class="text-sm font-bold text-[var(--text-main)]">Globale Lebensmittel- & Nährwert-Datenbank</h3>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">System-geseedete Lebensmittel (user_id = null) für alle Instanz-Nutzer</p>
        </div>
        <Btn variant="primary" size="sm" onclick={() => alert('Neues globales Lebensmittel anlegen')}>
          + Globales Lebensmittel anlegen
        </Btn>
      </div>

      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-[var(--border-subtle)] text-[var(--text-soft)] uppercase tracking-wider text-[0.625rem]">
                <th class="py-2.5 px-3">Lebensmittel</th>
                <th class="py-2.5 px-3">Quelle / Herkunft</th>
                <th class="py-2.5 px-3">Kalorien / 100g</th>
                <th class="py-2.5 px-3">Protein</th>
                <th class="py-2.5 px-3">Kohlenhydrate</th>
                <th class="py-2.5 px-3">Fett</th>
                <th class="py-2.5 px-3 text-right">Verifiziert</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)] font-mono">
              {#each foodItems as f}
                <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
                  <td class="py-3 px-3 font-sans font-bold text-[var(--text-main)]">{f.name}</td>
                  <td class="py-3 px-3 font-sans text-[var(--text-muted)]">{f.source}</td>
                  <td class="py-3 px-3 font-bold text-[var(--color-primary)]">{f.kcal} kcal</td>
                  <td class="py-3 px-3 text-[var(--text-muted)]">{f.protein}g</td>
                  <td class="py-3 px-3 text-[var(--text-muted)]">{f.carbs}g</td>
                  <td class="py-3 px-3 text-[var(--text-muted)]">{f.fat}g</td>
                  <td class="py-3 px-3 text-right font-sans">
                    <Badge variant={f.verified ? 'success' : 'default'}>{f.verified ? 'Verifiziert' : 'Prüfung'}</Badge>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 4: SERVER BACKUPS                                       -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'backups'}
    <div class="space-y-5">
      <div class="flex justify-between items-center flex-wrap gap-3">
        <div>
          <h3 class="text-sm font-bold text-[var(--text-main)]">Automatisierte Server-Backups</h3>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">Zstandard-komprimierte Datenbank-Snapshots</p>
        </div>
        <Btn variant="primary" size="sm" onclick={() => alert('Manuelles Server-Backup wird erstellt...')}>
           Snapshot jetzt erstellen
        </Btn>
      </div>

      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-[var(--border-subtle)] text-[var(--text-soft)] uppercase tracking-wider text-[0.625rem]">
                <th class="py-2.5 px-3">Dateiname</th>
                <th class="py-2.5 px-3">Typ</th>
                <th class="py-2.5 px-3">Erstellt am</th>
                <th class="py-2.5 px-3">Dateigröße</th>
                <th class="py-2.5 px-3 text-right">Aktion</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)] font-mono">
              {#each backups as b}
                <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
                  <td class="py-3 px-3 font-bold text-[var(--text-main)]">{b.filename}</td>
                  <td class="py-3 px-3 font-sans text-[var(--text-muted)]">{b.type}</td>
                  <td class="py-3 px-3 text-[var(--text-soft)]">{b.date}</td>
                  <td class="py-3 px-3 text-[var(--color-primary)]">{b.size}</td>
                  <td class="py-3 px-3 text-right font-sans">
                    <button type="button" onclick={() => alert(`Download gestartet: ${b.filename}`)} class="font-semibold text-[var(--color-primary)] hover:underline cursor-pointer">
                      Download 
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 5: TELEMETRY & SCHEDULER                                -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'telemetry'}
    <div class="space-y-5">
      <!-- Telemetry Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-4 shadow-[var(--shadow-card)]">
          <span class="text-[0.6875rem] font-mono text-[var(--text-soft)] uppercase tracking-wider">SSE Live-Clients</span>
          <div class="text-2xl font-black text-[var(--color-primary)] mt-1 font-mono">3 Aktiv</div>
          <span class="text-xs text-[var(--text-muted)]">Zero-Polling Server-Sent Events</span>
        </div>

        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-4 shadow-[var(--shadow-card)]">
          <span class="text-[0.6875rem] font-mono text-[var(--text-soft)] uppercase tracking-wider">Datenbank-Größe</span>
          <div class="text-2xl font-black text-[var(--text-main)] mt-1 font-mono">14.8 MB</div>
          <span class="text-xs text-[var(--text-muted)]">SQLite (WAL Mode aktiviert)</span>
        </div>

        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-4 shadow-[var(--shadow-card)]">
          <span class="text-[0.6875rem] font-mono text-[var(--text-soft)] uppercase tracking-wider">API Antwortzeit (p95)</span>
          <div class="text-2xl font-black text-emerald-500 mt-1 font-mono">4.2 ms</div>
          <span class="text-xs text-[var(--text-muted)]">FastAPI Uvicorn Loop</span>
        </div>

        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-4 shadow-[var(--shadow-card)]">
          <span class="text-[0.6875rem] font-mono text-[var(--text-soft)] uppercase tracking-wider">Hintergrund-Jobs</span>
          <div class="text-2xl font-black text-[var(--color-circadian)] mt-1 font-mono">4 / 4 OK</div>
          <span class="text-xs text-[var(--text-muted)]">AppScheduler (asyncio)</span>
        </div>
      </div>

      <!-- Scheduled Jobs Table -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <h3 class="text-sm font-bold text-[var(--text-main)] mb-4">Registrierte Hintergrund-Jobs (AppScheduler)</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-[var(--border-subtle)] text-[var(--text-soft)] uppercase tracking-wider text-[0.625rem]">
                <th class="py-2.5 px-3">Job-Klasse</th>
                <th class="py-2.5 px-3">Intervall</th>
                <th class="py-2.5 px-3">Letzter Durchlauf</th>
                <th class="py-2.5 px-3">Nächster Durchlauf</th>
                <th class="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)]">
              {#each scheduledJobs as j}
                <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
                  <td class="py-3 px-3 font-mono font-bold text-[var(--text-main)]">{j.name}</td>
                  <td class="py-3 px-3 text-[var(--text-muted)]">{j.interval}</td>
                  <td class="py-3 px-3 font-mono">{j.lastRun}</td>
                  <td class="py-3 px-3 font-mono text-[var(--text-soft)]">{j.nextRun}</td>
                  <td class="py-3 px-3 text-right">
                    <Badge variant="success">{j.status}</Badge>
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

<!-- Modal: New User -->
{#if newUserModal}
  <div class="fixed inset-0 bg-black/60 backdrop-blur-xs z-55 flex items-center justify-center p-4">
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-base font-extrabold text-[var(--text-main)]">Neuen Benutzer anlegen</h3>
        <button type="button" onclick={() => newUserModal = false} class="text-[var(--text-muted)] hover:text-[var(--text-main)] cursor-pointer text-lg">&times;</button>
      </div>

      <div class="space-y-3 text-xs">
        <TextInput
          label="Benutzername"
          bind:value={newUsername}
          placeholder="z.B. alex_health"
        />
        <TextInput
          label="E-Mail"
          type="email"
          bind:value={newEmail}
          placeholder="alex@domain.de"
        />
        <SelectDropdown
          label="Rolle"
          bind:value={newRole}
          options={[
            { value: 'user', label: 'Standard-Benutzer (User)' },
            { value: 'admin', label: 'Administrator (Voller Systemzugriff)' }
          ]}
        />
      </div>

      <div class="flex gap-2 justify-end pt-2">
        <Btn variant="secondary" size="sm" onclick={() => newUserModal = false}>Abbrechen</Btn>
        <Btn variant="primary" size="sm" onclick={addUser}>Benutzer speichern</Btn>
      </div>
    </div>
  </div>
{/if}
