<script lang="ts">
  import { db } from '$lib/db/database';
  import { startWorkout } from '$lib/mutations/workout';
  import { goto } from '$app/navigation';
  import { MS_PER_DAY } from '$lib/utils/datetime';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Select from '$components/ui/Select.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';

  const activeSessionQuery = useQuery(() =>
    db.workout_session.filter((s) => !s.completed_at && !s.deleted_at).first()
  );
  const activeSession = $derived(activeSessionQuery.value);

  const plansQuery = useQuery(() => db.workout_plan.filter((p) => !p.deleted_at).toArray());
  const plans = $derived(plansQuery.value);
  const planOptions = $derived((plans ?? []).map((p) => ({ value: p.id, label: p.name })));

  const lastSessionDataQuery = useQuery(async () => {
    const list = await db.workout_session
      .filter((s) => !!s.completed_at && !s.deleted_at)
      .toArray();
    if (list.length === 0) return null;
    list.sort((a, b) => new Date(b.completed_at!).getTime() - new Date(a.completed_at!).getTime());
    const latest = list[0];
    const plan = latest.plan_id ? await db.workout_plan.get(latest.plan_id) : null;
    return { session: latest, plan };
  });
  const lastSessionData = $derived(lastSessionDataQuery.value);

  let selectedPlanId = $state('');

  // Default select first plan if available
  $effect(() => {
    const p = plans;
    if (p && p.length > 0 && !selectedPlanId) {
      selectedPlanId = p[0].id;
    }
  });

  let starting = $state(false);

  async function start() {
    if (!selectedPlanId) return;
    starting = true;
    const plan = (plans ?? []).find((p) => p.id === selectedPlanId);
    const { ok } = await startWorkout(selectedPlanId, plan?.autoreg_mode || 'advisory');
    if (ok) {
      await goto('/workouts/active');
    }
    starting = false;
  }

  function formatRelativeTime(dateStr: string): string {
    const diffMs = Date.now() - new Date(dateStr).getTime();
    const diffDays = Math.floor(diffMs / MS_PER_DAY);
    if (diffDays === 0) return 'today';
    if (diffDays === 1) return 'yesterday';
    return `${diffDays} days ago`;
  }
</script>

<div class="flex flex-col gap-4">
  {#if activeSession}
    <div class="border-primary-100 bg-primary-50 flex flex-col gap-3 rounded-lg border p-4">
      <div class="text-primary-700 flex items-center gap-2">
        <Icon name="exercise" size="lg" class="text-primary-700 animate-pulse" />
        <span class="text-sm font-semibold">Workout in progress!</span>
      </div>
      <p class="text-primary-600 text-xs">
        You have a workout session currently active. Resume it to log your sets.
      </p>
      <Btn variant="primary" onclick={() => goto('/workouts/active')}>Resume Session</Btn>
    </div>
  {:else}
    <div class="flex flex-col gap-3">
      {#if plans && (plans ?? []).length > 0}
        <Select label="Select Training Plan" options={planOptions} bind:value={selectedPlanId} />

        <Btn variant="primary" loading={starting} onclick={start}>
          <span class="flex w-full items-center justify-center gap-2">
            <Icon name="play-arrow" size="sm" />
            Start Session
          </span>
        </Btn>
      {:else}
        <div
          class="rounded-2xl border border-dashed border-[var(--border-subtle)] bg-[var(--bg-surface-50)]/50 p-4 text-center"
        >
          <p class="text-xs text-[var(--text-muted)]">Noch keine Trainingspläne erstellt.</p>
          <a
            href="/workouts/plans"
            class="mt-2 inline-block text-xs font-bold text-[var(--color-primary)] hover:underline"
          >
            Trainingsplan erstellen &rarr;
          </a>
        </div>
      {/if}

      {#if lastSessionData}
        <div
          class="flex items-center gap-1.5 border-t border-[var(--border-subtle)] pt-3 text-[10px] text-[var(--text-soft)]"
        >
          <Icon name="history" size="sm" />
          <span>
            Zuletzt absolviert:
            <strong class="font-bold text-[var(--text-main)]">
              {lastSessionData.plan?.name || 'Freies Training'}
            </strong>
            ({formatRelativeTime(lastSessionData.session.completed_at!)})
          </span>
        </div>
      {/if}
    </div>
  {/if}
</div>
