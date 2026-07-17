<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { startWorkout } from '$lib/mutations/workout';
  import { goto } from '$app/navigation';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';

  const activeSession = liveQuery(() =>
    db.workout_session.filter((s) => !s.completed_at && !s.deleted_at).first()
  );

  const plans = liveQuery(() => db.workout_plan.filter((p) => !p.deleted_at).toArray());

  const lastSessionData = liveQuery(async () => {
    const list = await db.workout_session
      .filter((s) => !!s.completed_at && !s.deleted_at)
      .toArray();
    if (list.length === 0) return null;
    list.sort((a, b) => new Date(b.completed_at!).getTime() - new Date(a.completed_at!).getTime());
    const latest = list[0];
    const plan = latest.plan_id ? await db.workout_plan.get(latest.plan_id) : null;
    return { session: latest, plan };
  });

  let selectedPlanId = $state('');

  // Default select first plan if available
  $effect(() => {
    const p = $plans;
    if (p && p.length > 0 && !selectedPlanId) {
      selectedPlanId = p[0].id;
    }
  });

  let starting = $state(false);

  async function start() {
    if (!selectedPlanId) return;
    starting = true;
    const plan = ($plans ?? []).find((p) => p.id === selectedPlanId);
    const { ok } = await startWorkout(selectedPlanId, plan?.autoreg_mode || 'advisory');
    if (ok) {
      await goto('/workouts/active');
    }
    starting = false;
  }

  function formatRelativeTime(dateStr: string): string {
    const diffMs = Date.now() - new Date(dateStr).getTime();
    const diffDays = Math.floor(diffMs / 86400000);
    if (diffDays === 0) return 'today';
    if (diffDays === 1) return 'yesterday';
    return `${diffDays} days ago`;
  }
</script>

<div class="flex flex-col gap-4">
  {#if $activeSession}
    <div class="flex flex-col gap-3 rounded-lg border border-primary-100 bg-primary-50 p-4">
      <div class="flex items-center gap-2 text-primary-700">
        <Icon name="exercise" size="lg" class="animate-pulse text-primary-700" />
        <span class="text-sm font-semibold">Workout in progress!</span>
      </div>
      <p class="text-xs text-primary-600">
        You have a workout session currently active. Resume it to log your sets.
      </p>
      <Btn variant="primary" onclick={() => goto('/workouts/active')}>Resume Session</Btn>
    </div>
  {:else}
    <div class="flex flex-col gap-3">
      {#if $plans && $plans.length > 0}
        <div class="flex flex-col gap-1.5">
          <label for="workout-launcher-select" class="text-xs font-semibold text-surface-500">
            Select Training Plan
          </label>
          <div class="relative w-full">
            <select
              id="workout-launcher-select"
              class="w-full rounded-lg border border-surface-200 bg-surface-50 py-2.5 pr-10 pl-3 text-sm font-medium text-surface-700 transition-all outline-none focus:border-primary-500 focus:bg-surface-0 focus:ring-2 focus:ring-primary-500/20"
              bind:value={selectedPlanId}
            >
              {#each $plans as plan (plan.id)}
                <option value={plan.id}>{plan.name}</option>
              {/each}
            </select>
            <div
              class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-surface-400"
            >
              <Icon name="expand-more" />
            </div>
          </div>
        </div>

        <Btn variant="primary" loading={starting} onclick={start}>
          <span class="flex w-full items-center justify-center gap-2">
            <Icon name="play-arrow" size="sm" />
            Start Session
          </span>
        </Btn>
      {:else}
        <div
          class="rounded-lg border border-dashed border-surface-200 bg-surface-50/50 p-4 text-center"
        >
          <p class="text-xs text-surface-500">No workout plans created yet.</p>
          <a
            href="/workouts/plans"
            class="mt-2 inline-block text-xs font-semibold text-primary-600 hover:text-primary-700"
          >
            Create a Plan
          </a>
        </div>
      {/if}

      {#if $lastSessionData}
        <div
          class="flex items-center gap-1.5 border-t border-surface-100 pt-3 text-[11px] text-surface-400"
        >
          <Icon name="history" size="sm" />
          <span>
            Last completed:
            <strong class="text-surface-600">
              {$lastSessionData.plan?.name || 'Quick Workout'}
            </strong>
            ({formatRelativeTime($lastSessionData.session.completed_at!)})
          </span>
        </div>
      {/if}
    </div>
  {/if}
</div>
