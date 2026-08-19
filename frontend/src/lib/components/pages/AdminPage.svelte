<script lang="ts">
  import Badge from '../ui/Badge.svelte';

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
    {
      id: 'j1',
      name: 'DataQualitySweepJob',
      cron: '0 4 * * *',
      nextRun: 'Morgen 04:00',
      lastDuration: '240ms',
      status: 'Aktiv'
    },
    {
      id: 'j2',
      name: 'CircadianScoreRecalculationJob',
      cron: '*/30 * * * *',
      nextRun: 'In 12 Min',
      lastDuration: '45ms',
      status: 'Aktiv'
    },
    {
      id: 'j3',
      name: 'InsightsCoachingGenerationJob',
      cron: '0 6 * * 1',
      nextRun: 'Montag 06:00',
      lastDuration: '820ms',
      status: 'Aktiv'
    },
    {
      id: 'j4',
      name: 'SyncPushLogPruningJob',
      cron: '0 0 * * *',
      nextRun: 'Heute 24:00',
      lastDuration: '15ms',
      status: 'Aktiv'
    },
    {
      id: 'j5',
      name: 'LeaderboardScoreAggregationJob',
      cron: '0 */4 * * *',
      nextRun: 'In 2h 14m',
      lastDuration: '110ms',
      status: 'Aktiv'
    }
  ];

  const usersList = [
    {
      id: 'u1',
      username: 'philipp',
      displayName: 'Philipp Fleischer',
      email: 'philipp@salus.local',
      role: 'Superadmin',
      isActive: true,
      createdAt: '01.01.2026'
    }
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
  <!-- Server Metrics Grid -->
  <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
    <div class="rounded-3xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
      <span class="block text-[0.6875rem] font-bold text-text-muted uppercase">Server Uptime</span>
      <span class="mt-1 block text-sm font-extrabold text-text-main">{serverStats.uptime}</span>
    </div>

    <div class="rounded-3xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
      <span class="block text-[0.6875rem] font-bold text-text-muted uppercase"
        >Datenbank-Engine</span
      >
      <span class="mt-1 block text-sm font-extrabold text-primary">{serverStats.dbEngine}</span>
    </div>

    <div class="rounded-3xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
      <span class="block text-[0.6875rem] font-bold text-text-muted uppercase">DB-Dateigröße</span>
      <span class="mt-1 block text-sm font-extrabold text-emerald-500 tabular-nums"
        >{serverStats.dbSize}</span
      >
    </div>

    <div class="rounded-3xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
      <span class="block text-[0.6875rem] font-bold text-text-muted uppercase"
        >SSE EventBus Live</span
      >
      <span class="mt-1 block text-sm font-extrabold text-amber-500 tabular-nums"
        >{serverStats.eventBusSubscribers} Clients verbunden</span
      >
    </div>
  </div>

  <!-- AppScheduler Periodic Background Jobs (ADR-009) -->
  <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs sm:p-6">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 class="text-base font-extrabold text-text-main">
          Hintergrund-Scheduler Jobs (AppScheduler)
        </h2>
        <p class="mt-0.5 text-xs text-text-muted">
          Asynchrone periodische Aufgaben für Datenplausibilität, Zirkadian-Scores und
          Sync-Push-Pruning
        </p>
      </div>
      <Badge variant="success">{schedulerJobsList.length} Aktive Scheduler-Jobs</Badge>
    </div>

    <div class="w-full overflow-x-auto">
      <table class="w-full border-collapse text-left text-xs">
        <thead>
          <tr
            class="border-b border-border-subtle text-[0.625rem] tracking-wider text-text-muted uppercase"
          >
            <th class="px-3 py-2.5">Job Name</th>
            <th class="px-3 py-2.5">Cron-Intervall</th>
            <th class="px-3 py-2.5">Nächste Ausführung</th>
            <th class="px-3 py-2.5">Letzte Dauer</th>
            <th class="px-3 py-2.5">Status</th>
            <th class="px-3 py-2.5 text-right">Manuelle Ausführung</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border-subtle">
          {#each schedulerJobsList as job}
            <tr class="transition-colors hover:bg-surface-50">
              <td class="px-3 py-3 font-bold text-text-main">{job.name}</td>
              <td class="px-3 py-3 text-text-muted tabular-nums">{job.cron}</td>
              <td class="px-3 py-3 text-text-main tabular-nums">{job.nextRun}</td>
              <td class="px-3 py-3 text-text-soft tabular-nums">{job.lastDuration}</td>
              <td class="px-3 py-3">
                <Badge variant="success" class="text-[0.5625rem]">{job.status}</Badge>
              </td>
              <td class="px-3 py-3 text-right">
                <button
                  type="button"
                  onclick={() => triggerJob(job.name)}
                  disabled={isTriggeringJob === job.name}
                  class="cursor-pointer rounded-lg border border-border-subtle bg-surface-50 px-2.5 py-1 text-xs font-bold text-primary shadow-2xs transition-all hover:bg-primary hover:text-white"
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
  <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs sm:p-6">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 class="text-base font-extrabold text-text-main">Benutzerverwaltung</h2>
        <p class="mt-0.5 text-xs text-text-muted">
          Registrierte Benutzerkonten und Berechtigungsrollen
        </p>
      </div>
      <button
        type="button"
        onclick={() => alert('Neuen Benutzer anlegen')}
        class="cursor-pointer rounded-2xl bg-primary px-3.5 py-1.5 text-xs font-bold text-white shadow-xs hover:opacity-90"
      >
        + Neuer Benutzer
      </button>
    </div>

    <div class="w-full overflow-x-auto">
      <table class="w-full border-collapse text-left text-xs">
        <thead>
          <tr
            class="border-b border-border-subtle text-[0.625rem] tracking-wider text-text-muted uppercase"
          >
            <th class="px-3 py-2.5">Benutzername</th>
            <th class="px-3 py-2.5">Anzeigename</th>
            <th class="px-3 py-2.5">E-Mail</th>
            <th class="px-3 py-2.5">Rolle</th>
            <th class="px-3 py-2.5">Status</th>
            <th class="px-3 py-2.5 text-right">Aktionen</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border-subtle">
          {#each usersList as u}
            <tr class="transition-colors hover:bg-surface-50">
              <td class="px-3 py-3 font-bold text-text-main">{u.username}</td>
              <td class="px-3 py-3 text-text-main">{u.displayName}</td>
              <td class="px-3 py-3 text-text-muted">{u.email}</td>
              <td class="px-3 py-3"><Badge variant="primary">{u.role}</Badge></td>
              <td class="px-3 py-3"><Badge variant="success">Aktiv</Badge></td>
              <td class="px-3 py-3 text-right">
                <button
                  type="button"
                  onclick={() => alert('Benutzer bearbeiten')}
                  class="cursor-pointer font-bold text-primary hover:underline"
                >
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
