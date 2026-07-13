<script lang="ts">
  import { liveQuery } from 'dexie';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import type { WorkoutPlan } from '$lib/db/types';
  import { mutate, nextTempId } from '$lib/db/mutate';
  import { mutateDomain } from '$lib/db/mutate-domain';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import Textarea from '$components/ui/Textarea.svelte';
  import Select from '$components/ui/Select.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

  let plans = liveQuery(() =>
    db.workout_plan
      .toArray()
      .then((arr) => arr.filter((p) => !p.deleted_at).sort((a, b) => a.position - b.position))
  );

  let exercises = liveQuery(() =>
    db.exercise.toArray().then((arr) => arr.filter((e) => !e.deleted_at))
  );
  let planExercises = liveQuery(() =>
    db.workout_plan_exercise.toArray().then((arr) => arr.filter((pe) => !pe.deleted_at))
  );

  let showForm = $state(false);
  let planName = $state('');
  let planDescription = $state('');
  let planAutoreg = $state('advisory');
  let planError = $state('');
  let saving = $state(false);

  let planToDelete = $state<WorkoutPlan | null>(null);
  let deleteDialogOpen = $state(false);

  const autoregOptions = [
    { value: 'advisory', label: 'Advisory' },
    { value: 'guided', label: 'Guided' },
    { value: 'disabled', label: 'Disabled' }
  ];

  function openForm() {
    planName = '';
    planDescription = '';
    planAutoreg = 'advisory';
    planError = '';
    showForm = true;
  }

  function exerciseCount(planId: number): number {
    return ($planExercises ?? []).filter((pe) => pe.plan_id === planId).length;
  }

  function exerciseNames(planId: number): {
    name: string;
    target_sets: number | null;
    target_reps: number | null;
    target_rpe: number | null;
  }[] {
    const exById = new Map(($exercises ?? []).map((e) => [e.id, e]));
    return ($planExercises ?? [])
      .filter((pe) => pe.plan_id === planId)
      .sort((a, b) => a.sequence - b.sequence)
      .map((pe) => ({
        name: exById.get(pe.exercise_id)?.name ?? 'Unknown',
        target_sets: pe.target_sets,
        target_reps: pe.target_reps,
        target_rpe: pe.target_rpe
      }));
  }

  async function createPlan(e: SubmitEvent) {
    e.preventDefault();
    planError = '';
    saving = true;
    const data = {
      name: planName,
      description: planDescription || undefined,
      autoreg_mode: planAutoreg,
      position: ($plans ?? []).length
    };
    const { ok, error } = await mutate({
      table: 'workout_plan',
      type: 'create',
      data: data as Record<string, unknown>,
      optimistic: {
        id: nextTempId(),
        user_id: 0,
        ...data,
        created_at: new Date().toISOString(),
        updated_at: null,
        deleted_at: null
      }
    });
    saving = false;
    if (!ok) {
      planError = error || 'Failed to create plan';
      return;
    }
    showForm = false;
  }

  async function confirmDelete() {
    if (!planToDelete) return;
    const target = planToDelete;
    planToDelete = null;
    await mutate({
      table: 'workout_plan',
      type: 'delete',
      optimistic: { id: target.id },
      realId: target.id
    });
  }

  async function startSession(planId: number) {
    const plan = ($plans ?? []).find((p) => p.id === planId);
    const now = new Date().toISOString();
    const tempId = nextTempId();
    const { ok } = await mutateDomain({
      url: `/api/v1/workouts/sessions/start?plan_id=${planId}`,
      method: 'POST',
      optimisticTable: 'workout_session',
      optimisticData: {
        id: tempId,
        user_id: 0,
        plan_id: planId,
        plan_name: plan?.name ?? '',
        started_at: now,
        completed_at: null,
        recovery_score: null,
        autoreg_mode: plan?.autoreg_mode || 'advisory',
        notes: null,
        effort_rating: null,
        created_at: now,
        updated_at: null,
        deleted_at: null
      },
      optimisticId: tempId,
      responseTable: 'workout_session'
    });
    if (ok) await goto('/workouts/active');
  }
</script>

<svelte:head><title>Salus — Workout Plans</title></svelte:head>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <a
        href="/workouts"
        class="duration-micro flex items-center gap-1 text-sm text-surface-500 no-underline transition-colors hover:text-surface-700"
      >
        <Icon name="arrow-back" size="sm" />Workouts
      </a>
      <h1 class="mt-1 text-2xl font-semibold text-surface-900">Training Plans</h1>
    </div>
    <Btn variant="primary" onclick={openForm}>
      <Icon name="add" size="sm" />New Plan
    </Btn>
  </div>

  {#if !$plans}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else if $plans.length === 0}
    <EmptyState
      title="No workout plans"
      description="Create your first training plan to get started."
      icon="assignment"
    >
      <Btn variant="primary" onclick={openForm}>+ New Plan</Btn>
    </EmptyState>
  {:else}
    <div class="grid [grid-template-columns:repeat(auto-fill,minmax(320px,1fr))] gap-4">
      {#each $plans as plan, i (plan.id)}
        <div in:fade={{ ...staggerFade(i) }}>
          <Card padding={false} hoverable>
            {#snippet header()}
              <div class="flex items-center gap-3">
                <div class="min-w-0 flex-1">
                  <a href="/workouts/plans/{plan.id}" class="block">
                    <p class="truncate text-sm font-semibold text-surface-900">{plan.name}</p>
                  </a>
                  <div class="mt-1 flex items-center gap-1.5">
                    <Badge variant={plan.autoreg_mode === 'disabled' ? 'default' : 'primary'}>
                      {plan.autoreg_mode}
                    </Badge>
                    <span class="text-xs text-surface-400">{exerciseCount(plan.id)} exercises</span>
                  </div>
                </div>
                <button
                  type="button"
                  class="duration-micro flex h-7 w-7 items-center justify-center rounded text-surface-400 transition-colors hover:bg-error-50 hover:text-error-500"
                  aria-label="Delete plan"
                  onclick={() => {
                    planToDelete = plan;
                    deleteDialogOpen = true;
                  }}
                >
                  <Icon name="delete" size="sm" />
                </button>
              </div>
            {/snippet}

            <div class="p-6">
              {#if plan.description}
                <p class="mb-3 text-sm text-surface-500">{plan.description}</p>
              {/if}

              {#if exerciseNames(plan.id).length > 0}
                <ul class="space-y-1 text-xs text-surface-500">
                  {#each exerciseNames(plan.id) as pe (pe.name)}
                    <li class="flex items-center justify-between gap-2">
                      <span class="truncate">{pe.name}</span>
                      <span class="shrink-0 font-medium text-surface-400"
                        >{pe.target_sets}×{pe.target_reps} @ RPE {pe.target_rpe ?? '—'}</span
                      >
                    </li>
                  {/each}
                </ul>
              {:else}
                <p class="text-xs text-surface-400">No exercises added yet.</p>
              {/if}

              <div class="mt-4">
                <Btn variant="primary" size="sm" onclick={() => startSession(plan.id)}>
                  <Icon name="play-arrow" size="sm" />Start Workout
                </Btn>
              </div>
            </div>
          </Card>
        </div>
      {/each}
    </div>
  {/if}
</div>

<Modal title="New Workout Plan" bind:open={showForm}>
  <form onsubmit={createPlan} class="flex flex-col gap-4">
    <FormField label="Plan Name" required>
      <Input name="name" bind:value={planName} required placeholder="e.g. Push/Pull/Legs" />
    </FormField>
    <FormField label="Description">
      <Textarea
        name="description"
        bind:value={planDescription}
        rows={2}
        placeholder="Optional description"
      />
    </FormField>
    <FormField label="Autoregulation Mode">
      <Select name="autoreg_mode" options={autoregOptions} bind:value={planAutoreg} />
    </FormField>
    {#if planError}<p class="text-sm text-error-500">{planError}</p>{/if}
    <div class="flex justify-end gap-2">
      <Btn variant="ghost" onclick={() => (showForm = false)}>Cancel</Btn>
      <Btn variant="primary" type="submit" loading={saving}>Create Plan</Btn>
    </div>
  </form>
</Modal>

<ConfirmDialog
  bind:open={deleteDialogOpen}
  title="Delete Plan"
  variant="danger"
  message="Delete &quot;{planToDelete?.name}&quot;? This cannot be undone."
  confirmLabel="Delete"
  onconfirm={confirmDelete}
  oncancel={() => {
    planToDelete = null;
  }}
/>
