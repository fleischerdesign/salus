<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import type { MuscleGroup } from '../../types/workouts';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  interface MuscleVolumeData {
    name: MuscleGroup;
    category: 'push' | 'pull' | 'legs' | 'core';
    setsWeekly: number;
    volumeKg: number;
    recoveryHoursLeft: number;
    status: 'optimal' | 'low' | 'overreaching' | 'none';
    statusLabel: string;
    exercises: string[];
    color: string;
  }

  const muscleConfigs: Array<{
    name: MuscleGroup;
    category: 'push' | 'pull' | 'legs' | 'core';
    icon: string;
  }> = [
    { name: 'Brust', category: 'push', icon: 'fitness_center' },
    { name: 'Schultern', category: 'push', icon: 'accessibility' },
    { name: 'Trizeps', category: 'push', icon: 'sports_gymnastics' },
    { name: 'Rücken', category: 'pull', icon: 'rowing' },
    { name: 'Bizeps', category: 'pull', icon: 'sports_martial_arts' },
    { name: 'Quadrizeps', category: 'legs', icon: 'directions_run' },
    { name: 'Hamstrings', category: 'legs', icon: 'directions_walk' },
    { name: 'Waden', category: 'legs', icon: 'speed' },
    { name: 'Gesäß', category: 'legs', icon: 'airline_seat_recline_extra' },
    { name: 'Bauch', category: 'core', icon: 'self_improvement' }
  ];

  // Mode: 'visual' (Anatomical 2D Body) vs 'list' (Hypertrophy Matrix)
  let activeDisplayMode = $state<'visual' | 'list'>('visual');
  let bodySide = $state<'anterior' | 'posterior'>('anterior');
  let selectedCategory = $state<'all' | 'push' | 'pull' | 'legs' | 'core'>('all');
  let selectedMuscleKey = $state<MuscleGroup>('Brust');

  const volumeQuery = useQuery(async () => {
    const [exercises, logs] = await Promise.all([
      db.exercise.toArray(),
      db.workout_log_entry.toArray()
    ]);

    const validExercises = exercises.filter((e) => !e.deleted_at);
    const validLogs = logs.filter((l) => !l.deleted_at);
    const exMap = new Map(validExercises.map((e) => [e.id, e]));

    const muscleMap = new Map<string, { sets: number; volume: number; exNames: Set<string> }>();
    for (const conf of muscleConfigs) {
      muscleMap.set(conf.name, { sets: 0, volume: 0, exNames: new Set() });
    }

    for (const log of validLogs) {
      const ex = exMap.get(log.exercise_id);
      if (!ex) continue;
      const targetMuscle = (ex.primary_muscles as MuscleGroup) || 'Brust';
      const current = muscleMap.get(targetMuscle) ?? { sets: 0, volume: 0, exNames: new Set() };
      current.sets += 1;
      current.volume += (log.weight || 0) * (log.reps || 0);
      current.exNames.add(ex.name);
      muscleMap.set(targetMuscle, current);
    }

    const map: Record<string, MuscleVolumeData> = {};
    for (const conf of muscleConfigs) {
      const data = muscleMap.get(conf.name)!;
      const s = data.sets;
      const status: MuscleVolumeData['status'] =
        s >= 10 && s <= 18 ? 'optimal' : s > 18 ? 'overreaching' : s > 0 ? 'low' : 'none';
      const statusLabel =
        status === 'optimal'
          ? 'MAV (Optimal)'
          : status === 'overreaching'
            ? 'MRV (Hoch)'
            : status === 'low'
              ? 'MEV (Erhalt)'
              : 'Keine Sätze';

      const color =
        status === 'optimal'
          ? '#10b981'
          : status === 'overreaching'
            ? '#f43f5e'
            : status === 'low'
              ? '#0ea5e9'
              : 'var(--bg-surface-200)';

      map[conf.name] = {
        name: conf.name,
        category: conf.category,
        setsWeekly: s,
        volumeKg: data.volume,
        recoveryHoursLeft: s > 0 ? (s > 14 ? 18 : 8) : 0,
        status,
        statusLabel,
        exercises: Array.from(data.exNames),
        color
      };
    }

    return map;
  });

  const muscleMap = $derived(volumeQuery.value ?? {});
  const muscleList = $derived(Object.values(muscleMap));

  const filteredMuscles = $derived(
    muscleList.filter((m) => selectedCategory === 'all' || m.category === selectedCategory)
  );

  const selected = $derived(
    muscleMap[selectedMuscleKey] ?? {
      name: selectedMuscleKey,
      category: 'push',
      setsWeekly: 0,
      volumeKg: 0,
      recoveryHoursLeft: 0,
      status: 'none',
      statusLabel: 'Keine Sätze',
      exercises: [],
      color: 'var(--bg-surface-200)'
    }
  );

  const totalWeeklySets = $derived(muscleList.reduce((acc, m) => acc + m.setsWeekly, 0));
  const totalVolumeKg = $derived(muscleList.reduce((acc, m) => acc + m.volumeKg, 0));

  function getMuscleColor(muscle: MuscleGroup): string {
    return muscleMap[muscle]?.color || 'var(--bg-surface-200)';
  }

  function isMuscleActive(muscle: MuscleGroup): boolean {
    return selectedMuscleKey === muscle;
  }
</script>

<div
  class="flex h-full flex-col justify-between rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
>
  <div>
    <!-- Card Header -->
    <div class="flex items-start justify-between gap-2 border-b border-[var(--border-subtle)] pb-3">
      <div>
        <div class="flex items-center gap-1.5 text-sm font-extrabold text-[var(--text-main)]">
          <Icon name="fitness_center" class="text-[var(--color-activity)]" />
          <span>7-Tage Muskel-Volumen</span>
        </div>
        <p class="mt-0.5 text-xs text-[var(--text-muted)]">Hypertrophie-Zonen &amp; Regeneration</p>
      </div>

      <!-- Mode Switcher (Visual vs List) -->
      <div
        class="flex gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-1"
      >
        <button
          type="button"
          onclick={() => (activeDisplayMode = 'visual')}
          class="flex cursor-pointer items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-bold transition-all {activeDisplayMode ===
          'visual'
            ? 'bg-[var(--color-primary)] text-white shadow-xs'
            : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
          title="Anatomischer 2D Körper"
        >
          <Icon name="accessibility" size="sm" />
          <span>Körper</span>
        </button>
        <button
          type="button"
          onclick={() => (activeDisplayMode = 'list')}
          class="flex cursor-pointer items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-bold transition-all {activeDisplayMode ===
          'list'
            ? 'bg-[var(--color-primary)] text-white shadow-xs'
            : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
          title="Listen-Matrix"
        >
          <Icon name="list" size="sm" />
          <span>Matrix</span>
        </button>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- VIEW A: ANATOMICAL PROPORTIONED 2D BODY VIEW                -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if activeDisplayMode === 'visual'}
      <div class="my-3 space-y-3">
        <!-- Anterior / Posterior Toggle -->
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-[var(--text-muted)]">
            Ansicht: <strong class="text-[var(--text-main)]"
              >{bodySide === 'anterior'
                ? 'Vorderseite (Anterior)'
                : 'Rückseite (Posterior)'}</strong
            >
          </span>
          <div
            class="flex gap-1 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-0.5 text-xs font-bold"
          >
            <button
              type="button"
              onclick={() => (bodySide = 'anterior')}
              class="cursor-pointer rounded-md px-2 py-0.5 transition-all {bodySide === 'anterior'
                ? 'bg-[var(--bg-surface-0)] text-[var(--text-main)] shadow-xs'
                : 'text-[var(--text-muted)]'}"
            >
              Vorne
            </button>
            <button
              type="button"
              onclick={() => (bodySide = 'posterior')}
              class="cursor-pointer rounded-md px-2 py-0.5 transition-all {bodySide === 'posterior'
                ? 'bg-[var(--bg-surface-0)] text-[var(--text-main)] shadow-xs'
                : 'text-[var(--text-muted)]'}"
            >
              Hinten
            </button>
          </div>
        </div>

        <!-- Proportioned SVG Canvas -->
        <div
          class="relative flex h-[240px] w-full items-center justify-center overflow-hidden rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2 shadow-inner"
        >
          <svg
            viewBox="0 0 200 360"
            class="h-full max-h-[230px] w-auto overflow-visible select-none"
          >
            <defs>
              <filter id="activeGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow
                  dx="0"
                  dy="0"
                  stdDeviation="3.5"
                  flood-color="var(--color-primary)"
                  flood-opacity="0.9"
                />
              </filter>
            </defs>

            {#if bodySide === 'anterior'}
              <!-- ─── ANTERIOR (VORDERSEITE) ─── -->
              <!-- Head & Neck -->
              <ellipse
                cx="100"
                cy="22"
                rx="13"
                ry="16"
                fill="var(--bg-surface-200)"
                stroke="var(--border-subtle)"
                stroke-width="1.5"
              />
              <rect x="94" y="37" width="12" height="14" fill="var(--bg-surface-200)" />

              <!-- Chest (Pectoralis Major) -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Brust')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Brust';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Brust') ? 'url(#activeGlow)' : undefined}
              >
                <!-- Left Pec -->
                <path
                  d="M 68 62 C 84 62, 98 64, 98 88 C 86 96, 66 94, 60 86 C 58 74, 62 64, 68 62 Z"
                  fill={getMuscleColor('Brust')}
                  stroke={isMuscleActive('Brust') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Brust') ? '2.5' : '1'}
                />
                <!-- Right Pec -->
                <path
                  d="M 132 62 C 116 62, 102 64, 102 88 C 114 96, 134 94, 140 86 C 142 74, 138 64, 132 62 Z"
                  fill={getMuscleColor('Brust')}
                  stroke={isMuscleActive('Brust') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Brust') ? '2.5' : '1'}
                />
              </g>

              <!-- Shoulders (Anterior Deltoids) -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Schultern')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Schultern';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Schultern') ? 'url(#activeGlow)' : undefined}
              >
                <!-- Left Deltoid -->
                <path
                  d="M 66 56 C 48 60, 46 76, 54 88 C 60 88, 64 78, 66 66 Z"
                  fill={getMuscleColor('Schultern')}
                  stroke={isMuscleActive('Schultern') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Schultern') ? '2.5' : '1'}
                />
                <!-- Right Deltoid -->
                <path
                  d="M 134 56 C 152 60, 154 76, 146 88 C 140 88, 136 78, 134 66 Z"
                  fill={getMuscleColor('Schultern')}
                  stroke={isMuscleActive('Schultern') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Schultern') ? '2.5' : '1'}
                />
              </g>

              <!-- Biceps -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Bizeps')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Bizeps';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Bizeps') ? 'url(#activeGlow)' : undefined}
              >
                <path
                  d="M 54 88 C 44 96, 46 116, 54 122 C 60 122, 62 108, 60 88 Z"
                  fill={getMuscleColor('Bizeps')}
                  stroke={isMuscleActive('Bizeps') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Bizeps') ? '2.5' : '1'}
                />
                <path
                  d="M 146 88 C 156 96, 154 116, 146 122 C 140 122, 138 108, 140 88 Z"
                  fill={getMuscleColor('Bizeps')}
                  stroke={isMuscleActive('Bizeps') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Bizeps') ? '2.5' : '1'}
                />
              </g>

              <!-- Forearms -->
              <path
                d="M 52 124 C 42 136, 44 156, 48 168 C 54 168, 60 152, 58 124 Z"
                fill="var(--bg-surface-200)"
              />
              <path
                d="M 148 124 C 158 136, 156 156, 152 168 C 146 168, 140 152, 142 124 Z"
                fill="var(--bg-surface-200)"
              />

              <!-- Hands -->
              <ellipse cx="48" cy="176" rx="4" ry="7" fill="var(--bg-surface-200)" />
              <ellipse cx="152" cy="176" rx="4" ry="7" fill="var(--bg-surface-200)" />

              <!-- Abs & Obliques (Core) -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Bauch')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Bauch';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Bauch') ? 'url(#activeGlow)' : undefined}
              >
                <!-- 6-Pack Grid -->
                <rect
                  x="84"
                  y="94"
                  width="13"
                  height="12"
                  rx="2"
                  fill={getMuscleColor('Bauch')}
                  stroke={isMuscleActive('Bauch') ? '#fff' : 'none'}
                  stroke-width="1.5"
                />
                <rect
                  x="103"
                  y="94"
                  width="13"
                  height="12"
                  rx="2"
                  fill={getMuscleColor('Bauch')}
                  stroke={isMuscleActive('Bauch') ? '#fff' : 'none'}
                  stroke-width="1.5"
                />
                <rect
                  x="84"
                  y="110"
                  width="13"
                  height="12"
                  rx="2"
                  fill={getMuscleColor('Bauch')}
                  stroke={isMuscleActive('Bauch') ? '#fff' : 'none'}
                  stroke-width="1.5"
                />
                <rect
                  x="103"
                  y="110"
                  width="13"
                  height="12"
                  rx="2"
                  fill={getMuscleColor('Bauch')}
                  stroke={isMuscleActive('Bauch') ? '#fff' : 'none'}
                  stroke-width="1.5"
                />
                <rect
                  x="85"
                  y="126"
                  width="12"
                  height="14"
                  rx="2"
                  fill={getMuscleColor('Bauch')}
                  stroke={isMuscleActive('Bauch') ? '#fff' : 'none'}
                  stroke-width="1.5"
                />
                <rect
                  x="103"
                  y="126"
                  width="12"
                  height="14"
                  rx="2"
                  fill={getMuscleColor('Bauch')}
                  stroke={isMuscleActive('Bauch') ? '#fff' : 'none'}
                  stroke-width="1.5"
                />
                <!-- Obliques -->
                <path
                  d="M 68 96 C 78 96, 78 138, 70 144 Z"
                  fill={getMuscleColor('Bauch')}
                  opacity="0.8"
                />
                <path
                  d="M 132 96 C 122 96, 122 138, 130 144 Z"
                  fill={getMuscleColor('Bauch')}
                  opacity="0.8"
                />
              </g>

              <!-- Quads (Quadriceps) -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Quadrizeps')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Quadrizeps';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Quadrizeps') ? 'url(#activeGlow)' : undefined}
              >
                <!-- Left Quad -->
                <path
                  d="M 66 156 C 94 156, 94 204, 88 238 C 76 242, 60 236, 56 206 C 54 178, 60 158, 66 156 Z"
                  fill={getMuscleColor('Quadrizeps')}
                  stroke={isMuscleActive('Quadrizeps') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Quadrizeps') ? '2.5' : '1'}
                />
                <!-- Right Quad -->
                <path
                  d="M 134 156 C 106 156, 106 204, 112 238 C 124 242, 140 236, 144 206 C 146 178, 140 158, 134 156 Z"
                  fill={getMuscleColor('Quadrizeps')}
                  stroke={isMuscleActive('Quadrizeps') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Quadrizeps') ? '2.5' : '1'}
                />
              </g>

              <!-- Knees -->
              <circle cx="76" cy="246" r="5" fill="var(--bg-surface-200)" />
              <circle cx="124" cy="246" r="5" fill="var(--bg-surface-200)" />

              <!-- Calves (Anterior) -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Waden')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Waden';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Waden') ? 'url(#activeGlow)' : undefined}
              >
                <!-- Left Calf -->
                <path
                  d="M 68 254 C 54 270, 58 306, 68 328 C 76 328, 80 304, 78 254 Z"
                  fill={getMuscleColor('Waden')}
                  stroke={isMuscleActive('Waden') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Waden') ? '2.5' : '1'}
                />
                <!-- Right Calf -->
                <path
                  d="M 132 254 C 146 270, 142 306, 132 328 C 124 328, 120 304, 122 254 Z"
                  fill={getMuscleColor('Waden')}
                  stroke={isMuscleActive('Waden') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Waden') ? '2.5' : '1'}
                />
              </g>

              <!-- Feet -->
              <path d="M 64 330 L 56 348 L 74 348 L 74 330 Z" fill="var(--bg-surface-200)" />
              <path d="M 136 330 L 144 348 L 126 348 L 126 330 Z" fill="var(--bg-surface-200)" />
            {:else}
              <!-- ─── POSTERIOR (RÜCKSEITE) ─── -->
              <!-- Head & Neck -->
              <ellipse
                cx="100"
                cy="22"
                rx="13"
                ry="16"
                fill="var(--bg-surface-200)"
                stroke="var(--border-subtle)"
                stroke-width="1.5"
              />
              <rect x="94" y="37" width="12" height="14" fill="var(--bg-surface-200)" />

              <!-- Upper & Mid Back (Trapezius, Rhomboids, Lats) -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Rücken')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Rücken';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Rücken') ? 'url(#activeGlow)' : undefined}
              >
                <!-- Trapezius Diamond -->
                <path
                  d="M 94 40 L 106 40 L 134 58 L 100 108 L 66 58 Z"
                  fill={getMuscleColor('Rücken')}
                  stroke={isMuscleActive('Rücken') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Rücken') ? '2.5' : '1'}
                />
                <!-- Left Latissimus Wing -->
                <path
                  d="M 66 68 C 50 86, 54 122, 80 128 C 86 124, 90 110, 84 96 Z"
                  fill={getMuscleColor('Rücken')}
                  stroke={isMuscleActive('Rücken') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Rücken') ? '2.5' : '1'}
                />
                <!-- Right Latissimus Wing -->
                <path
                  d="M 134 68 C 150 86, 146 122, 120 128 C 114 124, 110 110, 116 96 Z"
                  fill={getMuscleColor('Rücken')}
                  stroke={isMuscleActive('Rücken') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Rücken') ? '2.5' : '1'}
                />
                <!-- Lower Back (Erector Spinae) -->
                <path
                  d="M 86 118 C 100 120, 114 118, 112 148 C 100 150, 88 148, 88 118 Z"
                  fill={getMuscleColor('Rücken')}
                  stroke={isMuscleActive('Rücken') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Rücken') ? '2.5' : '1'}
                />
              </g>

              <!-- Rear Deltoids -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Schultern')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Schultern';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Schultern') ? 'url(#activeGlow)' : undefined}
              >
                <path
                  d="M 66 56 C 48 60, 46 76, 54 88 C 60 88, 64 78, 66 66 Z"
                  fill={getMuscleColor('Schultern')}
                  stroke={isMuscleActive('Schultern') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Schultern') ? '2.5' : '1'}
                />
                <path
                  d="M 134 56 C 152 60, 154 76, 146 88 C 140 88, 136 78, 134 66 Z"
                  fill={getMuscleColor('Schultern')}
                  stroke={isMuscleActive('Schultern') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Schultern') ? '2.5' : '1'}
                />
              </g>

              <!-- Triceps -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Trizeps')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Trizeps';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Trizeps') ? 'url(#activeGlow)' : undefined}
              >
                <path
                  d="M 54 68 C 44 76, 46 114, 56 122 C 64 122, 66 98, 64 68 Z"
                  fill={getMuscleColor('Trizeps')}
                  stroke={isMuscleActive('Trizeps') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Trizeps') ? '2.5' : '1'}
                />
                <path
                  d="M 146 68 C 156 76, 154 114, 144 122 C 136 122, 134 98, 136 68 Z"
                  fill={getMuscleColor('Trizeps')}
                  stroke={isMuscleActive('Trizeps') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Trizeps') ? '2.5' : '1'}
                />
              </g>

              <!-- Glutes (Gluteus Maximus) -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Gesäß')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Gesäß';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Gesäß') ? 'url(#activeGlow)' : undefined}
              >
                <!-- Left Glute -->
                <path
                  d="M 68 150 C 98 148, 98 184, 88 194 C 72 198, 58 186, 60 164 Z"
                  fill={getMuscleColor('Gesäß')}
                  stroke={isMuscleActive('Gesäß') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Gesäß') ? '2.5' : '1'}
                />
                <!-- Right Glute -->
                <path
                  d="M 132 150 C 102 148, 102 184, 112 194 C 128 198, 142 186, 140 164 Z"
                  fill={getMuscleColor('Gesäß')}
                  stroke={isMuscleActive('Gesäß') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Gesäß') ? '2.5' : '1'}
                />
              </g>

              <!-- Hamstrings -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Hamstrings')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Hamstrings';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Hamstrings') ? 'url(#activeGlow)' : undefined}
              >
                <!-- Left Hamstring -->
                <path
                  d="M 62 196 C 92 196, 90 234, 86 242 C 74 244, 60 238, 58 212 Z"
                  fill={getMuscleColor('Hamstrings')}
                  stroke={isMuscleActive('Hamstrings') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Hamstrings') ? '2.5' : '1'}
                />
                <!-- Right Hamstring -->
                <path
                  d="M 138 196 C 108 196, 110 234, 114 242 C 126 244, 140 238, 142 212 Z"
                  fill={getMuscleColor('Hamstrings')}
                  stroke={isMuscleActive('Hamstrings') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Hamstrings') ? '2.5' : '1'}
                />
              </g>

              <!-- Calves (Posterior) -->
              <g
                role="button"
                tabindex="0"
                onclick={() => (selectedMuscleKey = 'Waden')}
                onkeydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Waden';
                }}
                class="cursor-pointer transition-all hover:opacity-90"
                filter={isMuscleActive('Waden') ? 'url(#activeGlow)' : undefined}
              >
                <path
                  d="M 68 252 C 52 268, 56 308, 68 328 C 76 328, 80 304, 78 252 Z"
                  fill={getMuscleColor('Waden')}
                  stroke={isMuscleActive('Waden') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Waden') ? '2.5' : '1'}
                />
                <path
                  d="M 132 252 C 148 268, 144 308, 132 328 C 124 328, 120 304, 122 252 Z"
                  fill={getMuscleColor('Waden')}
                  stroke={isMuscleActive('Waden') ? '#ffffff' : 'rgba(0,0,0,0.15)'}
                  stroke-width={isMuscleActive('Waden') ? '2.5' : '1'}
                />
              </g>

              <!-- Heels -->
              <path d="M 64 330 L 58 348 L 74 348 L 74 330 Z" fill="var(--bg-surface-200)" />
              <path d="M 136 330 L 142 348 L 126 348 L 126 330 Z" fill="var(--bg-surface-200)" />
            {/if}
          </svg>
        </div>

        <!-- Mini Selection Card -->
        <div class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3">
          <div class="flex items-center justify-between text-xs font-bold">
            <span class="text-[var(--text-main)]">{selected.name}</span>
            <Badge
              variant={selected.status === 'optimal'
                ? 'success'
                : selected.status === 'overreaching'
                  ? 'vital'
                  : selected.status === 'low'
                    ? 'primary'
                    : 'default'}
            >
              {selected.statusLabel}
            </Badge>
          </div>
          <div
            class="mt-1.5 flex items-center justify-between text-[0.6875rem] text-[var(--text-muted)]"
          >
            <span
              >{selected.setsWeekly} Sätze &bull; {selected.volumeKg.toLocaleString('de-DE')} kg</span
            >
            <span class="font-semibold text-emerald-500">
              {selected.recoveryHoursLeft > 0
                ? `~${selected.recoveryHoursLeft}h Regeneration`
                : '✓ Vollständig erholt'}
            </span>
          </div>
        </div>
      </div>
    {:else}
      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- VIEW B: HYPERTROPHY MATRIX LIST VIEW                        -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      <div class="my-3 space-y-2.5">
        <!-- Category Filter Pills -->
        <div class="no-scrollbar flex gap-1 overflow-x-auto">
          {#each [{ id: 'all', label: 'Alle' }, { id: 'push', label: 'Push' }, { id: 'pull', label: 'Pull' }, { id: 'legs', label: 'Beine' }, { id: 'core', label: 'Core' }] as const as tab}
            <button
              type="button"
              onclick={() => (selectedCategory = tab.id)}
              class="cursor-pointer rounded-lg px-2.5 py-1 text-[0.6875rem] font-bold whitespace-nowrap transition-all {selectedCategory ===
              tab.id
                ? 'bg-[var(--color-primary)] text-white shadow-xs'
                : 'border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
            >
              {tab.label}
            </button>
          {/each}
        </div>

        <!-- Muscle Volume Rows -->
        <div class="max-h-[280px] space-y-2 overflow-y-auto pr-1">
          {#each filteredMuscles as muscle (muscle.name)}
            <div
              class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5 transition-all hover:bg-[var(--bg-surface-100)]"
            >
              <div class="flex items-center justify-between text-xs">
                <span class="font-extrabold text-[var(--text-main)]">{muscle.name}</span>
                <div class="flex items-center gap-1.5">
                  <span class="font-mono font-bold text-[var(--text-main)] tabular-nums">
                    {muscle.setsWeekly}
                    <span class="text-[0.6875rem] font-normal text-[var(--text-muted)]">/ 18</span>
                  </span>
                  <Badge
                    variant={muscle.status === 'optimal'
                      ? 'success'
                      : muscle.status === 'overreaching'
                        ? 'vital'
                        : muscle.status === 'low'
                          ? 'primary'
                          : 'default'}
                  >
                    {muscle.statusLabel}
                  </Badge>
                </div>
              </div>

              <!-- Multi-Zone Progress Bar -->
              <div
                class="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-[var(--border-subtle)]/50"
              >
                <div
                  class="h-full rounded-full transition-all duration-500"
                  style="width: {Math.min(
                    100,
                    Math.max(0, (muscle.setsWeekly / 18) * 100)
                  )}%; background-color: {muscle.color};"
                ></div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>

  <!-- Legend Footer -->
  <div
    class="mt-2 flex items-center justify-between border-t border-[var(--border-subtle)] pt-2 text-[0.625rem] text-[var(--text-muted)]"
  >
    <span class="flex items-center gap-1">
      <span class="h-1.5 w-1.5 rounded-full bg-[#0ea5e9]"></span> MEV (&lt;10)
    </span>
    <span class="flex items-center gap-1">
      <span class="h-1.5 w-1.5 rounded-full bg-[#10b981]"></span> MAV (10–18)
    </span>
    <span class="flex items-center gap-1">
      <span class="h-1.5 w-1.5 rounded-full bg-[#f43f5e]"></span> MRV (&gt;18)
    </span>
    <span class="font-semibold text-[var(--text-main)] tabular-nums">
      {totalWeeklySets} Sätze &bull; {totalVolumeKg.toLocaleString('de-DE')} kg Last
    </span>
  </div>
</div>
