<script lang="ts">
  import { liveQuery } from 'dexie';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import { mutate, nextTempId } from '$lib/db/mutate';
  import { mutateDomain } from '$lib/db/mutate-domain';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Textarea from '$components/ui/Textarea.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import RestTimer from '$components/workouts/RestTimer.svelte';
  import SetLogger from '$components/workouts/SetLogger.svelte';

  type LogState = 'pending' | 'logging' | 'logged' | 'failed';

  let session = liveQuery(() =>
    db.workout_session
      .toArray()
      .then((arr) => arr.find((s) => s.completed_at == null && !s.deleted_at) ?? null),
  );

  let planExercises = liveQuery(async () => {
    if (!$session?.plan_id) return [];
    const pes = await db.workout_plan_exercise
      .where('plan_id')
      .equals($session.plan_id)
      .toArray();
    return pes
      .filter((pe) => !pe.deleted_at)
      .sort((a, b) => a.sequence - b.sequence);
  });

  let allLogs = liveQuery(async () => {
    if (!$session) return [];
    return db.workout_log_entry
      .where('session_id')
      .equals($session.id)
      .toArray()
      .then((arr) => arr.filter((l) => !l.deleted_at));
  });

  // Log states — keyed by `${exerciseId}-${setNumber}`
  let logStates = $state<Record<string, LogState>>({});
  // RPE-10 auto-scale
  let rpePrompts = $state(new Map<number, number>());
  let scaledWeights = $state<Record<string, number>>({});
  let scaleVersion = $state(0);

  // Audio guide
  let audioEnabled = $state(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem('salus_audio_guide') === 'true'
      : false,
  );

  // Rest timer
  let startTimer: ((seconds?: number) => void) | null = $state(null);

  let notes = $state('');
  let completing = $state(false);

  let loading = $derived($session == null || $allLogs == null);

  // Derive targets from plan exercises
  let targets = $derived(
    $planExercises.map((pe) => {
      const ex = $exercises?.get(pe.exercise_id);
      const exerciseLogs = ($allLogs ?? []).filter(
        (l) => l.exercise_id === pe.exercise_id,
      );
      const lastWeight =
        exerciseLogs.length > 0
          ? exerciseLogs[exerciseLogs.length - 1].weight
          : null;
      const maxWeight = Math.max(
        0,
        ...exerciseLogs.map((l) => l.weight ?? 0),
      );
      const maxEst1rm = Math.max(
        0,
        ...exerciseLogs.map((l) => {
          if (l.weight == null || l.reps == null) return 0;
          return l.weight / (1.0278 - 0.0278 * l.reps);
        }),
      );

      return {
        exercise_id: pe.exercise_id,
        name: ex?.name ?? `Exercise ${pe.exercise_id}`,
        suggested_sets: pe.target_sets ?? 3,
        suggested_reps: pe.target_reps ?? 10,
        suggested_rpe: pe.target_rpe ?? 7,
        weight_multiplier: 1.0,
        is_autoreg_exempt: pe.is_autoreg_exempt,
        reason: '',
        last_weight: lastWeight,
        pr_weight: maxWeight,
        pr_est_1rm: maxEst1rm,
        rest_seconds: pe.rest_seconds ?? 120,
      };
    }),
  );

  let exercises = liveQuery(async () => {
    const map = new Map((await db.exercise.toArray()).map((e) => [e.id, e]));
    return map;
  });

  // Init log states from existing logs
  $effect(() => {
    const init: Record<string, LogState> = {};
    for (const log of $allLogs ?? []) {
      init[`${log.exercise_id}-${log.set_number}`] = 'logged';
    }
    logStates = init;
  });

  function speak(text: string) {
    if (!audioEnabled || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = document.documentElement.lang || 'en-US';
    window.speechSynthesis.speak(u);
  }

  function toggleAudio() {
    audioEnabled = !audioEnabled;
    localStorage.setItem('salus_audio_guide', audioEnabled ? 'true' : 'false');
    if (audioEnabled) speak('Audio guide enabled.');
    else if (window.speechSynthesis) window.speechSynthesis.cancel();
  }

  function formatTime(dt: string | null | undefined): string {
    if (!dt) return '—';
    return new Date(dt).toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function getLogState(exId: number, setNum: number): LogState {
    return logStates[`${exId}-${setNum}`] ?? 'pending';
  }

  function getInitialWeight(exId: number, setNum: number): number {
    const log = ($allLogs ?? []).find(
      (l) => l.exercise_id === exId && l.set_number === setNum,
    );
    if (log?.weight) return log.weight;
    const key = `${exId}-${setNum}`;
    if (scaledWeights[key] !== undefined) return scaledWeights[key];
    return targets?.find((t) => t.exercise_id === exId)?.last_weight ?? 40;
  }

  function getInitialReps(exId: number, setNum: number): number {
    const log = ($allLogs ?? []).find(
      (l) => l.exercise_id === exId && l.set_number === setNum,
    );
    if (log?.reps) return log.reps;
    return targets?.find((t) => t.exercise_id === exId)?.suggested_reps ?? 10;
  }

  function getInitialRpe(exId: number, setNum: number): number {
    const log = ($allLogs ?? []).find(
      (l) => l.exercise_id === exId && l.set_number === setNum,
    );
    if (log?.rpe != null) return log.rpe;
    return targets?.find((t) => t.exercise_id === exId)?.suggested_rpe ?? 7;
  }

  async function handleLogSet(
    exId: number,
    setNum: number,
    data: { weight: number; reps: number; rpe: number },
  ) {
    const key = `${exId}-${setNum}`;
    logStates = { ...logStates, [key]: 'logging' };

    const tempId = nextTempId();
    const body = {
      exercise_id: exId,
      set_number: setNum,
      weight: data.weight,
      reps: data.reps,
      rpe: data.rpe,
    };

    const { ok } = await mutateDomain({
      url: `/api/v1/workouts/sessions/log?session_id=${$session?.id}`,
      method: 'POST',
      body,
      optimisticTable: 'workout_log_entry',
      optimisticData: {
        id: tempId,
        session_id: $session!.id,
        exercise_id: exId,
        set_number: setNum,
        weight: data.weight,
        reps: data.reps,
        rpe: data.rpe,
        created_at: new Date().toISOString(),
        updated_at: null,
        deleted_at: null,
      },
      optimisticId: tempId,
      responseTable: 'workout_log_entry',
    });

    if (ok) {
      logStates = { ...logStates, [key]: 'logged' };
      if (data.rpe >= 10) rpePrompts.set(exId, setNum);
      speak(`Set ${setNum} logged.`);
      startTimer?.(targets?.find((t) => t.exercise_id === exId)?.rest_seconds);
    } else {
      logStates = { ...logStates, [key]: 'failed' };
      speak('Failed to log set.');
    }
  }

  async function handleUnlogSet(exId: number, setNum: number) {
    const key = `${exId}-${setNum}`;
    logStates = { ...logStates, [key]: 'logging' };

    const existingId = ($allLogs ?? []).find(
      (l) => l.exercise_id === exId && l.set_number === setNum,
    )?.id;

    const { ok } = await mutateDomain({
      url: `/api/v1/workouts/sessions/log?session_id=${$session?.id}&exercise_id=${exId}&set_number=${setNum}`,
      method: 'DELETE',
      optimisticTable: 'workout_log_entry',
      optimisticId: existingId ?? nextTempId(),
    });

    if (ok) {
      logStates = { ...logStates, [key]: 'pending' };
      speak(`Set ${setNum} removed.`);
    } else {
      logStates = { ...logStates, [key]: 'logged' };
    }
  }

  function applyWeightScaling(exId: number, totalSets: number) {
    const triggerSet = rpePrompts.get(exId);
    if (triggerSet === undefined) return;
    const triggerLog = ($allLogs ?? []).find(
      (l) => l.exercise_id === exId && l.set_number === triggerSet,
    );
    if (!triggerLog?.weight) return;
    const baseWeight = triggerLog.weight;
    const next: Record<string, number> = { ...scaledWeights };
    for (let s = triggerSet + 1; s <= totalSets; s++) {
      const key = `${exId}-${s}`;
      if (
        logStates[key] === 'pending' ||
        logStates[key] === undefined
      ) {
        next[key] = Math.round(baseWeight * 0.95 * 2) / 2;
      }
    }
    scaledWeights = next;
    rpePrompts.delete(exId);
    scaleVersion++;
  }

  function dismissRpePrompt(exId: number) {
    rpePrompts.delete(exId);
  }

  async function complete() {
    completing = true;
    const now = new Date().toISOString();
    const sessionId = $session?.id as number;
    const { ok } = await mutate({
      table: 'workout_session',
      type: 'update',
      realId: sessionId,
      data: {
        completed_at: now,
        notes: notes || undefined,
      },
      optimistic: {
        id: sessionId,
        user_id: $session?.user_id ?? 0,
        plan_id: $session?.plan_id ?? null,
        started_at: $session?.started_at ?? now,
        completed_at: now,
        recovery_score: $session?.recovery_score ?? null,
        autoreg_mode: $session?.autoreg_mode ?? 'advisory',
        notes: notes || null,
        created_at: $session?.created_at ?? now,
        updated_at: now,
        deleted_at: null,
      },
    });
    if (ok) {
      await goto(`/workouts/sessions/${sessionId}`);
    }
    completing = false;
  }
</script>

<svelte:head><title>Salus — Active Workout</title></svelte:head>

<div class="space-y-6">
  {#if loading}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else if $session}
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <a
          href="/workouts"
          class="flex items-center gap-1 text-sm text-surface-500 no-underline transition-colors duration-150 hover:text-surface-700"
        >
          <Icon name="arrow-back" size="sm" />Workouts
        </a>
        <h1 class="mt-1 text-2xl font-semibold text-surface-900">
          Active Workout Session
        </h1>
        <p class="mt-1 text-sm text-surface-500">
          Started {formatTime($session.started_at)}
        </p>
      </div>
      <div class="flex items-center gap-3">
        {#if $session.recovery_score}
          <Badge variant="success">
            <Icon name="bolt" size="sm" />Recovery {Math.round(
              $session.recovery_score,
            )}%
          </Badge>
        {/if}
        <button
          type="button"
          class="flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors duration-150 {audioEnabled
            ? 'border-primary-300 bg-primary-50 text-primary-700'
            : 'border-surface-200 bg-surface-50 text-surface-500 hover:border-surface-300'}"
          onclick={toggleAudio}
        >
          <Icon
            name={audioEnabled ? 'volume-up' : 'volume-off'}
            size="sm"
          />
          {audioEnabled ? 'Audio On' : 'Audio Off'}
        </button>
      </div>
    </div>

    {#if targets && targets.length > 0}
      {#each targets as target (target.exercise_id)}
        {#key `${target.exercise_id}-${scaleVersion}`}
          <Card padding={false}>
            {#snippet header()}
              <div class="flex items-center justify-between gap-3">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-semibold text-surface-900"
                    >{target.name}</span
                  >
                  <Icon
                    name={target.is_autoreg_exempt ? 'lock' : 'auto-awesome'}
                    size="sm"
                    class={target.is_autoreg_exempt
                      ? 'text-surface-400'
                      : 'text-primary-500'}
                  />
                </div>
                <div
                  class="flex items-center gap-2 text-xs text-surface-500"
                >
                  <span
                    >{target.suggested_sets} sets × {target.suggested_reps} @
                    RPE {target.suggested_rpe}</span
                  >
                  {#if target.weight_multiplier !== 1.0}
                    <span class="text-primary-500"
                      >({Math.round(
                        target.weight_multiplier * 100,
                      )}%)</span
                    >
                  {/if}
                  {#if target.pr_weight > 0}
                    <Badge variant="primary">
                      <Icon name="trophy" size="sm" />PR: {target.pr_weight} kg
                    </Badge>
                  {/if}
                </div>
              </div>
              {#if target.reason}
                <p class="mt-1 max-w-xl text-xs text-surface-400">
                  {target.reason}
                </p>
              {/if}
            {/snippet}

            <div class="space-y-1 p-3">
              {#each Array.from({ length: target.suggested_sets }, (_, i) => i + 1) as setNum}
                <SetLogger
                  setNumber={setNum}
                  suggestedWeight={getInitialWeight(
                    target.exercise_id,
                    setNum,
                  )}
                  suggestedReps={getInitialReps(
                    target.exercise_id,
                    setNum,
                  )}
                  suggestedRpe={getInitialRpe(
                    target.exercise_id,
                    setNum,
                  )}
                  prWeight={target.pr_weight}
                  prEst1rm={target.pr_est_1rm}
                  logState={getLogState(target.exercise_id, setNum)}
                  onlog={(data) =>
                    handleLogSet(target.exercise_id, setNum, data)}
                  onunlog={() =>
                    handleUnlogSet(target.exercise_id, setNum)}
                />
              {/each}
            </div>

            {#if rpePrompts.has(target.exercise_id)}
              <div
                class="mx-3 mb-3 rounded-lg border border-error-200 bg-error-50 p-3"
              >
                <div class="flex items-center gap-2">
                  <Icon
                    name="warning"
                    size="sm"
                    class="text-error-600"
                  />
                  <p class="text-xs font-semibold text-error-700">
                    Muscle Failure (RPE 10) Detected
                  </p>
                </div>
                <p class="mt-1 text-xs text-surface-600">
                  Scale remaining sets down by 5% for this exercise?
                </p>
                <div class="mt-2 flex gap-2">
                  <Btn
                    variant="primary"
                    size="sm"
                    onclick={() =>
                      applyWeightScaling(
                        target.exercise_id,
                        target.suggested_sets,
                      )}
                  >
                    Yes, scale down
                  </Btn>
                  <Btn
                    variant="ghost"
                    size="sm"
                    onclick={() =>
                      dismissRpePrompt(target.exercise_id)}
                  >
                    No, keep weight
                  </Btn>
                </div>
              </div>
            {/if}
          </Card>
        {/key}
      {/each}
    {:else}
      <Card>
        <p class="text-sm text-surface-500">
          No workout plan associated with this session.
        </p>
      </Card>
    {/if}

    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">
          Finish Workout Session
        </span>
      {/snippet}
      <div class="p-6">
        <FormField label="Session Notes">
          <Textarea
            name="notes"
            bind:value={notes}
            rows={3}
            placeholder="How did it feel today? Any pain or outstanding form?"
          />
        </FormField>
        <div class="mt-4 flex justify-end">
          <Btn
            variant="primary"
            loading={completing}
            onclick={complete}
          >
            Complete Workout
          </Btn>
        </div>
      </div>
    </Card>
  {:else}
    <div class="flex justify-center py-20">
      <Card>
        <div class="text-center py-8">
          <p class="text-lg font-semibold text-surface-900">
            No Active Workout
          </p>
          <p class="mt-1 text-sm text-surface-500">
            Start a workout from your training plan.
          </p>
          <div class="mt-4">
            <Btn variant="primary" href="/workouts/plans">
              Go to Plans
            </Btn>
          </div>
        </div>
      </Card>
    </div>
  {/if}

  <RestTimer
    onstart={(fn) => {
      startTimer = fn;
    }}
    oncomplete={() =>
      speak('Rest finished. Time for your next set!')}
  />
</div>
