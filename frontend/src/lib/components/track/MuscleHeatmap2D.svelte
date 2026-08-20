<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import SegmentedControl from '../ui/SegmentedControl.svelte';
  import AnatomicalBodyVector from './AnatomicalBodyVector.svelte';
  import {
    DETAILED_MUSCLES,
    DETAILED_MUSCLE_MAP,
    parseMuscles,
    resolveMuscleGroup,
    type MuscleGroup,
    type DetailedMuscleKey
  } from '../../types/workouts';
  import { ANATOMICAL_PATH_TO_DETAILED_KEY } from './anatomy-data';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  interface MuscleVolumeData {
    name: string;
    latin?: string;
    key?: string;
    group: MuscleGroup;
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
  let activeDisplayMode = $state<string>('visual');
  let bodySide = $state<string>('anterior');
  let selectedCategory = $state<'all' | 'push' | 'pull' | 'legs' | 'core'>('all');
  let granularity = $state<string>('detailed');

  // Active selection: can be a DetailedMuscleKey OR a MuscleGroup
  let selectedDetailedKey = $state<DetailedMuscleKey | null>('chest_clavicular');
  let selectedMuscleGroup = $state<MuscleGroup>('Brust');

  const volumeQuery = useQuery(async () => {
    const [exercises, logs] = await Promise.all([db.exercise.toArray(), db.workout_set.toArray()]);

    const validExercises = exercises.filter((e) => !e.deleted_at);
    const validLogs = logs.filter((l) => !l.deleted_at);
    const exMap = new Map(validExercises.map((e) => [e.id, e]));

    // High-level group volume map (12 groups)
    const groupMap = new Map<MuscleGroup, { sets: number; volume: number; exNames: Set<string> }>();
    for (const conf of muscleConfigs) {
      groupMap.set(conf.name, { sets: 0, volume: 0, exNames: new Set() });
    }

    // Granular detailed muscle volume map (28 detailed muscles)
    const detailedMap = new Map<
      DetailedMuscleKey,
      { sets: number; volume: number; exNames: Set<string> }
    >();
    for (const m of DETAILED_MUSCLES) {
      detailedMap.set(m.key, { sets: 0, volume: 0, exNames: new Set() });
    }

    for (const log of validLogs) {
      const ex = exMap.get(log.exercise_id);
      if (!ex) continue;

      const logVol = (log.weight || 0) * (log.reps || 0);

      // Primary muscles (1.0 volume credit)
      const primaryTokens = parseMuscles(ex.primary_muscles);
      for (const token of primaryTokens) {
        const pGroup = resolveMuscleGroup(token);
        const curGroup = groupMap.get(pGroup) ?? { sets: 0, volume: 0, exNames: new Set() };
        curGroup.sets += 1.0;
        curGroup.volume += logVol;
        curGroup.exNames.add(ex.name);
        groupMap.set(pGroup, curGroup);

        if (token in DETAILED_MUSCLE_MAP) {
          const dKey = token as DetailedMuscleKey;
          const curDet = detailedMap.get(dKey) ?? { sets: 0, volume: 0, exNames: new Set() };
          curDet.sets += 1.0;
          curDet.volume += logVol;
          curDet.exNames.add(ex.name);
          detailedMap.set(dKey, curDet);
        } else {
          // If a high level group was specified, credit all submuscles in that group evenly
          for (const m of DETAILED_MUSCLES.filter((dm) => dm.group === pGroup)) {
            const curDet = detailedMap.get(m.key) ?? { sets: 0, volume: 0, exNames: new Set() };
            curDet.sets += 1.0;
            curDet.volume += logVol;
            curDet.exNames.add(ex.name);
            detailedMap.set(m.key, curDet);
          }
        }
      }

      // Secondary muscles (0.5 volume credit)
      const secondaryTokens = parseMuscles(ex.secondary_muscles);
      for (const token of secondaryTokens) {
        const sGroup = resolveMuscleGroup(token);
        const curGroup = groupMap.get(sGroup) ?? { sets: 0, volume: 0, exNames: new Set() };
        curGroup.sets += 0.5;
        curGroup.volume += logVol * 0.5;
        curGroup.exNames.add(ex.name);
        groupMap.set(sGroup, curGroup);

        if (token in DETAILED_MUSCLE_MAP) {
          const dKey = token as DetailedMuscleKey;
          const curDet = detailedMap.get(dKey) ?? { sets: 0, volume: 0, exNames: new Set() };
          curDet.sets += 0.5;
          curDet.volume += logVol * 0.5;
          curDet.exNames.add(ex.name);
          detailedMap.set(dKey, curDet);
        } else {
          for (const m of DETAILED_MUSCLES.filter((dm) => dm.group === sGroup)) {
            const curDet = detailedMap.get(m.key) ?? { sets: 0, volume: 0, exNames: new Set() };
            curDet.sets += 0.5;
            curDet.volume += logVol * 0.5;
            curDet.exNames.add(ex.name);
            detailedMap.set(m.key, curDet);
          }
        }
      }
    }

    // Compute rolled-up Group stats
    const groups: Partial<Record<MuscleGroup, MuscleVolumeData>> = {};
    for (const conf of muscleConfigs) {
      const data = groupMap.get(conf.name)!;
      const s = data.sets;
      const status: MuscleVolumeData['status'] =
        s >= 10 && s <= 18 ? 'optimal' : s > 18 ? 'overreaching' : s > 0 ? 'low' : 'none';
      const statusLabel =
        status === 'optimal'
          ? 'Optimal'
          : status === 'overreaching'
            ? 'Hoch'
            : status === 'low'
              ? 'Erhalt'
              : 'Keine Sätze';

      const color =
        status === 'optimal'
          ? '#10b981'
          : status === 'overreaching'
            ? '#f43f5e'
            : status === 'low'
              ? '#0ea5e9'
              : 'var(--bg-surface-200)';

      groups[conf.name] = {
        name: conf.name,
        group: conf.name,
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

    // Compute Granular Detailed Muscle Stats & Path Colors
    const detailed: Partial<Record<DetailedMuscleKey, MuscleVolumeData>> = {};
    const pathColorMap: Record<string, string> = {};

    for (const m of DETAILED_MUSCLES) {
      const data = detailedMap.get(m.key)!;
      const s = data.sets;
      const status: MuscleVolumeData['status'] =
        s >= 6 && s <= 14 ? 'optimal' : s > 14 ? 'overreaching' : s > 0 ? 'low' : 'none';
      const statusLabel =
        status === 'optimal'
          ? 'Optimal'
          : status === 'overreaching'
            ? 'Hoch'
            : status === 'low'
              ? 'Erhalt'
              : 'Keine Sätze';

      const color =
        status === 'optimal'
          ? '#10b981'
          : status === 'overreaching'
            ? '#f43f5e'
            : status === 'low'
              ? '#0ea5e9'
              : 'var(--bg-surface-200)';

      detailed[m.key] = {
        name: m.name,
        latin: m.latin,
        key: m.key,
        group: m.group,
        category: m.category,
        setsWeekly: s,
        volumeKg: data.volume,
        recoveryHoursLeft: s > 0 ? (s > 10 ? 18 : 8) : 0,
        status,
        statusLabel,
        exercises: Array.from(data.exNames),
        color
      };

      for (const pid of m.svgPathIds) {
        pathColorMap[pid] = color;
      }
    }

    return { groups, detailed, pathColorMap };
  });

  const groupsMap = $derived(volumeQuery.value?.groups ?? {});
  const detailedMap = $derived(volumeQuery.value?.detailed ?? {});

  // Path color map: in 'groups' mode, all paths of a group get that group's aggregated color
  const activePathColorMap = $derived.by(() => {
    if (granularity === 'groups') {
      const map: Record<string, string> = {};
      for (const m of DETAILED_MUSCLES) {
        const grp = groupsMap[m.group];
        const gColor = grp ? grp.color : 'var(--bg-surface-200)';
        for (const pid of m.svgPathIds) {
          map[pid] = gColor;
        }
      }
      return map;
    }
    return volumeQuery.value?.pathColorMap ?? {};
  });

  // Determine currently selected detailed or group item
  const selected = $derived.by<MuscleVolumeData>(() => {
    if (granularity === 'detailed' && selectedDetailedKey && detailedMap[selectedDetailedKey]) {
      return detailedMap[selectedDetailedKey]!;
    }
    if (groupsMap[selectedMuscleGroup]) {
      return groupsMap[selectedMuscleGroup]!;
    }
    return {
      name: selectedMuscleGroup,
      group: selectedMuscleGroup,
      category: 'push',
      setsWeekly: 0,
      volumeKg: 0,
      recoveryHoursLeft: 0,
      status: 'none',
      statusLabel: 'Keine Sätze',
      exercises: [],
      color: 'var(--bg-surface-200)'
    };
  });

  const detailedList = $derived(Object.values(detailedMap) as MuscleVolumeData[]);
  const groupList = $derived(Object.values(groupsMap) as MuscleVolumeData[]);

  const filteredDetailedMuscles = $derived(
    detailedList.filter((m) => selectedCategory === 'all' || m.category === selectedCategory)
  );

  const filteredGroupMuscles = $derived(
    groupList.filter((m) => selectedCategory === 'all' || m.category === selectedCategory)
  );

  function handleVectorSelect(group: MuscleGroup, detailedId?: string) {
    selectedMuscleGroup = group;
    if (granularity === 'groups') {
      selectedDetailedKey = null;
    } else {
      if (detailedId && ANATOMICAL_PATH_TO_DETAILED_KEY[detailedId]) {
        selectedDetailedKey = ANATOMICAL_PATH_TO_DETAILED_KEY[detailedId];
      } else {
        const first = DETAILED_MUSCLES.find((m) => m.group === group);
        selectedDetailedKey = first ? first.key : null;
      }
    }
  }
</script>

<div
  class="flex flex-col justify-between space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs"
>
  <!-- ═════════════════════════════════════════════════════════════ -->
  <!-- 1. COMPACT HEADER                                             -->
  <!-- ═════════════════════════════════════════════════════════════ -->
  <div class="flex items-center justify-between border-b border-border-subtle pb-3">
    <div class="flex items-center gap-2">
      <div
        class="flex h-7 w-7 items-center justify-center rounded-lg bg-primary-soft text-primary shadow-2xs"
      >
        <Icon name="accessibility_new" class="text-sm" />
      </div>
      <div>
        <h3 class="text-sm font-extrabold text-text-main">Muskel-Heatmap</h3>
        <p class="text-[10px] text-text-muted">7-Tage-Volumen</p>
      </div>
    </div>

    <!-- Mode Switch: Visual vs Matrix -->
    <SegmentedControl
      size="sm"
      bind:value={activeDisplayMode}
      options={[
        { value: 'visual', label: 'Visual' },
        { value: 'list', label: 'Matrix' }
      ]}
    />
  </div>

  <!-- ═════════════════════════════════════════════════════════════ -->
  <!-- 2. CONTEXT CONTROLS (Tightly spaced for 1/3 sidebar width)    -->
  <!-- ═════════════════════════════════════════════════════════════ -->
  <div class="flex flex-wrap items-center justify-between gap-1.5 text-xs">
    {#if activeDisplayMode === 'visual'}
      <SegmentedControl
        size="sm"
        bind:value={bodySide}
        options={[
          { value: 'anterior', label: 'Front' },
          { value: 'posterior', label: 'Rück' }
        ]}
      />
    {:else}
      <!-- Category Filter Pills -->
      <div class="no-scrollbar flex gap-1 overflow-x-auto">
        {#each [{ id: 'all', label: 'Alle' }, { id: 'push', label: 'Push' }, { id: 'pull', label: 'Pull' }, { id: 'legs', label: 'Beine' }, { id: 'core', label: 'Core' }] as const as tab}
          <button
            type="button"
            onclick={() => (selectedCategory = tab.id)}
            class="cursor-pointer rounded-lg px-2 py-0.5 text-[10px] font-bold whitespace-nowrap transition-all {selectedCategory ===
            tab.id
              ? 'bg-primary text-white shadow-2xs'
              : 'border border-border-subtle bg-surface-50 text-text-muted hover:text-text-main'}"
          >
            {tab.label}
          </button>
        {/each}
      </div>
    {/if}

    <!-- Granularity Toggle: Granular vs Hauptgruppen -->
    <SegmentedControl
      size="sm"
      bind:value={granularity}
      options={[
        { value: 'detailed', label: 'Granular (28)' },
        { value: 'groups', label: 'Gruppen (12)' }
      ]}
    />
  </div>

  <!-- ═════════════════════════════════════════════════════════════ -->
  <!-- 3. MAIN CONTENT: VISUAL VIEW (Perfect for Column Width)      -->
  <!-- ═════════════════════════════════════════════════════════════ -->
  {#if activeDisplayMode === 'visual'}
    <div class="space-y-3">
      <!-- 2D Anatomical Vector Mannequin Display -->
      <div
        class="flex h-[200px] w-full items-center justify-center rounded-2xl border border-border-subtle bg-gradient-to-b from-surface-50 to-surface-100 py-1.5 shadow-2xs"
      >
        <AnatomicalBodyVector
          view={bodySide as 'anterior' | 'posterior'}
          pathColorMap={activePathColorMap}
          selectedDetailedKey={granularity === 'detailed' ? selectedDetailedKey : null}
          selectedGroup={granularity === 'groups' ? selectedMuscleGroup : null}
          onselect={handleVectorSelect}
        />
      </div>

      <!-- Selected Muscle Info Card -->
      <div
        class="space-y-2.5 rounded-2xl border border-border-subtle bg-surface-50 p-3.5 shadow-2xs"
      >
        <!-- Muscle Header & Badge -->
        <div class="flex items-start justify-between gap-1.5 border-b border-border-subtle pb-2">
          <div>
            <div class="flex items-center gap-1.5">
              <span
                class="h-2 w-2 shrink-0 rounded-full"
                style="background-color: {selected.color === 'var(--bg-surface-200)'
                  ? 'var(--text-muted)'
                  : selected.color};"
              ></span>
              <h4 class="text-xs font-bold text-text-main">{selected.name}</h4>
              <span
                class="rounded bg-surface-200 px-1.5 py-0.5 text-[9px] font-bold text-text-muted"
              >
                {selected.group}
              </span>
            </div>
            {#if selected.latin}
              <p class="mt-0.5 line-clamp-1 text-[10px] text-text-muted italic">{selected.latin}</p>
            {/if}
          </div>

          <Badge
            variant={selected.status === 'optimal'
              ? 'success'
              : selected.status === 'overreaching'
                ? 'vital'
                : selected.status === 'low'
                  ? 'primary'
                  : 'default'}
            class="text-[9px]"
          >
            {selected.statusLabel}
          </Badge>
        </div>

        <!-- Volume & Sets Metrics -->
        <div class="grid grid-cols-2 gap-2 text-xs">
          <div class="rounded-xl border border-border-subtle bg-surface-0 p-2">
            <span class="text-[9px] font-semibold tracking-wider text-text-muted uppercase">
              Volumen
            </span>
            <p class="mt-0.5 text-sm font-extrabold text-text-main">
              {selected.setsWeekly.toLocaleString('de-DE')}
              <span class="text-[10px] font-medium text-text-muted">Sätze</span>
            </p>
            <p class="text-[9px] text-text-muted">
              {selected.volumeKg.toLocaleString('de-DE')} kg
            </p>
          </div>

          <div class="rounded-xl border border-border-subtle bg-surface-0 p-2">
            <span class="text-[9px] font-semibold tracking-wider text-text-muted uppercase">
              Erholung
            </span>
            <p
              class="mt-0.5 text-xs font-bold {selected.recoveryHoursLeft > 0
                ? 'text-amber-500'
                : 'text-emerald-500'}"
            >
              {selected.recoveryHoursLeft > 0 ? `~${selected.recoveryHoursLeft}h Rest` : '✓ Erholt'}
            </p>
            <p class="text-[9px] text-text-muted">
              {selected.setsWeekly > 0 ? 'Hypertrophie' : 'Inaktiv'}
            </p>
          </div>
        </div>

        <!-- Targeted Exercises List -->
        {#if selected.exercises.length > 0}
          <div class="border-t border-border-subtle pt-1.5">
            <span class="mb-1 block text-[9px] font-bold tracking-wider text-text-muted uppercase">
              Beteiligte Übungen:
            </span>
            <div class="flex max-h-[50px] flex-wrap gap-1 overflow-y-auto">
              {#each selected.exercises as exName}
                <span
                  class="rounded border border-border-subtle bg-surface-0 px-1.5 py-0.5 text-[10px] font-medium text-text-main shadow-2xs"
                >
                  {exName}
                </span>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </div>
  {:else}
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 4. MATRIX LIST VIEW                                           -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div class="grid max-h-[290px] grid-cols-1 gap-1.5 overflow-y-auto pr-1">
      {#if granularity === 'detailed'}
        {#each filteredDetailedMuscles as m (m.key)}
          <button
            type="button"
            onclick={() => {
              selectedDetailedKey = m.key as DetailedMuscleKey;
              selectedMuscleGroup = m.group;
            }}
            class="flex cursor-pointer items-center justify-between rounded-xl border p-2 text-left transition-all {selectedDetailedKey ===
            m.key
              ? 'border-primary bg-primary-soft ring-1 ring-primary'
              : 'border border-border-subtle bg-surface-50 hover:border-border-strong'}"
          >
            <div class="flex items-center gap-2">
              <span
                class="h-2 w-2 shrink-0 rounded-full"
                style="background-color: {m.color === 'var(--bg-surface-200)'
                  ? 'var(--text-muted)'
                  : m.color};"
              ></span>
              <div>
                <p class="text-xs font-bold text-text-main">{m.name}</p>
                <p class="line-clamp-1 text-[9px] text-text-muted italic">{m.latin}</p>
              </div>
            </div>
            <span
              class="rounded px-1.5 py-0.5 text-[10px] font-bold"
              style="background-color: {m.color}15; color: {m.color === 'var(--bg-surface-200)'
                ? 'var(--text-muted)'
                : m.color};"
            >
              {m.setsWeekly.toLocaleString('de-DE')} S
            </span>
          </button>
        {/each}
      {:else}
        {#each filteredGroupMuscles as m (m.name)}
          <button
            type="button"
            onclick={() => {
              selectedMuscleGroup = m.group;
              selectedDetailedKey = null;
            }}
            class="flex cursor-pointer items-center justify-between rounded-xl border p-2 text-left transition-all {selectedMuscleGroup ===
              m.group && !selectedDetailedKey
              ? 'border-primary bg-primary-soft ring-1 ring-primary'
              : 'border border-border-subtle bg-surface-50 hover:border-border-strong'}"
          >
            <div class="flex items-center gap-2">
              <span
                class="h-2 w-2 shrink-0 rounded-full"
                style="background-color: {m.color === 'var(--bg-surface-200)'
                  ? 'var(--text-muted)'
                  : m.color};"
              ></span>
              <div>
                <p class="text-xs font-bold text-text-main">{m.name}</p>
                <p class="text-[10px] text-text-muted">
                  {m.setsWeekly.toLocaleString('de-DE')} Sätze &bull; {m.volumeKg.toLocaleString(
                    'de-DE'
                  )} kg
                </p>
              </div>
            </div>
            <span
              class="rounded px-1.5 py-0.5 text-[10px] font-bold"
              style="background-color: {m.color}15; color: {m.color === 'var(--bg-surface-200)'
                ? 'var(--text-muted)'
                : m.color};"
            >
              {m.statusLabel}
            </span>
          </button>
        {/each}
      {/if}
    </div>
  {/if}
</div>
