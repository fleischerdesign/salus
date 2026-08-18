<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import type { MuscleGroup } from '../../types/workouts';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  interface MuscleVolumeData {
    name: MuscleGroup;
    setsWeekly: number;
    volumeKg: number;
    recoveryHoursLeft: number;
    status: 'optimal' | 'low' | 'overreaching' | 'none';
    statusText: string;
    exercises: string[];
    color: string;
  }

  const allMuscles: MuscleGroup[] = [
    'Brust',
    'Rücken',
    'Schultern',
    'Trizeps',
    'Bizeps',
    'Quadrizeps',
    'Hamstrings',
    'Waden',
    'Bauch',
    'Gesäß'
  ];

  const muscleHeatmapQuery = useQuery(async () => {
    const [exercises, logs] = await Promise.all([
      db.exercise.toArray(),
      db.workout_log_entry.toArray()
    ]);

    const validExercises = exercises.filter((e) => !e.deleted_at);
    const validLogs = logs.filter((l) => !l.deleted_at);
    const exMap = new Map(validExercises.map((e) => [e.id, e]));

    const muscleSets = new Map<string, { sets: number; volume: number; exNames: Set<string> }>();
    for (const m of allMuscles) {
      muscleSets.set(m, { sets: 0, volume: 0, exNames: new Set() });
    }

    for (const log of validLogs) {
      const ex = exMap.get(log.exercise_id);
      if (!ex) continue;
      const targetMuscle = (ex.primary_muscles as MuscleGroup) || 'Brust';
      const current = muscleSets.get(targetMuscle) ?? { sets: 0, volume: 0, exNames: new Set() };
      current.sets += 1;
      current.volume += log.weight * log.reps;
      current.exNames.add(ex.name);
      muscleSets.set(targetMuscle, current);
    }

    const result: Record<string, MuscleVolumeData> = {};
    for (const m of allMuscles) {
      const data = muscleSets.get(m)!;
      const s = data.sets;
      const status: MuscleVolumeData['status'] =
        s >= 10 && s <= 18 ? 'optimal' : s > 18 ? 'overreaching' : s > 0 ? 'low' : 'none';
      const statusText =
        status === 'optimal'
          ? 'MAV (Optimaler Wachstumsreiz: 10–18 Sätze)'
          : status === 'overreaching'
            ? 'MRV (Hohe Belastung: >18 Sätze)'
            : status === 'low'
              ? 'MEV (Erhaltungsvolumen: <10 Sätze)'
              : 'Keine Sätze in den letzten 7 Tagen';

      const color =
        status === 'optimal'
          ? '#10b981'
          : status === 'overreaching'
            ? '#ef4444'
            : status === 'low'
              ? '#0284c7'
              : 'var(--bg-surface-100)';

      result[m] = {
        name: m,
        setsWeekly: s,
        volumeKg: data.volume,
        recoveryHoursLeft: s > 0 ? 24 : 0,
        status,
        statusText,
        exercises: Array.from(data.exNames),
        color
      };
    }

    return result;
  });

  const muscleData = $derived(muscleHeatmapQuery.value ?? {});
  let selectedMuscleKey = $state<MuscleGroup>('Brust');
  let selected = $derived(
    muscleData[selectedMuscleKey] ?? {
      name: selectedMuscleKey,
      setsWeekly: 0,
      volumeKg: 0,
      recoveryHoursLeft: 0,
      status: 'none',
      statusText: 'Keine Sätze in den letzten 7 Tagen',
      exercises: [],
      color: 'var(--bg-surface-100)'
    }
  );
</script>

<div
  class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
>
  <!-- Header with Legend -->
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div>
      <div class="flex items-center gap-1.5 text-sm font-extrabold text-[var(--text-main)]">
        <Icon name="fitness_center" class="text-[var(--color-activity)]" />
        <span>7-Tage Muskel-Volumen und Regeneration</span>
      </div>
      <p class="mt-0.5 text-xs text-[var(--text-muted)]">
        Wissenschaftliche MEV/MAV/MRV Hypertrophie-Zonen
      </p>
    </div>

    <!-- Volume Legend -->
    <div class="flex items-center gap-2 text-[0.625rem] font-bold">
      <span class="flex items-center gap-1"
        ><span class="h-2 w-2 rounded-full bg-[#0284c7]"></span> MEV (&lt;10 Sätze)</span
      >
      <span class="flex items-center gap-1"
        ><span class="h-2 w-2 rounded-full bg-[#10b981]"></span> MAV (Optimal 10–18)</span
      >
      <span class="flex items-center gap-1"
        ><span class="h-2 w-2 rounded-full bg-[#ef4444]"></span> MRV (&gt;20 Sätze)</span
      >
    </div>
  </div>

  <!-- Dual Silhouette Graphic: Anterior (Vorderseite) & Posterior (Rückseite) -->
  <div
    class="flex flex-col items-center justify-around gap-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 sm:flex-row"
  >
    <!-- 1. ANTERIOR (VORDERSEITE) -->
    <div class="flex flex-col items-center">
      <span class="mb-1 text-[0.6875rem] font-extrabold text-[var(--text-muted)] uppercase"
        >Vorderseite (Anterior)</span
      >
      <svg width="130" height="230" viewBox="0 0 130 230" class="select-none">
        <!-- Head -->
        <circle
          cx="65"
          cy="22"
          r="14"
          fill="var(--bg-surface-100)"
          stroke="var(--border-subtle)"
          stroke-width="1.5"
        />
        <!-- Neck -->
        <rect x="60" y="34" width="10" height="8" fill="var(--bg-surface-100)" />

        <!-- Chest (Pectoralis) -->
        <g
          role="button"
          tabindex="0"
          onclick={() => (selectedMuscleKey = 'Brust')}
          onkeydown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Brust';
          }}
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <path
            d="M 46 45 Q 65 52 84 45 L 86 68 Q 65 76 44 68 Z"
            fill={muscleData['Brust']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Brust' ? '#ffffff' : 'none'}
            stroke-width="2"
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
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <circle
            cx="36"
            cy="50"
            r="9"
            fill={muscleData['Schultern']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Schultern' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
          <circle
            cx="94"
            cy="50"
            r="9"
            fill={muscleData['Schultern']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Schultern' ? '#ffffff' : 'none'}
            stroke-width="2"
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
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <rect
            x="25"
            y="62"
            width="10"
            height="26"
            rx="4"
            fill={muscleData['Bizeps']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Bizeps' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
          <rect
            x="95"
            y="62"
            width="10"
            height="26"
            rx="4"
            fill={muscleData['Bizeps']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Bizeps' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
        </g>

        <!-- Forearms -->
        <rect x="22" y="91" width="9" height="30" rx="3" fill="var(--bg-surface-100)" />
        <rect x="99" y="91" width="9" height="30" rx="3" fill="var(--bg-surface-100)" />

        <!-- Abs (Rectus Abdominis) -->
        <g
          role="button"
          tabindex="0"
          onclick={() => (selectedMuscleKey = 'Bauch')}
          onkeydown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Bauch';
          }}
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <rect
            x="52"
            y="72"
            width="26"
            height="38"
            rx="4"
            fill={muscleData['Bauch']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Bauch' ? '#ffffff' : 'none'}
            stroke-width="2"
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
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <rect
            x="42"
            y="115"
            width="20"
            height="52"
            rx="6"
            fill={muscleData['Quadrizeps']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Quadrizeps' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
          <rect
            x="68"
            y="115"
            width="20"
            height="52"
            rx="6"
            fill={muscleData['Quadrizeps']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Quadrizeps' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
        </g>

        <!-- Calves Anterior -->
        <g
          role="button"
          tabindex="0"
          onclick={() => (selectedMuscleKey = 'Waden')}
          onkeydown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Waden';
          }}
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <rect
            x="44"
            y="174"
            width="16"
            height="42"
            rx="5"
            fill={muscleData['Waden']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Waden' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
          <rect
            x="70"
            y="174"
            width="16"
            height="42"
            rx="5"
            fill={muscleData['Waden']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Waden' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
        </g>
      </svg>
    </div>

    <!-- 2. POSTERIOR (RÜCKSEITE) -->
    <div class="flex flex-col items-center">
      <span class="mb-1 text-[0.6875rem] font-extrabold text-[var(--text-muted)] uppercase"
        >Rückseite (Posterior)</span
      >
      <svg width="130" height="230" viewBox="0 0 130 230" class="select-none">
        <!-- Head -->
        <circle
          cx="65"
          cy="22"
          r="14"
          fill="var(--bg-surface-100)"
          stroke="var(--border-subtle)"
          stroke-width="1.5"
        />
        <!-- Traps & Upper Back -->
        <g
          role="button"
          tabindex="0"
          onclick={() => (selectedMuscleKey = 'Rücken')}
          onkeydown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Rücken';
          }}
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <path
            d="M 44 42 Q 65 36 86 42 L 82 78 Q 65 85 48 78 Z"
            fill={muscleData['Rücken']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Rücken' ? '#ffffff' : 'none'}
            stroke-width="2"
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
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <rect
            x="25"
            y="60"
            width="10"
            height="28"
            rx="4"
            fill={muscleData['Trizeps']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Trizeps' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
          <rect
            x="95"
            y="60"
            width="10"
            height="28"
            rx="4"
            fill={muscleData['Trizeps']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Trizeps' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
        </g>

        <!-- Glutes -->
        <g
          role="button"
          tabindex="0"
          onclick={() => (selectedMuscleKey = 'Gesäß')}
          onkeydown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Gesäß';
          }}
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <rect
            x="42"
            y="86"
            width="46"
            height="26"
            rx="6"
            fill={muscleData['Gesäß']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Gesäß' ? '#ffffff' : 'none'}
            stroke-width="2"
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
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <rect
            x="42"
            y="115"
            width="20"
            height="52"
            rx="6"
            fill={muscleData['Hamstrings']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Hamstrings' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
          <rect
            x="68"
            y="115"
            width="20"
            height="52"
            rx="6"
            fill={muscleData['Hamstrings']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Hamstrings' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
        </g>

        <!-- Calves Posterior -->
        <g
          role="button"
          tabindex="0"
          onclick={() => (selectedMuscleKey = 'Waden')}
          onkeydown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Waden';
          }}
          class="cursor-pointer transition-all hover:opacity-80"
        >
          <rect
            x="44"
            y="174"
            width="16"
            height="42"
            rx="5"
            fill={muscleData['Waden']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Waden' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
          <rect
            x="70"
            y="174"
            width="16"
            height="42"
            rx="5"
            fill={muscleData['Waden']?.color || 'var(--bg-surface-100)'}
            stroke={selectedMuscleKey === 'Waden' ? '#ffffff' : 'none'}
            stroke-width="2"
          />
        </g>
      </svg>
    </div>
  </div>

  <!-- Detail Muscle Card for Currently Selected Muscle -->
  <div
    class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="h-3 w-3 rounded-full" style="background-color: {selected.color};"></span>
        <h3 class="text-sm font-extrabold text-[var(--text-main)]">{selected.name}</h3>
      </div>
      <Badge variant="default" class="font-bold">{selected.setsWeekly} Sätze diese Woche</Badge>
    </div>

    <div class="text-xs font-semibold text-[var(--text-muted)]">
      {selected.statusText}
    </div>
  </div>
</div>
