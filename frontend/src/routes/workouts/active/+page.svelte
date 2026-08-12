<script lang="ts">
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import { completeWorkout, cancelWorkout, logSet, deleteLogSet } from '$lib/mutations/workout';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Textarea from '$components/ui/Textarea.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import RestTimer from '$components/workouts/RestTimer.svelte';
  import SetLogger from '$components/workouts/SetLogger.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';

  type LogState = 'pending' | 'logging' | 'logged' | 'failed';

  const sessionQuery = useQuery(() =>
    db.workout_session
      .toArray()
      .then((arr) => arr.find((s) => s.completed_at == null && !s.deleted_at) ?? null)
  );
  const session = $derived(sessionQuery.value);

  const planExercisesQuery = useQuery(async () => {
    const activeSession = session;
    if (!activeSession?.plan_id) return [];
    const pes = await db.workout_plan_exercise
      .where('plan_id')
      .equals(activeSession.plan_id)
      .toArray();
    return pes.filter((pe) => !pe.deleted_at).sort((a, b) => a.sequence - b.sequence);
  });
  const planExercises = $derived(planExercisesQuery.value);

  const allLogsQuery = useQuery(async () => {
    const activeSession = session;
    if (!activeSession) return [];
    return db.workout_log_entry
      .where('session_id')
      .equals(activeSession.id)
      .toArray()
      .then((arr) => arr.filter((l) => !l.deleted_at));
  });
  const allLogs = $derived(allLogsQuery.value);

  let logStates = $state<Record<string, LogState>>({});
  let rpePrompts = $state(new Map<string, number>());
  let scaledWeights = $state<Record<string, number>>({});
  let scaleVersion = $state(0);

  let audioEnabled = $state(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem('salus_audio_guide') === 'true'
      : false
  );

  let autoStartRest = $state(
    typeof localStorage !== 'undefined' ? localStorage.getItem('salus_auto_rest') !== 'false' : true
  );

  function toggleAutoRest() {
    autoStartRest = !autoStartRest;
    localStorage.setItem('salus_auto_rest', autoStartRest ? 'true' : 'false');
  }

  let startTimer: ((seconds?: number) => void) | null = $state(null);

  let notes = $state('');
  let completing = $state(false);
  let canceling = $state(false);
  let cancelDialogOpen = $state(false);
  let settingsModalOpen = $state(false);

  let loading = $derived(session == null || planExercises == null || allLogs == null);

  const exercisesQuery = useQuery(async () => {
    const map = new Map((await db.exercise.toArray()).map((e) => [e.id, e]));
    return map;
  });
  const exercises = $derived(exercisesQuery.value);

  interface Target {
    exercise_id: string;
    name: string;
    suggested_sets: number;
    suggested_reps: number;
    suggested_rpe: number;
    weight_multiplier: number;
    is_autoreg_exempt: boolean;
    reason: string;
    rest_seconds: number;
    last_weight: number;
    pr_weight: number;
    pr_est_1rm: number;
  }

  let targets = $derived.by<Target[] | null>(() => {
    if (!session || !planExercises || !exercises) return null;

    const sessionScore = session.recovery_score ?? 100;
    const factor = sessionScore / 100;

    return (planExercises ?? []).map((pe) => {
      const ex = exercises.get(pe.exercise_id);
      const exLogs = (allLogs ?? []).filter((l) => l.exercise_id === pe.exercise_id);

      let lastWeight = 40;
      let prWeight = 0;
      let prEst1rm = 0;

      for (const l of exLogs) {
        if (l.weight > prWeight) prWeight = l.weight;
        const est1rm =
          l.reps <= 0 ? 0 : l.reps === 1 ? l.weight : l.weight / (1.0278 - 0.0278 * l.reps);
        if (est1rm > prEst1rm) prEst1rm = est1rm;
        lastWeight = l.weight;
      }

      let multiplier = 1.0;
      let reason = '';
      if (!pe.is_autoreg_exempt && factor < 0.95) {
        multiplier = Math.max(0.8, factor);
        reason = `Autoregulated: recovery score is ${Math.round(sessionScore)}%, intensity scaled to ${Math.round(multiplier * 100)}%.`;
      }

      return {
        exercise_id: pe.exercise_id,
        name: ex?.name ?? 'Exercise',
        suggested_sets: pe.target_sets ?? 3,
        suggested_reps: pe.target_reps ?? 8,
        suggested_rpe: pe.target_rpe ?? 8,
        weight_multiplier: multiplier,
        is_autoreg_exempt: pe.is_autoreg_exempt ?? false,
        reason,
        rest_seconds: ex?.suggested_rest_seconds ?? pe.rest_seconds ?? 90,
        last_weight: lastWeight,
        pr_weight: prWeight,
        pr_est_1rm: prEst1rm
      };
    });
  });

  function speak(text: string) {
    if (!audioEnabled || typeof window === 'undefined' || !window.speechSynthesis) return;
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
      minute: '2-digit'
    });
  }

  function getLogState(exId: string, setNum: number): LogState {
    const key = `${exId}-${setNum}`;
    if (logStates[key]) return logStates[key];
    const isLogged = (allLogs ?? []).some(
      (l) => l.exercise_id === exId && l.set_number === setNum && !l.deleted_at
    );
    return isLogged ? 'logged' : 'pending';
  }

  function getInitialWeight(exId: string, setNum: number): number {
    const log = (allLogs ?? []).find((l) => l.exercise_id === exId && l.set_number === setNum);
    if (log?.weight) return log.weight;
    const key = `${exId}-${setNum}`;
    if (scaledWeights[key] !== undefined) return scaledWeights[key];
    return targets?.find((t) => t.exercise_id === exId)?.last_weight ?? 40;
  }

  function getInitialReps(exId: string, setNum: number): number {
    const log = (allLogs ?? []).find((l) => l.exercise_id === exId && l.set_number === setNum);
    if (log?.reps) return log.reps;
    return targets?.find((t) => t.exercise_id === exId)?.suggested_reps ?? 10;
  }

  function getInitialRpe(exId: string, setNum: number): number {
    const log = (allLogs ?? []).find((l) => l.exercise_id === exId && l.set_number === setNum);
    if (log?.rpe != null) return log.rpe;
    return targets?.find((t) => t.exercise_id === exId)?.suggested_rpe ?? 7;
  }

  async function handleLogSet(
    exId: string,
    setNum: number,
    data: { weight: number; reps: number; rpe: number }
  ) {
    const key = `${exId}-${setNum}`;
    logStates = { ...logStates, [key]: 'logging' };

    const sessionId = session?.id ?? '';
    const { ok } = await logSet(sessionId, exId, setNum, data.weight, data.reps, data.rpe);

    if (ok) {
      logStates = { ...logStates, [key]: 'logged' };
      if (data.rpe >= 10) rpePrompts.set(exId, setNum);
      speak(`Set ${setNum} logged.`);
      if (autoStartRest) {
        startTimer?.(targets?.find((t) => t.exercise_id === exId)?.rest_seconds);
      }
    } else {
      logStates = { ...logStates, [key]: 'failed' };
      speak('Failed to log set.');
    }
  }

  async function handleUnlogSet(exId: string, setNum: number) {
    const key = `${exId}-${setNum}`;
    logStates = { ...logStates, [key]: 'logging' };

    const existingId = (allLogs ?? []).find(
      (l) => l.exercise_id === exId && l.set_number === setNum
    )?.id;

    if (existingId) {
      const { ok } = await deleteLogSet(existingId);
      if (ok) {
        logStates = { ...logStates, [key]: 'pending' };
        speak(`Set ${setNum} removed.`);
      } else {
        logStates = { ...logStates, [key]: 'logged' };
      }
    }
  }

  function applyWeightScaling(exId: string, totalSets: number) {
    const triggerSet = rpePrompts.get(exId);
    if (triggerSet === undefined) return;
    const triggerLog = (allLogs ?? []).find(
      (l) => l.exercise_id === exId && l.set_number === triggerSet
    );
    if (!triggerLog?.weight) return;
    const baseWeight = triggerLog.weight;
    const next: Record<string, number> = { ...scaledWeights };
    for (let s = triggerSet + 1; s <= totalSets; s++) {
      const key = `${exId}-${s}`;
      if (logStates[key] === 'pending' || logStates[key] === undefined) {
        next[key] = Math.round(baseWeight * 0.95 * 2) / 2;
      }
    }
    scaledWeights = next;
    rpePrompts.delete(exId);
    scaleVersion++;
  }

  function dismissRpePrompt(exId: string) {
    rpePrompts.delete(exId);
  }

  async function complete() {
    completing = true;
    const sessionId = session?.id ?? '';
    const { ok } = await completeWorkout(sessionId, notes || undefined);
    if (ok) {
      await goto(`/workouts/sessions/${sessionId}`);
    }
    completing = false;
  }

  async function confirmCancel() {
    if (!session) return;
    canceling = true;
    const sessionId = session.id;
    await cancelWorkout(sessionId);
    canceling = false;
    await goto('/workouts');
  }
</script>

<svelte:head><title>Salus — Active Workout</title></svelte:head>

<div class="space-y-6">
  {#if loading}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else if session}
    <PageHeader
      title="Active Workout Session"
      subtitle={`Started ${formatTime(session.started_at)}`}
      icon="fitness-center"
      iconColor="#4f46e5"
      backUrl="/workouts"
    >
      {#snippet actions()}
        <div class="flex h-full items-stretch divide-x divide-surface-200 select-none">
          {#if session.recovery_score}
            <div
              class="flex h-full items-center justify-center gap-2 bg-emerald-50 px-6 text-xs font-semibold whitespace-nowrap text-emerald-800"
            >
              <Icon name="bolt" size="sm" class="text-emerald-600" />
              <span>Recovery {Math.round(session.recovery_score)}%</span>
            </div>
          {/if}
          <button
            type="button"
            class="duration-micro flex h-full w-14 items-center justify-center text-surface-600 transition-colors hover:bg-surface-100 hover:text-surface-900"
            onclick={() => (settingsModalOpen = true)}
            title="Session Settings"
            aria-label="Session Settings"
          >
            <Icon name="settings" size="sm" />
          </button>
        </div>
      {/snippet}
    </PageHeader>

    {#if targets && targets.length > 0}
      {#each targets as target (target.exercise_id)}
        {#key `${target.exercise_id}-${scaleVersion}`}
          <Card padding={false}>
            {#snippet header()}
              <div class="flex items-center justify-between gap-3">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-semibold text-surface-900">{target.name}</span>
                  <Icon
                    name={target.is_autoreg_exempt ? 'lock' : 'auto-awesome'}
                    size="sm"
                    class={target.is_autoreg_exempt ? 'text-surface-400' : 'text-primary-500'}
                  />
                </div>
                <div class="flex items-center gap-2 text-xs text-surface-500">
                  <span
                    >{target.suggested_sets} sets × {target.suggested_reps} @ RPE {target.suggested_rpe}</span
                  >
                  {#if target.weight_multiplier !== 1.0}
                    <span class="text-primary-500"
                      >({Math.round(target.weight_multiplier * 100)}%)</span
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
                  suggestedWeight={getInitialWeight(target.exercise_id, setNum)}
                  suggestedReps={getInitialReps(target.exercise_id, setNum)}
                  suggestedRpe={getInitialRpe(target.exercise_id, setNum)}
                  prWeight={target.pr_weight}
                  prEst1rm={target.pr_est_1rm}
                  logState={getLogState(target.exercise_id, setNum)}
                  onlog={(data) => handleLogSet(target.exercise_id, setNum, data)}
                  onunlog={() => handleUnlogSet(target.exercise_id, setNum)}
                />
              {/each}
            </div>

            {#if rpePrompts.has(target.exercise_id)}
              <div class="mx-3 mb-3 rounded-lg border border-error-200 bg-error-50 p-3">
                <div class="flex items-center gap-2">
                  <Icon name="warning" size="sm" class="text-error-600" />
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
                    onclick={() => applyWeightScaling(target.exercise_id, target.suggested_sets)}
                  >
                    Yes, scale down
                  </Btn>
                  <Btn
                    variant="ghost"
                    size="sm"
                    onclick={() => dismissRpePrompt(target.exercise_id)}
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
        <p class="text-sm text-surface-500">No workout plan associated with this session.</p>
      </Card>
    {/if}

    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900"> Finish Workout Session </span>
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
        <div class="mt-4 flex items-center justify-end gap-3">
          <Btn variant="danger" loading={canceling} onclick={() => (cancelDialogOpen = true)}>
            Cancel Workout
          </Btn>
          <Btn variant="primary" loading={completing} onclick={complete}>Complete Workout</Btn>
        </div>
      </div>
    </Card>
  {:else}
    <div class="flex justify-center py-20">
      <Card>
        <div class="py-8 text-center">
          <p class="text-lg font-semibold text-surface-900">No Active Workout</p>
          <p class="mt-1 text-sm text-surface-500">Start a workout from your training plan.</p>
          <div class="mt-4">
            <Btn variant="primary" href="/workouts/plans">Go to Plans</Btn>
          </div>
        </div>
      </Card>
    </div>
  {/if}

  <RestTimer
    onstart={(fn) => {
      startTimer = fn;
    }}
    oncomplete={() => speak('Rest finished. Time for your next set!')}
  />
</div>

<ConfirmDialog
  bind:open={cancelDialogOpen}
  title="Cancel Workout"
  variant="danger"
  message="Are you sure you want to cancel this workout session? All logged sets for this session will be discarded."
  confirmLabel="Cancel Workout"
  onconfirm={confirmCancel}
/>

<Modal bind:open={settingsModalOpen} title="Session Settings" size="md">
  <div class="space-y-4 divide-y divide-surface-100">
    <div class="flex items-center justify-between pt-1">
      <div>
        <p class="text-sm font-semibold text-surface-900">Audio Guide</p>
        <p class="text-xs text-surface-500">Spoken rest timer and set completion alerts</p>
      </div>
      <button
        type="button"
        class="duration-micro flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors {audioEnabled
          ? 'border-primary-300 bg-primary-50 text-primary-700'
          : 'border-surface-200 bg-surface-50 text-surface-500 hover:border-surface-300'}"
        onclick={toggleAudio}
      >
        <Icon name={audioEnabled ? 'volume-up' : 'volume-off'} size="sm" />
        {audioEnabled ? 'Audio On' : 'Audio Off'}
      </button>
    </div>

    <div class="flex items-center justify-between pt-4">
      <div>
        <p class="text-sm font-semibold text-surface-900">Auto-Start Rest Timer</p>
        <p class="text-xs text-surface-500">Automatically start timer when logging a set</p>
      </div>
      <button
        type="button"
        class="duration-micro flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors {autoStartRest
          ? 'border-primary-300 bg-primary-50 text-primary-700'
          : 'border-surface-200 bg-surface-50 text-surface-500 hover:border-surface-300'}"
        onclick={toggleAutoRest}
      >
        <Icon name={autoStartRest ? 'timer' : 'timer-off'} size="sm" />
        {autoStartRest ? 'Auto Start' : 'Manual'}
      </button>
    </div>

    {#if session?.autoreg_mode}
      <div class="flex items-center justify-between pt-4">
        <div>
          <p class="text-sm font-semibold text-surface-900">Autoregulation Mode</p>
          <p class="text-xs text-surface-500">Intensity scaling mode for this workout session</p>
        </div>
        <Badge
          variant={session.autoreg_mode === 'disabled' ? 'default' : 'primary'}
          class="capitalize"
        >
          {session.autoreg_mode}
        </Badge>
      </div>
    {/if}
  </div>
</Modal>
