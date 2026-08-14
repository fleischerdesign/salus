<script lang="ts">
  import { db } from '$lib/db/database';
  import type { FastingSession } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Input from '$components/ui/Input.svelte';
  import Select from '$components/ui/Select.svelte';
  import Checkbox from '$components/ui/Checkbox.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import {
    startFastingSession,
    endFastingSession,
    cancelFastingSession,
    deleteFastingSession
  } from '$lib/mutations/fasting';
  import { useQuery } from '$lib/db/use-query.svelte';

  const sessionsQuery = useQuery(() => db.notDeleted(db.fasting_session).toArray());
  const sessions = $derived(sessionsQuery.value);
  const loading = $derived(sessionsQuery.loading);

  const activeSession = $derived((sessions ?? []).find((s) => !s.ended_at) ?? null);
  const history = $derived(
    (sessions ?? [])
      .filter((s) => s.ended_at)
      .sort((a, b) => (b.started_at ?? '').localeCompare(a.started_at ?? ''))
  );

  let now = $state(Date.now());
  $effect(() => {
    const timer = setInterval(() => (now = Date.now()), 30_000);
    return () => clearInterval(timer);
  });

  const activeElapsedHours = $derived.by(() => {
    if (!activeSession) return null;
    return (now - new Date(activeSession.started_at).getTime()) / 3_600_000;
  });

  let formOpen = $state(false);
  let targetHours = $state('16');
  let fastingType = $state('intermittent');
  let waterOnly = $state(true);
  let saving = $state(false);

  let pendingCancel = $state<FastingSession | null>(null);
  let pendingDelete = $state<FastingSession | null>(null);

  async function handleStart() {
    saving = true;
    const { ok, error } = await startFastingSession({
      target_hours: Number(targetHours),
      fasting_type: fastingType,
      water_only: waterOnly
    });
    saving = false;
    if (ok) formOpen = false;
    else console.error('Failed to start fasting session:', error);
  }

  async function handleEnd() {
    if (!activeSession) return;
    const { ok, error } = await endFastingSession(activeSession.id);
    if (!ok) console.error('Failed to end fasting session:', error);
  }

  async function confirmCancel() {
    if (!pendingCancel) return;
    const { ok, error } = await cancelFastingSession(pendingCancel.id);
    if (!ok) console.error('Failed to cancel fasting session:', error);
    pendingCancel = null;
  }

  async function confirmDelete() {
    if (!pendingDelete) return;
    const { ok, error } = await deleteFastingSession(pendingDelete.id);
    if (!ok) console.error('Failed to delete fasting session:', error);
    pendingDelete = null;
  }

  function durationHours(s: FastingSession): number {
    const start = new Date(s.started_at).getTime();
    const end = s.ended_at ? new Date(s.ended_at).getTime() : Date.now();
    return Math.max(0, (end - start) / 3_600_000);
  }

  function formatDuration(hours: number): string {
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    return `${h}h ${m}m`;
  }

  function formatStarted(s: FastingSession): string {
    return new Date(s.started_at).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  }
</script>

<svelte:head><title>Salus — Fasting</title></svelte:head>

<div class="space-y-6">
  <PageHeader title="Fasting" subtitle="Track intermittent fasting sessions" icon="timer">
    {#snippet actions()}
      <PageHeaderAction
        icon="add"
        onclick={() => (formOpen = true)}
        disabled={activeSession != null}
      >
        Start Fast
      </PageHeaderAction>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="flex justify-center py-20">
      <Spinner />
    </div>
  {:else}
    {#if activeSession}
      <Card>
        <div class="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-center gap-4">
            <div
              class="flex h-14 w-14 items-center justify-center rounded-xl bg-success-50 text-success-600"
            >
              <Icon name="timer" size="lg" />
            </div>
            <div>
              <p class="text-xs font-semibold tracking-label text-surface-500 uppercase">
                Active fast
              </p>
              <p class="text-2xl font-semibold text-surface-900">
                {formatDuration(activeElapsedHours ?? 0)}
              </p>
              <p class="text-xs text-surface-500">
                started {formatStarted(activeSession)} · target {activeSession.target_hours}h
                {activeSession.water_only ? ' · water only' : ''}
              </p>
            </div>
          </div>
          <div class="flex gap-3">
            <Btn variant="ghost" onclick={() => (pendingCancel = activeSession)}>Cancel</Btn>
            <Btn variant="primary" onclick={handleEnd}>End Fast</Btn>
          </div>
        </div>
      </Card>
    {:else}
      <Card>
        <EmptyState
          icon="timer"
          title="Not fasting right now"
          description="Start a session to track your fasting window and log your fasting duration."
        >
          <Btn variant="primary" onclick={() => (formOpen = true)}>Start Fast</Btn>
        </EmptyState>
      </Card>
    {/if}

    {#if history.length > 0}
      <Card title="History" padding={false} class="overflow-hidden">
        <div class="divide-y divide-surface-100">
          {#each history as s}
            <div class="flex items-center justify-between gap-3 px-6 py-3">
              <div>
                <p class="text-sm font-semibold text-surface-900">
                  {formatDuration(durationHours(s))}
                </p>
                <p class="text-xs text-surface-500">
                  {formatStarted(s)} · {s.target_hours}h target
                </p>
              </div>
              <button
                class="flex h-8 w-8 items-center justify-center rounded-md text-surface-400 transition-colors hover:bg-error-50 hover:text-error-600"
                onclick={() => (pendingDelete = s)}
                aria-label="Delete session"
              >
                <Icon name="delete" size="sm" />
              </button>
            </div>
          {/each}
        </div>
      </Card>
    {/if}
  {/if}

  <Modal bind:open={formOpen} title="Start Fast" size="sm">
    <div class="space-y-4">
      <Input
        name="target_hours"
        type="number"
        step="0.5"
        min={1}
        label="Target duration (hours)"
        bind:value={targetHours}
      />
      <Select
        name="fasting_type"
        label="Type"
        options={[
          { value: 'intermittent', label: 'Intermittent' },
          { value: 'prolonged', label: 'Prolonged' },
          { value: 'religious', label: 'Religious' },
          { value: 'water_fast', label: 'Water fast' }
        ]}
        bind:value={fastingType}
      />
      <Checkbox name="water_only" label="Water only" bind:checked={waterOnly} />
      <div class="flex justify-end gap-3 pt-2">
        <Btn variant="ghost" onclick={() => (formOpen = false)}>Cancel</Btn>
        <Btn variant="primary" onclick={handleStart} loading={saving}>Start</Btn>
      </div>
    </div>
  </Modal>

  <ConfirmDialog
    open={pendingCancel != null}
    title="Cancel fast?"
    message="This discards the active fasting session without recording a duration."
    confirmLabel="Cancel Fast"
    onconfirm={confirmCancel}
    oncancel={() => (pendingCancel = null)}
  />

  <ConfirmDialog
    open={pendingDelete != null}
    title="Delete session?"
    message="This removes the session and its recorded fasting duration."
    confirmLabel="Delete"
    onconfirm={confirmDelete}
    oncancel={() => (pendingDelete = null)}
  />
</div>
