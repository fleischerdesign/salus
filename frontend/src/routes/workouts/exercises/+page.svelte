<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { Exercise } from '$lib/db/types';
  import { mutate, nextTempId } from '$lib/db/mutate';
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

  let allExercises = liveQuery(() =>
    db.exercise.toArray().then((arr) => arr.filter((e) => !e.deleted_at))
  );

  let searchQuery = $state('');
  let muscleFilter = $state('');
  let equipFilter = $state('');

  let showForm = $state(false);
  let exName = $state('');
  let exEquipment = $state('barbell');
  let exPrimaryMuscles = $state('');
  let exDescription = $state('');
  let exInstructions = $state('');
  let exVideoUrl = $state('');
  let formError = $state('');
  let saving = $state(false);

  let exToDelete = $state<Exercise | null>(null);
  let deleteDialogOpen = $state(false);

  const equipmentOptions = [
    { value: '', label: 'All Equipment' },
    { value: 'barbell', label: 'Barbell' },
    { value: 'dumbbell', label: 'Dumbbell' },
    { value: 'machine', label: 'Machine' },
    { value: 'bodyweight', label: 'Bodyweight' },
    { value: 'cable', label: 'Cable' },
    { value: 'kettlebell', label: 'Kettlebell' }
  ];

  let muscleOptions = $derived.by(() => {
    const muscles = new Set<string>();
    for (const ex of $allExercises ?? []) {
      for (const m of ex.primary_muscles?.split(',') ?? []) {
        const trimmed = m.trim();
        if (trimmed) muscles.add(trimmed.toLowerCase());
      }
    }
    return [
      { value: '', label: 'All Muscles' },
      ...Array.from(muscles)
        .sort()
        .map((m) => ({
          value: m,
          label: m.charAt(0).toUpperCase() + m.slice(1)
        }))
    ];
  });

  let filteredExercises = $derived.by(() => {
    const q = searchQuery.toLowerCase().trim();
    const m = muscleFilter.toLowerCase();
    const e = equipFilter.toLowerCase();
    return ($allExercises ?? []).filter((ex) => {
      const matchesQuery = !q || ex.name.toLowerCase().includes(q);
      const matchesMuscle = !m || (ex.primary_muscles ?? '').toLowerCase().includes(m);
      const matchesEquip = !e || (ex.equipment ?? '').toLowerCase() === e;
      return matchesQuery && matchesMuscle && matchesEquip;
    });
  });

  function openForm() {
    exName = '';
    exEquipment = 'barbell';
    exPrimaryMuscles = '';
    exDescription = '';
    exInstructions = '';
    exVideoUrl = '';
    formError = '';
    showForm = true;
  }

  async function createExercise(e: SubmitEvent) {
    e.preventDefault();
    formError = '';
    saving = true;
    const data = {
      name: exName,
      equipment: exEquipment,
      primary_muscles: exPrimaryMuscles,
      description: exDescription || undefined,
      instructions: exInstructions || undefined,
      video_url: exVideoUrl || undefined
    };
    const { ok, error } = await mutate({
      table: 'exercise',
      type: 'create',
      data: data as Record<string, unknown>,
      optimistic: {
        id: nextTempId(),
        user_id: 0,
        ...data,
        secondary_muscles: null,
        suggested_rest_seconds: null,
        created_at: new Date().toISOString(),
        updated_at: null,
        deleted_at: null
      }
    });
    saving = false;
    if (!ok) {
      formError = error || 'Failed to create exercise';
      return;
    }
    showForm = false;
  }

  async function confirmDelete() {
    if (!exToDelete) return;
    const target = exToDelete;
    exToDelete = null;
    await mutate({
      table: 'exercise',
      type: 'delete',
      optimistic: { id: target.id },
      realId: target.id
    });
  }

  function formatMuscle(m: string): string {
    return (m ?? '').split(',')[0].trim();
  }
</script>

<svelte:head><title>Salus — Exercise Library</title></svelte:head>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <a
        href="/workouts"
        class="flex items-center gap-1 text-sm text-surface-500 no-underline transition-colors duration-150 hover:text-surface-700"
      >
        <Icon name="arrow-back" size="sm" />Workouts
      </a>
      <h1 class="mt-1 text-2xl font-semibold text-surface-900">Exercise Library</h1>
    </div>
    <Btn variant="primary" onclick={openForm}>
      <Icon name="add" size="sm" />New Exercise
    </Btn>
  </div>

  {#if !$allExercises}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else}
    <div class="flex flex-wrap gap-3">
      <div class="relative min-w-[200px] flex-1">
        <span class="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-surface-400">
          <Icon name="search" size="sm" />
        </span>
        <input
          type="text"
          placeholder="Search exercises…"
          bind:value={searchQuery}
          class="h-10 w-full rounded-md border border-surface-300 bg-surface-50 pr-3 pl-9 text-sm text-surface-900 transition-colors duration-150 hover:border-surface-400 focus:border-primary-500 focus:bg-surface-0 focus:ring-1 focus:ring-primary-500 focus:outline-none"
        />
      </div>
      <div class="w-40">
        <Select name="muscle" options={muscleOptions} bind:value={muscleFilter} />
      </div>
      <div class="w-40">
        <Select name="equipment" options={equipmentOptions} bind:value={equipFilter} />
      </div>
    </div>

    {#if filteredExercises.length === 0}
      <EmptyState
        title="No exercises found"
        description={$allExercises.length === 0
          ? 'Add exercises to your catalog.'
          : 'No exercises match your filters.'}
        icon="exercise"
      >
        {#if $allExercises.length === 0}
          <Btn variant="primary" onclick={openForm}>+ New Exercise</Btn>
        {/if}
      </EmptyState>
    {:else}
      <div class="grid [grid-template-columns:repeat(auto-fill,minmax(300px,1fr))] gap-4">
        {#each filteredExercises as ex (ex.id)}
          <a href="/workouts/exercises/{ex.id}" class="no-underline">
            <Card padding={false} hoverable>
              {#snippet header()}
                <div class="flex items-center gap-3">
                  <div class="min-w-0 flex-1">
                    <p class="truncate text-sm font-semibold text-surface-900">
                      {ex.name}
                    </p>
                    <div class="mt-1 flex items-center gap-1.5">
                      <Badge variant="default" class="capitalize">{ex.equipment}</Badge>
                      <Badge variant="primary" class="capitalize"
                        >{formatMuscle(ex.primary_muscles ?? '')}</Badge
                      >
                    </div>
                  </div>
                  {#if ex.video_url}
                    <Icon name="smart-display" size="sm" class="text-surface-400" />
                  {/if}
                </div>
              {/snippet}
              {#if ex.description}
                <div class="p-4">
                  <p class="truncate text-xs text-surface-400">
                    {ex.description}
                  </p>
                </div>
              {/if}
            </Card>
          </a>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<Modal title="New Exercise" bind:open={showForm}>
  <form onsubmit={createExercise} class="flex flex-col gap-4">
    <FormField label="Name" required>
      <Input name="name" bind:value={exName} required placeholder="e.g. Bench Press" />
    </FormField>
    <FormField label="Equipment">
      <Select
        name="equipment"
        options={equipmentOptions.filter((o) => o.value !== '')}
        bind:value={exEquipment}
      />
    </FormField>
    <FormField label="Primary Muscles" required>
      <Input name="muscles" bind:value={exPrimaryMuscles} required placeholder="chest,triceps" />
    </FormField>
    <FormField label="Description">
      <Textarea
        name="description"
        bind:value={exDescription}
        rows={2}
        placeholder="Brief description"
      />
    </FormField>
    <FormField label="Instructions">
      <Textarea
        name="instructions"
        bind:value={exInstructions}
        rows={3}
        placeholder="Step-by-step form cues"
      />
    </FormField>
    <FormField label="Video URL">
      <Input name="video_url" bind:value={exVideoUrl} placeholder="https://…" />
    </FormField>
    {#if formError}
      <p class="text-sm text-error-500">{formError}</p>
    {/if}
    <div class="flex justify-end gap-2">
      <Btn variant="ghost" onclick={() => (showForm = false)}>Cancel</Btn>
      <Btn variant="primary" type="submit" loading={saving}>Create</Btn>
    </div>
  </form>
</Modal>

<ConfirmDialog
  bind:open={deleteDialogOpen}
  title="Delete Exercise"
  variant="danger"
  message="Delete &quot;{exToDelete?.name}&quot;? This cannot be undone."
  confirmLabel="Delete"
  onconfirm={confirmDelete}
  oncancel={() => {
    exToDelete = null;
  }}
/>
