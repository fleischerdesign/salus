<script lang="ts">
  import { liveQuery } from 'dexie';
  import type { components } from '$lib/api/schema';
  import { db } from '$lib/db/database';
  import type { MetricType } from '$lib/db/types';
  import { createGoal, deleteGoal } from '$lib/mutations/goal';
  import { fetchGoalViews } from '$lib/analytics/views/goal-views';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import Select from '$components/ui/Select.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import ProgressBar from '$components/ui/ProgressBar.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import SegmentedControl from '$components/ui/SegmentedControl.svelte';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

  let goals = liveQuery(() => fetchGoalViews());
  let metrics = liveQuery(() =>
    db.metric_type.toArray().then((arr) => arr.filter((m) => !m.deleted_at))
  );

  // Form state
  let showForm = $state(false);
  let formMetricId = $state('');
  let formTarget = $state('');
  let formDirection = $state('increase');
  let formFrequency = $state('daily');
  let formDeadline = $state('');
  let formError = $state('');
  let saving = $state(false);

  // Delete state
  let goalToDelete = $state<{ id: string } | null>(null);
  let deleteDialogOpen = $state(false);

  const directionOptions = [
    { value: 'increase', label: 'Increase' },
    { value: 'decrease', label: 'Decrease' }
  ];

  const frequencyOptions = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'once', label: 'Once' }
  ];

  function openForm() {
    formMetricId = '';
    formTarget = '';
    formDirection = 'increase';
    formFrequency = 'daily';
    formDeadline = '';
    formError = '';
    showForm = true;
  }

  function closeForm() {
    showForm = false;
  }

  async function saveGoal(e: SubmitEvent) {
    e.preventDefault();
    formError = '';
    saving = true;
    const { ok, error } = await createGoal(
      formMetricId,
      parseFloat(formTarget),
      formDirection as 'increase' | 'decrease',
      formFrequency as 'daily' | 'weekly' | 'once',
      formFrequency === 'once' && formDeadline ? formDeadline : undefined
    );
    saving = false;
    if (!ok) {
      formError = error || 'Failed to create goal';
      return;
    }
    closeForm();
  }

  async function confirmDelete() {
    if (!goalToDelete) return;
    const target = goalToDelete;
    goalToDelete = null;
    await deleteGoal(target.id);
  }

  function progressVariant(status: string): 'success' | 'error' | 'info' {
    if (status === 'fulfilled') return 'success';
    if (status === 'missed') return 'error';
    return 'info';
  }

  function statusColor(status: string): string {
    if (status === 'fulfilled') return 'text-success-600';
    if (status === 'missed') return 'text-error-500';
    return 'text-primary-600';
  }

  function resetLabel(g: { frequency: string; deadline?: string | null }): string {
    if (g.frequency === 'once' && g.deadline) {
      return `due ${new Date(g.deadline).toLocaleDateString()}`;
    }
    if (g.frequency === 'daily') return 'daily reset';
    if (g.frequency === 'weekly') return 'weekly reset';
    return '';
  }

  function formatValue(v: number | null | undefined): string {
    if (v === null || v === undefined) return '—';
    return v >= 1000
      ? v.toLocaleString(undefined, { maximumFractionDigits: 1 })
      : v.toFixed(1).replace(/\.0$/, '');
  }

  const metricOptions = $derived(
    ($metrics ?? []).map((m) => ({
      value: String(m.id),
      label: `${m.name}${m.unit ? ` (${m.unit})` : ''}`
    }))
  );
</script>

<svelte:head><title>Salus — Goals</title></svelte:head>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-semibold text-surface-900">Goals</h1>
      <p class="text-sm text-surface-500">Set and track your health targets.</p>
    </div>
    <Btn variant="primary" onclick={openForm}>
      <Icon name="add" size="sm" />New Goal
    </Btn>
  </div>

  {#if !$goals || !$metrics}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else if $goals.length === 0}
    <EmptyState
      title="No goals yet"
      description="Set your first health goal to track progress."
      icon="track-changes"
    >
      <Btn variant="primary" onclick={openForm}>+ New Goal</Btn>
    </EmptyState>
  {:else}
    <div class="grid [grid-template-columns:repeat(auto-fill,minmax(300px,1fr))] gap-4">
      {#each $goals as g, i (g.id)}
        <div in:fade={{ ...staggerFade(i) }}>
          <a href="/goals/{g.id}" class="group/card block">
            <Card padding={false} class="cursor-pointer transition-shadow hover:shadow-md">
              {#snippet header()}
                <div class="flex items-center gap-3">
                  <div
                    class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg"
                    style="background-color: {g.metric_color}20; color: {g.metric_color}"
                  >
                    <Icon name={g.metric_icon || 'track-changes'} size="sm" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <p
                      class="truncate text-sm font-semibold text-surface-900 transition-colors group-hover/card:text-primary-600"
                    >
                      {g.metric_name}
                    </p>
                    <p class="text-xs text-surface-400 capitalize">{g.frequency}</p>
                  </div>
                  <button
                    type="button"
                    class="duration-micro flex h-7 w-7 items-center justify-center rounded text-surface-400 transition-colors hover:bg-error-50 hover:text-error-500"
                    aria-label="Delete goal"
                    onclick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      goalToDelete = g;
                      deleteDialogOpen = true;
                    }}
                  >
                    <Icon name="close" size="sm" />
                  </button>
                </div>
              {/snippet}

              <div class="p-6">
                <div class="flex items-baseline gap-2">
                  <Icon
                    name={g.direction === 'increase' ? 'trending-up' : 'trending-down'}
                    size="sm"
                    class={g.direction === 'increase' ? 'text-success-600' : 'text-primary-500'}
                  />
                  <span class="text-2xl font-bold text-surface-900 tabular-nums">
                    {formatValue(g.progress.current_value)}
                  </span>
                  <span class="text-sm text-surface-400">
                    / {formatValue(g.target_value)}{g.metric_unit ? ` ${g.metric_unit}` : ''}
                  </span>
                </div>

                <div class="mt-3">
                  <ProgressBar
                    value={g.progress.percent}
                    max={100}
                    variant={progressVariant(g.progress.status)}
                    height="md"
                  />
                </div>

                <div class="mt-3 flex items-center justify-between">
                  <span class="text-xs font-semibold capitalize {statusColor(g.progress.status)}">
                    {g.progress.status}
                  </span>
                  <span class="text-xs text-surface-400">{resetLabel(g)}</span>
                </div>

                {#if g.forecast}
                  <div class="mt-4 border-t border-surface-100 pt-3 text-xs">
                    <div class="mb-1.5 flex items-center justify-between">
                      <span class="text-surface-400">Projection to Deadline</span>
                      <span
                        class="rounded px-1.5 py-0.5 text-[10px] font-semibold"
                        class:bg-success-50={g.forecast.on_track}
                        class:text-success-600={g.forecast.on_track}
                        class:bg-error-50={!g.forecast.on_track}
                        class:text-error-600={!g.forecast.on_track}
                      >
                        {g.forecast.on_track ? 'ON TRACK' : 'OFF TRACK'}
                      </span>
                    </div>
                    <div class="flex justify-between text-surface-500">
                      <span>Est. Target Value</span>
                      <span class="font-medium text-surface-700">
                        {formatValue(g.forecast.predicted)}{g.metric_unit
                          ? ` ${g.metric_unit}`
                          : ''}
                      </span>
                    </div>
                    <div class="mt-0.5 flex justify-between text-surface-400">
                      <span>80% Conf. Range</span>
                      <span>
                        [{formatValue(g.forecast.ci_lower)} – {formatValue(g.forecast.ci_upper)}]
                      </span>
                    </div>
                  </div>
                {/if}
              </div>
            </Card>
          </a>
        </div>
      {/each}
    </div>
  {/if}
</div>

<Modal title="New Goal" bind:open={showForm}>
  <form onsubmit={saveGoal} class="flex flex-col gap-4">
    <FormField label="Metric" required>
      <Select name="metric_type_id" options={metricOptions} bind:value={formMetricId} />
    </FormField>

    <FormField label="Target Value" required>
      <Input
        name="target_value"
        type="number"
        step="0.1"
        bind:value={formTarget}
        required
        placeholder="e.g. 10000"
      />
    </FormField>

    <div class="space-y-2">
      <span class="text-sm font-medium text-surface-700">Direction</span>
      <SegmentedControl options={directionOptions} bind:value={formDirection} />
    </div>

    <div class="space-y-2">
      <span class="text-sm font-medium text-surface-700">Frequency</span>
      <SegmentedControl options={frequencyOptions} bind:value={formFrequency} />
    </div>

    {#if formFrequency === 'once'}
      <FormField label="Deadline">
        <Input name="deadline" type="date" bind:value={formDeadline} />
      </FormField>
    {/if}

    {#if formError}
      <p class="text-sm text-error-500">{formError}</p>
    {/if}
    <div class="flex justify-end gap-2">
      <Btn variant="ghost" onclick={closeForm}>Cancel</Btn>
      <Btn variant="primary" type="submit" loading={saving}>Create Goal</Btn>
    </div>
  </form>
</Modal>

<ConfirmDialog
  bind:open={deleteDialogOpen}
  title="Delete Goal"
  variant="danger"
  message="Delete this goal? This cannot be undone."
  confirmLabel="Delete"
  onconfirm={confirmDelete}
  oncancel={() => {
    goalToDelete = null;
  }}
/>
