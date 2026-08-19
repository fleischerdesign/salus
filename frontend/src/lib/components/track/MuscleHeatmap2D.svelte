<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import AnatomicalBodyVector from './AnatomicalBodyVector.svelte';
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
    { name: 'Bauch', category: 'core', icon: 'self_improvement' },
    { name: 'Nacken', category: 'pull', icon: 'accessibility_new' },
    { name: 'Unterarme', category: 'pull', icon: 'pan_tool' }
  ];

  // Mode: 'visual' (Anatomical 2D Body) vs 'list' (Hypertrophy Matrix)
  let activeDisplayMode = $state<'visual' | 'list'>('visual');
  let bodySide = $state<'anterior' | 'posterior'>('anterior');
  let selectedCategory = $state<'all' | 'push' | 'pull' | 'legs' | 'core'>('all');
  let selectedMuscleGroup = $state<MuscleGroup>('Brust');

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

    const map: Partial<Record<MuscleGroup, MuscleVolumeData>> = {};
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
  const muscleList = $derived(Object.values(muscleMap) as MuscleVolumeData[]);

  const filteredMuscles = $derived(
    muscleList.filter((m) => selectedCategory === 'all' || m.category === selectedCategory)
  );

  const selected = $derived(
    muscleMap[selectedMuscleGroup] ?? {
      name: selectedMuscleGroup,
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

  const colorMap = $derived(
    Object.fromEntries(
      Object.entries(muscleMap).map(([k, v]) => [k, v?.color || 'var(--bg-surface-200)'])
    ) as Partial<Record<MuscleGroup, string>>
  );

  const totalWeeklySets = $derived(muscleList.reduce((acc, m) => acc + m.setsWeekly, 0));
  const totalVolumeKg = $derived(muscleList.reduce((acc, m) => acc + m.volumeKg, 0));

  function handleVectorSelect(group: MuscleGroup, _id: string) {
    selectedMuscleGroup = group;
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
        <p class="mt-0.5 text-xs text-[var(--text-muted)]">
          Evidenzbasierte Hypertrophie-Zonen &amp; Regeneration
        </p>
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

        <!-- Anatomical Body Vector Stage -->
        <div
          class="relative flex h-[240px] w-full items-center justify-center overflow-hidden rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2 shadow-inner"
        >
          <AnatomicalBodyVector
            view={bodySide}
            {colorMap}
            selectedGroup={selectedMuscleGroup}
            onselect={handleVectorSelect}
          />
        </div>

        <!-- Selected Muscle Detail Card -->
        <div class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3">
          <div class="flex items-center justify-between text-xs font-bold">
            <div class="flex items-center gap-1.5">
              <span
                class="h-2 w-2 rounded-full"
                style="background-color: {selected.color === 'var(--bg-surface-200)'
                  ? 'var(--text-muted)'
                  : selected.color};"
              ></span>
              <span class="text-[var(--text-main)]">{selected.name}</span>
            </div>
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
