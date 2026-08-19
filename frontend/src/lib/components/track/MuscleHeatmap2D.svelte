<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import AnatomicalBodyVector from './AnatomicalBodyVector.svelte';
  import {
    DETAILED_MUSCLES,
    DETAILED_MUSCLE_MAP,
    MUSCLE_GROUPS,
    parseMuscles,
    resolveMuscleGroup,
    type MuscleGroup,
    type DetailedMuscleKey
  } from '../../types/workouts';
  import { ANATOMICAL_PATH_TO_DETAILED_KEY } from './anatomy-data';
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

    // High-level muscle map (12 groups)
    const muscleMap = new Map<MuscleGroup, { sets: number; volume: number; exNames: Set<string> }>();
    for (const conf of muscleConfigs) {
      muscleMap.set(conf.name, { sets: 0, volume: 0, exNames: new Set() });
    }

    // Granular muscle map (28 detailed muscles)
    const detailedMap = new Map<DetailedMuscleKey, { sets: number; volume: number }>();
    for (const m of DETAILED_MUSCLES) {
      detailedMap.set(m.key, { sets: 0, volume: 0 });
    }

    for (const log of validLogs) {
      const ex = exMap.get(log.exercise_id);
      if (!ex) continue;

      const logVol = (log.weight || 0) * (log.reps || 0);

      // Primary muscles (1.0 volume credit)
      const primaryTokens = parseMuscles(ex.primary_muscles);
      for (const token of primaryTokens) {
        const pGroup = resolveMuscleGroup(token);
        const curGroup = muscleMap.get(pGroup) ?? { sets: 0, volume: 0, exNames: new Set() };
        curGroup.sets += 1.0;
        curGroup.volume += logVol;
        curGroup.exNames.add(ex.name);
        muscleMap.set(pGroup, curGroup);

        if (token in DETAILED_MUSCLE_MAP) {
          const curDet = detailedMap.get(token as DetailedMuscleKey) ?? { sets: 0, volume: 0 };
          curDet.sets += 1.0;
          curDet.volume += logVol;
          detailedMap.set(token as DetailedMuscleKey, curDet);
        }
      }

      // Secondary muscles (0.5 volume credit)
      const secondaryTokens = parseMuscles(ex.secondary_muscles);
      for (const token of secondaryTokens) {
        const sGroup = resolveMuscleGroup(token);
        const curGroup = muscleMap.get(sGroup) ?? { sets: 0, volume: 0, exNames: new Set() };
        curGroup.sets += 0.5;
        curGroup.volume += logVol * 0.5;
        curGroup.exNames.add(ex.name);
        muscleMap.set(sGroup, curGroup);

        if (token in DETAILED_MUSCLE_MAP) {
          const curDet = detailedMap.get(token as DetailedMuscleKey) ?? { sets: 0, volume: 0 };
          curDet.sets += 0.5;
          curDet.volume += logVol * 0.5;
          detailedMap.set(token as DetailedMuscleKey, curDet);
        }
      }
    }

    // Compute rolled-up Group stats
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

    // Compute granular SVG path colors
    const pathColorMap: Record<string, string> = {};
    for (const [key, dData] of detailedMap.entries()) {
      const def = DETAILED_MUSCLE_MAP[key];
      if (!def) continue;

      let pColor = 'var(--bg-surface-200)';
      if (dData.sets >= 6 && dData.sets <= 14) {
        pColor = '#10b981'; // Optimal
      } else if (dData.sets > 14) {
        pColor = '#f43f5e'; // Overreaching
      } else if (dData.sets > 0) {
        pColor = '#0ea5e9'; // Low
      }

      for (const pid of def.svgPathIds) {
        pathColorMap[pid] = pColor;
      }
    }

    return { groups: map, pathColorMap };
  });

  const muscleMap = $derived(volumeQuery.value?.groups ?? {});
  const pathColorMap = $derived(volumeQuery.value?.pathColorMap ?? {});
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

  function handleVectorSelect(group: MuscleGroup) {
    selectedMuscleGroup = group;
  }
</script>

<div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-4 shadow-sm">
  <!-- Card Header with Visual / List Mode Switch -->
  <div class="flex items-center justify-between border-b border-[var(--border-subtle)] pb-3">
    <div class="flex items-center gap-2">
      <div
        class="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--color-primary-soft)] text-[var(--color-primary)]"
      >
        <Icon name="accessibility_new" class="text-base" />
      </div>
      <div>
        <h3 class="text-sm font-bold text-[var(--text-main)]">Muskel-Heatmap & Belastung</h3>
        <p class="text-[0.6875rem] text-[var(--text-muted)]">
          Hypertrophie-Volumen der letzten 7 Tage
        </p>
      </div>
    </div>

    <!-- Toggle: 2D Visual vs Table List -->
    <div class="flex rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-100)] p-0.5">
      <button
        type="button"
        onclick={() => (activeDisplayMode = 'visual')}
        class="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-bold transition-all {activeDisplayMode ===
        'visual'
          ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-xs'
          : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        title="2D Anatomie-Ansicht"
      >
        <Icon name="person" class="text-xs" />
        <span class="hidden sm:inline">2D Body</span>
      </button>
      <button
        type="button"
        onclick={() => (activeDisplayMode = 'list')}
        class="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-bold transition-all {activeDisplayMode ===
        'list'
          ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-xs'
          : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        title="Matrix-Listenansicht"
      >
        <Icon name="view_list" class="text-xs" />
        <span class="hidden sm:inline">Matrix</span>
      </button>
    </div>
  </div>

  <!-- Main Body Content -->
  {#if activeDisplayMode === 'visual'}
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- VIEW A: 2D ANATOMICAL BODY MANNEQUIN VIEW                   -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div class="my-3 space-y-3">
      <!-- Perspective Switch & Status Legend -->
      <div class="flex flex-wrap items-center justify-between gap-2 text-xs">
        <!-- Anterior / Posterior Selector -->
        <div
          class="flex rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-0.5"
        >
          <button
            type="button"
            onclick={() => (bodySide = 'anterior')}
            class="rounded-md px-2.5 py-1 text-[0.6875rem] font-bold transition-all {bodySide ===
            'anterior'
              ? 'bg-[var(--color-primary)] text-white shadow-xs'
              : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
          >
            Vorderseite
          </button>
          <button
            type="button"
            onclick={() => (bodySide = 'posterior')}
            class="rounded-md px-2.5 py-1 text-[0.6875rem] font-bold transition-all {bodySide ===
            'posterior'
              ? 'bg-[var(--color-primary)] text-white shadow-xs'
              : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
          >
            Rückseite
          </button>
        </div>

        <!-- Color Status Legend -->
        <div class="flex items-center gap-2.5 text-[0.6875rem] text-[var(--text-muted)]">
          <div class="flex items-center gap-1">
            <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
            <span>Optimal</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="h-2 w-2 rounded-full bg-sky-500"></span>
            <span>Gering</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="h-2 w-2 rounded-full bg-rose-500"></span>
            <span>Hoch</span>
          </div>
        </div>
      </div>

      <!-- 2D SVG Mannequin Display -->
      <div
        class="flex h-[240px] w-full items-center justify-center rounded-2xl border border-[var(--border-subtle)] bg-gradient-to-b from-[var(--bg-surface-50)] to-[var(--bg-surface-100)] py-2"
      >
        <AnatomicalBodyVector
          view={bodySide}
          {pathColorMap}
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
            >{selected.setsWeekly.toLocaleString('de-DE')} Sätze &bull; {selected.volumeKg.toLocaleString('de-DE')} kg</span
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

      <!-- Muscle Matrix Grid -->
      <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {#each filteredMuscles as m (m.name)}
          <button
            type="button"
            onclick={() => (selectedMuscleGroup = m.name)}
            class="flex items-center justify-between rounded-xl border p-2.5 text-left transition-all {selectedMuscleGroup ===
            m.name
              ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)] ring-1 ring-[var(--color-primary)]'
              : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)] hover:border-[var(--border-strong)]'}"
          >
            <div class="flex items-center gap-2.5">
              <span
                class="h-2 w-2 rounded-full"
                style="background-color: {m.color === 'var(--bg-surface-200)'
                  ? 'var(--text-muted)'
                  : m.color};"
              ></span>
              <div>
                <p class="text-xs font-bold text-[var(--text-main)]">{m.name}</p>
                <p class="text-[0.6875rem] text-[var(--text-muted)]">
                  {m.setsWeekly.toLocaleString('de-DE')} Sätze &bull; {m.volumeKg.toLocaleString('de-DE')} kg
                </p>
              </div>
            </div>
            <span
              class="rounded-md px-1.5 py-0.5 text-[0.625rem] font-bold"
              style="background-color: {m.color}15; color: {m.color === 'var(--bg-surface-200)'
                ? 'var(--text-muted)'
                : m.color};"
            >
              {m.statusLabel}
            </span>
          </button>
        {/each}
      </div>
    </div>
  {/if}
</div>
