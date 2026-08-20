<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  interface ExerciseProgress {
    id: string;
    name: string;
    e1RM: number;
    bwRatio: number;
    tier: 'Anfänger' | 'Fortgeschritten' | 'Athlet' | 'Elite';
    tierColor: string;
    history: { date: string; weight: number; reps: number; e1RM: number }[];
  }

  const oneRmQuery = useQuery(async () => {
    const [exercises, logs, sessions] = await Promise.all([
      db.exercise.toArray(),
      db.workout_set.toArray(),
      db.workout_session.toArray()
    ]);

    const validExercises = exercises.filter((e) => !e.deleted_at);
    const validLogs = logs.filter((l) => !l.deleted_at && l.weight > 0 && l.reps > 0);
    const sessionMap = new Map(sessions.map((s) => [s.id, s]));

    const logsByExercise = new Map<string, typeof logs>();
    for (const log of validLogs) {
      const list = logsByExercise.get(log.exercise_id) ?? [];
      list.push(log);
      logsByExercise.set(log.exercise_id, list);
    }

    const profiles: ExerciseProgress[] = [];
    for (const ex of validExercises) {
      const exLogs = logsByExercise.get(ex.id);
      if (!exLogs || exLogs.length === 0) continue;

      const history = exLogs
        .map((l) => {
          const session = sessionMap.get(l.session_id);
          const dateStr = session?.started_at
            ? new Date(session.started_at).toLocaleDateString('de-DE', {
                day: '2-digit',
                month: 'short'
              })
            : 'Training';
          // Brzycki 1RM formula: weight * (36 / (37 - reps))
          const e1RM = Math.round(l.weight * (36 / Math.max(1, 37 - l.reps)));
          return { date: dateStr, weight: l.weight, reps: l.reps, e1RM };
        })
        .sort((a, b) => a.e1RM - b.e1RM);

      const max1RM = Math.max(...history.map((h) => h.e1RM));
      const bwRatio = Number((max1RM / 80).toFixed(2));
      const tier =
        bwRatio >= 2.0
          ? 'Elite'
          : bwRatio >= 1.5
            ? 'Athlet'
            : bwRatio >= 1.1
              ? 'Fortgeschritten'
              : 'Anfänger';
      const tierColor =
        tier === 'Elite'
          ? '#10b981'
          : tier === 'Athlet'
            ? '#0284c7'
            : tier === 'Fortgeschritten'
              ? '#eab308'
              : '#94a3b8';

      profiles.push({
        id: ex.id,
        name: ex.name,
        e1RM: max1RM,
        bwRatio,
        tier,
        tierColor,
        history
      });
    }

    return profiles;
  });

  const profiles = $derived(oneRmQuery.value ?? []);
  let selectedId = $state<string | null>(null);

  $effect(() => {
    if (profiles.length > 0 && (!selectedId || !profiles.find((p) => p.id === selectedId))) {
      selectedId = profiles[0].id;
    }
  });

  const selectedProfile = $derived(
    profiles.find((p) => p.id === selectedId) ?? profiles[0] ?? null
  );
</script>

<div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
  <!-- Header with Exercise Pills -->
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <div class="flex items-center gap-1.5 text-sm font-extrabold text-text-main">
        <Icon name="fitness_center" class="text-activity" />
        <span>1RM Maximalkraft-Entwicklung und Relativkraft</span>
      </div>
      <p class="mt-0.5 text-xs text-text-muted">
        Berechnet nach Brzycki &amp; Epley aus deinen absolvierten Trainingssätzen
      </p>
    </div>

    <!-- Exercise Selector Pills -->
    {#if profiles.length > 0}
      <div class="no-scrollbar flex gap-1.5 overflow-x-auto">
        {#each profiles as p}
          <button
            type="button"
            onclick={() => (selectedId = p.id)}
            class="cursor-pointer rounded-xl px-3 py-1 text-xs font-bold whitespace-nowrap transition-all {selectedId ===
            p.id
              ? 'bg-primary text-white shadow-xs'
              : 'border border-border-subtle bg-surface-50 text-text-muted hover:text-text-main'}"
          >
            {p.name}
          </button>
        {/each}
      </div>
    {/if}
  </div>

  {#if profiles.length === 0 || !selectedProfile}
    <div class="space-y-2 py-8 text-center text-xs text-text-muted">
      <Icon name="fitness_center" size="lg" class="mx-auto text-text-muted opacity-60" />
      <p class="text-xs font-bold text-text-main">Keine 1RM-Historie vorhanden</p>
      <p class="mx-auto max-w-sm text-[0.6875rem]">
        Sobald du Sätze mit Gewichten und Wiederholungen protokollierst, werden hier deine
        Kraftkurven und IPF-Einstufungen visualisiert.
      </p>
    </div>
  {:else}
    <!-- Main Score Cards -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <!-- 1RM Max -->
      <div
        class="flex items-center justify-between rounded-2xl border border-border-subtle bg-surface-50 p-3.5"
      >
        <div>
          <span class="block text-[0.6875rem] font-bold text-text-muted uppercase"
            >Geschätztes 1RM</span
          >
          <span class="text-2xl font-extrabold text-activity tabular-nums">
            {selectedProfile.e1RM} kg
          </span>
        </div>
        <Badge variant="success" class="text-[0.625rem]">Aktiver Rekord</Badge>
      </div>

      <!-- Relative Strength Ratio -->
      <div
        class="flex items-center justify-between rounded-2xl border border-border-subtle bg-surface-50 p-3.5"
      >
        <div>
          <span class="block text-[0.6875rem] font-bold text-text-muted uppercase"
            >Relativkraft-Koeffizient</span
          >
          <span class="text-2xl font-extrabold text-primary tabular-nums">
            {selectedProfile.bwRatio.toFixed(2)}&times;
          </span>
        </div>
        <span class="text-xs font-bold text-text-muted">des Körpergewichts</span>
      </div>

      <!-- Strength Tier -->
      <div
        class="flex items-center justify-between rounded-2xl border border-border-subtle bg-surface-50 p-3.5"
      >
        <div>
          <span class="block text-[0.6875rem] font-bold text-text-muted uppercase"
            >IPF / Wilks Einstufung</span
          >
          <span
            class="block text-xl font-extrabold text-text-main"
            style="color: {selectedProfile.tierColor};"
          >
            {selectedProfile.tier}
          </span>
        </div>
        <Badge variant="default" class="text-xs font-bold">{selectedProfile.tier}</Badge>
      </div>
    </div>
  {/if}
</div>
