<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  // ─── ADMIN CONSOLE STATE ───
  let serverStats = $state({
    uptime: '18 Tage, 4 Stunden',
    dbEngine: 'SQLite (WAL-Mode, StaticPool)',
    dbSize: '4.8 MB',
    activeUsers: 1,
    schedulerJobs: 6,
    eventBusSubscribers: 2,
    memoryUsage: '42 MB / 512 MB',
    cpuUsage: '1.2%'
  });

  const schedulerJobsList = [
    { id: 'j1', name: 'DataQualitySweepJob', cron: '0 4 * * *', nextRun: 'Morgen 04:00', lastDuration: '240ms', status: 'Aktiv' },
    { id: 'j2', name: 'CircadianScoreRecalculationJob', cron: '*/30 * * * *', nextRun: 'In 12 Min', lastDuration: '45ms', status: 'Aktiv' },
    { id: 'j3', name: 'InsightsCoachingGenerationJob', cron: '0 6 * * 1', nextRun: 'Montag 06:00', lastDuration: '820ms', status: 'Aktiv' },
    { id: 'j4', name: 'SyncPushLogPruningJob', cron: '0 0 * * *', nextRun: 'Heute 24:00', lastDuration: '15ms', status: 'Aktiv' },
    { id: 'j5', name: 'LeaderboardScoreAggregationJob', cron: '0 */4 * * *', nextRun: 'In 2h 14m', lastDuration: '110ms', status: 'Aktiv' }
  ];

  const usersList = [
    { id: 'u1', username: 'philipp', displayName: 'Philipp Fleischer', email: 'philipp@salus.local', role: 'Superadmin', isActive: true, createdAt: '01.01.2026' }
  ];

  let isTriggeringJob = $state<string | null>(null);

  function triggerJob(jobName: string) {
    isTriggeringJob = jobName;
    setTimeout(() => {
      isTriggeringJob = null;
      alert(`Hintergrundjob "${jobName}" erfolgreich manuell ausgeführt`);
    }, 800);
  }
</script>

<div class="space-y-6">
  
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <div class="flex items-center gap-2">
        <h1 class="text-2xl font-extrabold tracking-tight">System- und Server-Administration</h1>
        <Badge variant="primary" class="font-bold">Admin-Modus</Badge>
      </div>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Server-Ressourcen, AppScheduler Hintergrundjobs (ADR-009), Datenbank-Statistiken und Benutzerverwaltung
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">FastAPI + SQLModel Backend</Badge>
    </div>
  </div>

  <!-- Server Metrics Grid -->
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
    <div class="p-4 rounded-3xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] shadow-xs">
      <span class="text-[0.6875rem] text-[var(--text-muted)] font-bold uppercase block">Server Uptime</span>
      <span class="text-sm font-extrabold text-[var(--text-main)] mt-1 block">{serverStats.uptime}</span>
    </div>

    <div class="p-4 rounded-3xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] shadow-xs">
      <span class="text-[0.6875rem] text-[var(--text-muted)] font-bold uppercase block">Datenbank-Engine</span>
      <span class="text-sm font-extrabold text-[var(--color-primary)] mt-1 block">{serverStats.dbEngine}</span>
    </div>

    <div class="p-4 rounded-3xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] shadow-xs">
      <span class="text-[0.6875rem] text-[var(--text-muted)] font-bold uppercase block">DB-Dateigröße</span>
      <span class="text-sm font-extrabold text-emerald-500 mt-1 block tabular-nums">{serverStats.dbSize}</span>
    </div>

    <div class="p-4 rounded-3xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] shadow-xs">
      <span class="text-[0.6875rem] text-[var(--text-muted)] font-bold uppercase block">SSE EventBus Live</span>
      <span class="text-sm font-extrabold text-amber-500 mt-1 block tabular-nums">{serverStats.eventBusSubscribers} Clients verbunden</span>
    </div>
  </div>

  <!-- AppScheduler Periodic Background Jobs (ADR-009) -->
  <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 sm:p-6 shadow-xs space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h2 class="text-base font-extrabold text-[var(--text-main)]">Hintergrund-Scheduler Jobs (AppScheduler)</h2>
        <p class="text-xs text-[var(--text-muted)] mt-0.5">
          Asynchrone periodische Aufgaben für Datenplausibilität, Zirkadian-Scores und Sync-Push-Pruning
        </p>
      </div>
      <Badge variant="success">{schedulerJobsList.length} Aktive Scheduler-Jobs</Badge>
    </div>

    <div class="w-full overflow-x-auto">
      <table class="w-full text-left text-xs border-collapse">
        <thead>
          <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.625rem]">
            <th class="py-2.5 px-3">Job Name</th>
            <th class="py-2.5 px-3">Cron-Intervall</th>
            <th class="py-2.5 px-3">Nächste Ausführung</th>
            <th class="py-2.5 px-3">Letzte Dauer</th>
            <th class="py-2.5 px-3">Status</th>
            <th class="py-2.5 px-3 text-right">Manuelle Ausführung</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)]">
          {#each schedulerJobsList as job}
            <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
              <td class="py-3 px-3 font-bold text-[var(--text-main)]">{job.name}</td>
              <td class="py-3 px-3 text-[var(--text-muted)] tabular-nums">{job.cron}</td>
              <td class="py-3 px-3 text-[var(--text-main)] tabular-nums">{job.nextRun}</td>
              <td class="py-3 px-3 text-[var(--text-soft)] tabular-nums">{job.lastDuration}</td>
              <td class="py-3 px-3">
                <Badge variant="success" class="text-[0.5625rem]">{job.status}</Badge>
              </td>
              <td class="py-3 px-3 text-right">
                <button
                  type="button"
                  onclick={() => triggerJob(job.name)}
                  disabled={isTriggeringJob === job.name}
                  class="px-2.5 py-1 rounded-lg bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-white transition-all cursor-pointer shadow-2xs"
                >
                  {isTriggeringJob === job.name ? 'Läuft...' : '▶ Ausführen'}
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>

  <!-- User Management Table -->
  <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 sm:p-6 shadow-xs space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h2 class="text-base font-extrabold text-[var(--text-main)]">Benutzerverwaltung</h2>
        <p class="text-xs text-[var(--text-muted)] mt-0.5">Registrierte Benutzerkonten und Berechtigungsrollen</p>
      </div>
      <button type="button" onclick={() => alert('Neuen Benutzer anlegen')} class="px-3.5 py-1.5 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 cursor-pointer shadow-xs">
        + Neuer Benutzer
      </button>
    </div>

    <div class="w-full overflow-x-auto">
      <table class="w-full text-left text-xs border-collapse">
        <thead>
          <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.625rem]">
            <th class="py-2.5 px-3">Benutzername</th>
            <th class="py-2.5 px-3">Anzeigename</th>
            <th class="py-2.5 px-3">E-Mail</th>
            <th class="py-2.5 px-3">Rolle</th>
            <th class="py-2.5 px-3">Status</th>
            <th class="py-2.5 px-3 text-right">Aktionen</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)]">
          {#each usersList as u}
            <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
              <td class="py-3 px-3 font-bold text-[var(--text-main)]">{u.username}</td>
              <td class="py-3 px-3 text-[var(--text-main)]">{u.displayName}</td>
              <td class="py-3 px-3 text-[var(--text-muted)]">{u.email}</td>
              <td class="py-3 px-3"><Badge variant="primary">{u.role}</Badge></td>
              <td class="py-3 px-3"><Badge variant="success">Aktiv</Badge></td>
              <td class="py-3 px-3 text-right">
                <button type="button" onclick={() => alert('Benutzer bearbeiten')} class="text-[var(--color-primary)] hover:underline font-bold cursor-pointer">
                  Bearbeiten
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>

</div>
