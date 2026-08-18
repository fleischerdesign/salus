<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import ActiveWorkoutSession from '../workouts/ActiveWorkoutSession.svelte';
  import MuscleHeatmap2D from '../track/MuscleHeatmap2D.svelte';
  import Exercise1RMChart from '../track/Exercise1RMChart.svelte';
  import WorkoutSplitCard from '../track/WorkoutSplitCard.svelte';
  import WorkoutPlanEditorModal from '../workouts/WorkoutPlanEditorModal.svelte';
  import type { WorkoutPlan, WorkoutHistorySession } from '../../types/workouts';

  export type WorkoutTab = 'active' | 'plans' | 'sessions' | 'exercises';

  let {
    initialTab = 'active',
    ontabchange
  } = $props<{
    initialTab?: WorkoutTab;
    ontabchange?: (tab: WorkoutTab) => void;
  }>();

  let activeTab = $state<WorkoutTab>('active');

  $effect(() => {
    activeTab = initialTab;
  });

  function setTab(tab: WorkoutTab) {
    activeTab = tab;
    ontabchange?.(tab);
  }

  // ─── SAVED PLANS STATE ───
  let savedPlans = $state<WorkoutPlan[]>([
    {
      id: 'p1',
      name: 'Push Day A (Hypertrophie und Kraft)',
      split: 'Push / Pull / Legs',
      subtitle: 'Brust, vordere Schulter und Trizeps Fokus',
      exercisesCount: 5,
      estimatedDuration: '55 Min',
      targetVolume: '4.850 kg',
      targetVolumeKg: 4850,
      exercises: [
        { name: 'Bankdrücken (Langhantel)', muscle: 'Brust', targetSets: 4, targetReps: '6–8 Wdh', targetRir: 2 },
        { name: 'Schrägbankdrücken (Kurzhantel)', muscle: 'Brust', targetSets: 3, targetReps: '8–10 Wdh', targetRir: 1 },
        { name: 'Dips mit Zusatzgewicht', muscle: 'Trizeps', targetSets: 3, targetReps: '8–10 Wdh', targetRir: 1 },
        { name: 'Seitheben am Kabelzug', muscle: 'Schultern', targetSets: 3, targetReps: '12–15 Wdh', targetRir: 1 },
        { name: 'Trizepsdrücken am Kabelzug', muscle: 'Trizeps', targetSets: 3, targetReps: '10–12 Wdh', targetRir: 0 }
      ]
    },
    {
      id: 'p2',
      name: 'Pull Day A (Latissimus und Bizeps)',
      split: 'Push / Pull / Legs',
      subtitle: 'Breiter Rücken, oberer Rücken und Armbeuger',
      exercisesCount: 5,
      estimatedDuration: '50 Min',
      targetVolume: '5.200 kg',
      targetVolumeKg: 5200,
      exercises: [
        { name: 'Klimmzüge mit Zusatzgewicht', muscle: 'Rücken', targetSets: 4, targetReps: '6–8 Wdh', targetRir: 2 },
        { name: 'Langhantelrudern vorgebeugt', muscle: 'Rücken', targetSets: 4, targetReps: '8–10 Wdh', targetRir: 1 },
        { name: 'Latzug enger Griff', muscle: 'Rücken', targetSets: 3, targetReps: '10–12 Wdh', targetRir: 1 },
        { name: 'Face Pulls', muscle: 'Schultern', targetSets: 3, targetReps: '15 Wdh', targetRir: 2 },
        { name: 'Incline Dumbbell Curls', muscle: 'Bizeps', targetSets: 3, targetReps: '10–12 Wdh', targetRir: 0 }
      ]
    },
    {
      id: 'p3',
      name: 'Legs und Core (Unterkörper Kraft)',
      split: 'Push / Pull / Legs',
      subtitle: 'Quadrizeps, Beinbeuger, Waden und Rumpf',
      exercisesCount: 6,
      estimatedDuration: '65 Min',
      targetVolume: '7.800 kg',
      targetVolumeKg: 7800,
      exercises: [
        { name: 'Kniebeugen (High Bar)', muscle: 'Quadrizeps', targetSets: 4, targetReps: '5–6 Wdh', targetRir: 2 },
        { name: 'Rumänisches Kreuzheben', muscle: 'Hamstrings', targetSets: 4, targetReps: '8–10 Wdh', targetRir: 2 },
        { name: 'Beinpresse 45°', muscle: 'Quadrizeps', targetSets: 3, targetReps: '10–12 Wdh', targetRir: 1 },
        { name: 'Beinstrecker', muscle: 'Quadrizeps', targetSets: 3, targetReps: '12–15 Wdh', targetRir: 0 },
        { name: 'Wadenheben stehend', muscle: 'Waden', targetSets: 4, targetReps: '12–15 Wdh', targetRir: 0 },
        { name: 'Hanging Leg Raises', muscle: 'Bauch', targetSets: 3, targetReps: '12–15 Wdh', targetRir: 1 }
      ]
    }
  ]);

  // Plan Editor Modal State
  let isPlanEditorOpen = $state(false);
  let planToEdit = $state<WorkoutPlan | null>(null);

  function openCreatePlan() {
    planToEdit = null;
    isPlanEditorOpen = true;
  }

  function openEditPlan(plan: WorkoutPlan) {
    planToEdit = plan;
    isPlanEditorOpen = true;
  }

  function handleSavePlan(saved: WorkoutPlan) {
    const idx = savedPlans.findIndex(p => p.id === saved.id);
    if (idx !== -1) {
      savedPlans[idx] = saved;
      savedPlans = [...savedPlans];
    } else {
      savedPlans = [...savedPlans, saved];
    }
  }

  // ─── PAST SESSIONS HISTORY STATE ───
  let pastSessions = $state<WorkoutHistorySession[]>([
    {
      id: 's1',
      date: 'Samstag, 15. August 2026',
      planName: 'Pull Day A (Latissimus und Bizeps)',
      duration: '52 Min',
      durationMinutes: 52,
      tonnage: '5.240 kg',
      tonnageKg: 5240,
      setsCount: 17,
      prCount: 1,
      prNote: 'Klimmzüge: +25 kg Zusatzgewicht × 6 Wdh',
      avgHeartRate: 142,
      activeKcal: 485,
      exercises: [
        {
          name: 'Klimmzüge mit Zusatzgewicht',
          muscle: 'Rücken',
          totalVolumeKg: 1820,
          sets: [
            { setNumber: 1, weight: 106.8, reps: 8, type: 'warmup', rpe: 7 },
            { setNumber: 2, weight: 106.8, reps: 6, type: 'normal', rpe: 8.5, isPR: true },
            { setNumber: 3, weight: 106.8, reps: 6, type: 'normal', rpe: 9 },
            { setNumber: 4, weight: 106.8, reps: 5, type: 'normal', rpe: 9.5 }
          ]
        },
        {
          name: 'Langhantelrudern',
          muscle: 'Rücken',
          totalVolumeKg: 2040,
          sets: [
            { setNumber: 1, weight: 85, reps: 8, type: 'normal', rpe: 8 },
            { setNumber: 2, weight: 85, reps: 8, type: 'normal', rpe: 8.5 },
            { setNumber: 3, weight: 85, reps: 8, type: 'normal', rpe: 9 }
          ]
        },
        {
          name: 'Incline Dumbbell Curls',
          muscle: 'Bizeps',
          totalVolumeKg: 780,
          sets: [
            { setNumber: 1, weight: 16, reps: 10, type: 'normal', rpe: 8.5 },
            { setNumber: 2, weight: 16, reps: 9, type: 'drop', rpe: 10 }
          ]
        }
      ]
    },
    {
      id: 's2',
      date: 'Donnerstag, 13. August 2026',
      planName: 'Legs und Core (Unterkörper Kraft)',
      duration: '64 Min',
      durationMinutes: 64,
      tonnage: '7.850 kg',
      tonnageKg: 7850,
      setsCount: 19,
      prCount: 0,
      prNote: '',
      avgHeartRate: 156,
      activeKcal: 620,
      exercises: [
        {
          name: 'Kniebeugen (High Bar)',
          muscle: 'Quadrizeps',
          totalVolumeKg: 3120,
          sets: [
            { setNumber: 1, weight: 130, reps: 6, type: 'normal', rpe: 8 },
            { setNumber: 2, weight: 130, reps: 6, type: 'normal', rpe: 8.5 },
            { setNumber: 3, weight: 130, reps: 5, type: 'normal', rpe: 9 }
          ]
        },
        {
          name: 'Rumänisches Kreuzheben',
          muscle: 'Hamstrings',
          totalVolumeKg: 2640,
          sets: [
            { setNumber: 1, weight: 110, reps: 8, type: 'normal', rpe: 8 },
            { setNumber: 2, weight: 110, reps: 8, type: 'normal', rpe: 8.5 }
          ]
        }
      ]
    },
    {
      id: 's3',
      date: 'Dienstag, 11. August 2026',
      planName: 'Push Day A (Hypertrophie und Kraft)',
      duration: '48 Min',
      durationMinutes: 48,
      tonnage: '4.620 kg',
      tonnageKg: 4620,
      setsCount: 16,
      prCount: 1,
      prNote: 'Bankdrücken: 120 kg × 5 Wdh',
      avgHeartRate: 138,
      activeKcal: 440,
      exercises: [
        {
          name: 'Bankdrücken',
          muscle: 'Brust',
          totalVolumeKg: 2400,
          sets: [
            { setNumber: 1, weight: 120, reps: 5, type: 'normal', rpe: 8.5, isPR: true },
            { setNumber: 2, weight: 120, reps: 5, type: 'normal', rpe: 9 }
          ]
        }
      ]
    }
  ]);

  let expandedSessionId = $state<string | null>('s1');

  function toggleExpandSession(id: string) {
    expandedSessionId = expandedSessionId === id ? null : id;
  }

  // ─── EXERCISE DATABASE STATE ───
  let selectedMuscle = $state<string>('all');
  let exerciseSearch = $state<string>('');

  const exercises = [
    { name: 'Bankdrücken (Langhantel)', muscle: 'Brust', e1RM: '143.0 kg', bwRatio: '1.75x', category: 'Grundübung', equipment: 'Langhantel' },
    { name: 'Schrägbankdrücken (Kurzhantel)', muscle: 'Brust', e1RM: '42.5 kg je KH', bwRatio: '1.04x', category: 'Hypertrophie', equipment: 'Kurzhantel' },
    { name: 'Kniebeugen (High Bar)', muscle: 'Quadrizeps', e1RM: '155.0 kg', bwRatio: '1.90x', category: 'Grundübung', equipment: 'Langhantel' },
    { name: 'Kreuzheben (Konventionell)', muscle: 'Rücken / Beinbeuger', e1RM: '190.0 kg', bwRatio: '2.32x', category: 'Grundübung', equipment: 'Langhantel' },
    { name: 'Klimmzüge mit Zusatzgewicht', muscle: 'Rücken', e1RM: '115.0 kg Gesamtlast', bwRatio: '1.41x', category: 'Grundübung', equipment: 'Eigengewicht' },
    { name: 'Schulterdrücken (Overhead Press)', muscle: 'Schultern', e1RM: '82.5 kg', bwRatio: '1.01x', category: 'Grundübung', equipment: 'Langhantel' },
    { name: 'Dips mit Zusatzgewicht', muscle: 'Brust und Trizeps', e1RM: '125.0 kg Gesamtlast', bwRatio: '1.53x', category: 'Grundübung', equipment: 'Eigengewicht' }
  ];

  let filteredExercises = $derived(
    exercises.filter(ex => {
      const matchM = selectedMuscle === 'all' || ex.muscle.includes(selectedMuscle);
      const matchQ = !exerciseSearch || ex.name.toLowerCase().includes(exerciseSearch.toLowerCase());
      return matchM && matchQ;
    })
  );
</script>

<div class="space-y-6">
  
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Krafttraining und Workouts</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Live-Einheiten, progressive Überlastung, Periodisierung und Kraftkurven
      </p>
    </div>
    <div class="flex items-center gap-2">
      {#if activeTab !== 'active'}
        <button
          type="button"
          onclick={() => setTab('active')}
          class="px-4 py-2 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md flex items-center gap-1.5"
        >
          <span>+ Live-Training starten</span>
        </button>
      {/if}
    </div>
  </div>

  <!-- Primary Sub-Navigation Tabs -->
  <div class="flex gap-2 bg-[var(--bg-surface-50)] p-1.5 rounded-2xl border border-[var(--border-subtle)] overflow-x-auto no-scrollbar">
    <button
      type="button"
      onclick={() => setTab('active')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'active' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
      <span>Live-Einheit</span>
      <Badge variant="activity" class="text-[0.625rem]">Aktiv</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('plans')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'plans' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="chart" class="text-[var(--color-primary)]" />
      <span>Trainingspläne</span>
      <Badge variant="default" class="text-[0.625rem]">{savedPlans.length}</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('sessions')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'sessions' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="sun" class="text-[var(--color-circadian)]" />
      <span>Historie</span>
      <Badge variant="default" class="text-[0.625rem]">{pastSessions.length}</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('exercises')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'exercises' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="labs" class="text-[var(--color-vital)]" />
      <span>Kraftkurven und 1RM</span>
    </button>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 1: LIVE-TRAINING                                       -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'active'}
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 mb-4">
      <div class="lg:col-span-8">
        <ActiveWorkoutSession
          planName="Push Day A (Hypertrophie und Kraft)"
          onfinish={() => setTab('sessions')}
        />
      </div>
      <div class="lg:col-span-4 space-y-4">
        <MuscleHeatmap2D />
      </div>
    </div>
  {/if}

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 2: TRAININGSPLÄNE & SPLITS                             -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'plans'}
    <div class="space-y-5">
      <!-- Weekly Split Visualizer -->
      <WorkoutSplitCard />

      <!-- Saved Plan Templates List -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs">
        <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Deine Trainingsplan-Vorlagen</h2>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">Strukturierte Pläne mit progressivem Belastungsziel</p>
          </div>
          <button
            type="button"
            onclick={openCreatePlan}
            class="px-4 py-2 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-sm flex items-center gap-1.5"
          >
            <span>+ Neuen Plan erstellen</span>
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          {#each savedPlans as plan}
            <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 flex flex-col justify-between hover:border-[var(--color-primary)] transition-all space-y-4">
              <div>
                <div class="flex items-start justify-between mb-2">
                  <div>
                    <h3 class="text-sm font-extrabold text-[var(--text-main)]">{plan.name}</h3>
                    <span class="text-xs text-[var(--text-muted)]">{plan.split}</span>
                  </div>
                  <Badge variant="activity">{plan.estimatedDuration}</Badge>
                </div>

                <div class="space-y-1.5 my-3">
                  <span class="text-[0.6875rem] text-[var(--text-soft)] uppercase font-bold block">
                    Enthaltene Übungen ({plan.exercisesCount}):
                  </span>
                  {#each plan.exercises as ex}
                    <div class="text-xs text-[var(--text-main)] flex items-center justify-between">
                      <div class="flex items-center gap-1.5">
                        <span class="w-1.5 h-1.5 rounded-full bg-[var(--color-activity)]"></span>
                        <span class="font-semibold">{ex.name}</span>
                      </div>
                      <span class="text-[0.6875rem] text-[var(--text-muted)] tabular-nums">{ex.targetSets} &times; {ex.targetReps}</span>
                    </div>
                  {/each}
                </div>
              </div>

              <div class="pt-3 border-t border-[var(--border-subtle)] flex items-center justify-between">
                <button
                  type="button"
                  onclick={() => openEditPlan(plan)}
                  class="text-xs text-[var(--text-muted)] hover:text-[var(--color-primary)] font-bold cursor-pointer"
                >
                  Bearbeiten
                </button>
                <button
                  type="button"
                  onclick={() => setTab('active')}
                  class="px-3.5 py-1.5 rounded-xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs"
                >
                  Starten &rarr;
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>
  {/if}

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 3: VERGANGENE EINHEITEN (HISTORIE)                     -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'sessions'}
    <div class="space-y-4">
      {#each pastSessions as s}
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-3">
          
          <div class="flex items-center justify-between mb-2 flex-wrap gap-2">
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-base font-extrabold text-[var(--text-main)]">{s.planName}</h3>
                {#if s.prCount > 0}
                  <Badge variant="success">{s.prCount} Neuer Rekord (PR)</Badge>
                {/if}
              </div>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">{s.date} &bull; {s.duration} Dauer &bull; {s.activeKcal} kcal</p>
            </div>

            <div class="flex items-center gap-4">
              <div>
                <span class="text-xs text-[var(--text-muted)] block text-right font-semibold">Volumen-Tonnage</span>
                <span class="text-base font-extrabold text-[var(--color-activity)] block text-right tabular-nums">{s.tonnage}</span>
              </div>
              <Badge variant="default" class="font-bold">{s.setsCount} Sätze</Badge>
              <button
                type="button"
                onclick={() => toggleExpandSession(s.id)}
                class="px-2.5 py-1 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--text-main)] cursor-pointer hover:bg-[var(--bg-surface-100)]"
              >
                {expandedSessionId === s.id ? 'Einklappen ▲' : 'Details ▼'}
              </button>
            </div>
          </div>

          {#if s.prNote}
            <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-3 text-xs text-emerald-500 font-bold flex items-center gap-2">
              <span>PR:</span>
              <span>{s.prNote}</span>
            </div>
          {/if}

          <!-- Expandable Detailed Set Breakdown -->
          {#if expandedSessionId === s.id}
            <div class="pt-3 border-t border-[var(--border-subtle)] space-y-3 animate-[fadeIn_0.15s_ease-out]">
              <span class="text-xs font-extrabold text-[var(--text-main)] block">Satz-für-Satz Aufschlüsselung:</span>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                {#each s.exercises as ex}
                  <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-3.5 space-y-2">
                    <div class="flex justify-between items-center text-xs">
                      <span class="font-extrabold text-[var(--text-main)]">{ex.name}</span>
                      <span class="text-[0.6875rem] text-[var(--color-activity)] font-bold tabular-nums">{ex.totalVolumeKg} kg</span>
                    </div>

                    <div class="space-y-1 text-xs">
                      {#each ex.sets as st}
                        <div class="flex justify-between items-center text-[0.6875rem] text-[var(--text-muted)]">
                          <span>Satz {st.setNumber} ({st.type}):</span>
                          <span class="font-bold text-[var(--text-main)] tabular-nums">
                            {st.weight} kg &times; {st.reps} Wdh {st.rpe ? `(@${st.rpe})` : ''}
                            {#if st.isPR}<span class="text-emerald-500 ml-1">Stern PR</span>{/if}
                          </span>
                        </div>
                      {/each}
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}

        </div>
      {/each}
    </div>
  {/if}

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 4: ÜBUNGS-KATALOG & 1RM                                -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'exercises'}
    <div class="space-y-5">
      <!-- 1RM Trajectory Showcase -->
      <Exercise1RMChart />

      <!-- Muscle Heatmap Full Visualizer -->
      <MuscleHeatmap2D />

      <!-- Exercise Database Table -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs">
        <div class="flex items-center justify-between mb-4 flex-wrap gap-3">
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Übungs-Katalog und Maximalkraft-Werte</h2>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">Wissenschaftliche 1RM-Formel nach Brzycki und Epley</p>
          </div>
          <div class="flex items-center gap-2">
            <input
              type="text"
              placeholder="Übung suchen..."
              bind:value={exerciseSearch}
              class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl px-3.5 py-2 text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
            />
          </div>
        </div>

        <div class="w-full overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.6875rem]">
                <th class="py-2.5 px-3">Übungsname</th>
                <th class="py-2.5 px-3">Muskelgruppe</th>
                <th class="py-2.5 px-3">Equipment</th>
                <th class="py-2.5 px-3">Aktuelles 1RM</th>
                <th class="py-2.5 px-3">Relativkraft</th>
                <th class="py-2.5 px-3 text-right">Kategorie</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)]">
              {#each filteredExercises as ex}
                <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
                  <td class="py-3 px-3 font-extrabold text-[var(--text-main)]">{ex.name}</td>
                  <td class="py-3 px-3"><Badge variant="default">{ex.muscle}</Badge></td>
                  <td class="py-3 px-3 text-[var(--text-muted)]">{ex.equipment}</td>
                  <td class="py-3 px-3 font-bold text-[var(--color-activity)] text-sm tabular-nums">{ex.e1RM}</td>
                  <td class="py-3 px-3 font-bold text-[var(--color-primary)] tabular-nums">{ex.bwRatio}</td>
                  <td class="py-3 px-3 text-right text-[var(--text-muted)] font-semibold">{ex.category}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  {/if}

</div>

<!-- Plan Editor Modal -->
<WorkoutPlanEditorModal
  open={isPlanEditorOpen}
  plan={planToEdit}
  onsave={handleSavePlan}
  onclose={() => isPlanEditorOpen = false}
/>
