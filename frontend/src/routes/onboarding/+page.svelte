<script lang="ts">
  import { db } from '$lib/db/database';
  import { createToken as issueOnboardingToken } from '$lib/mutations/account';
  import { dismissOnboarding } from '$lib/mutations/account';
  import { createMeasurement } from '$lib/mutations/measurement';
  import { createGoal as createGoalMutation } from '$lib/mutations/goal';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import StepIndicator from '$components/ui/StepIndicator.svelte';
  import CopyToClipboard from '$components/ui/CopyToClipboard.svelte';
  import { goto } from '$app/navigation';

  let step = $state(1);
  let token = $state('');
  let webhookUrl = $state('');
  let entryMetricId = $state(0);
  let entryValue = $state('');
  let goalMetricId = $state(0);
  let goalTarget = $state('');
  let error = $state('');

  async function createToken() {
    const resp = await issueOnboardingToken('Webhook Token', 'ingest:write');
    if (resp.ok && resp.data) {
      const data = resp.data as { token: string; webhook_url: string };
      token = data.token;
      webhookUrl = data.webhook_url;
    }
  }

  async function createEntry() {
    error = '';
    const resp = await createMeasurement(String(entryMetricId), { value: entryValue });
    if (!resp.ok) {
      error = resp.error ?? 'Failed';
      return;
    }
    step = 3;
  }

  async function createGoal() {
    error = '';
    const resp = await createGoalMutation(
      String(goalMetricId),
      parseFloat(goalTarget),
      'increase',
      'daily'
    );
    if (!resp.ok) {
      error = resp.error ?? 'Failed';
      return;
    }
    step = 4;
  }

  async function dismiss() {
    await dismissOnboarding();
    const profiles = await db.user_profile.toArray();
    const profile = profiles[0];
    if (profile) {
      await db.user_profile.put({ ...profile, onboarding_dismissed: true });
    }
    await goto('/');
  }
</script>

<svelte:head><title>Salus — Onboarding</title></svelte:head>

<div class="mx-auto max-w-lg space-y-6 pt-8">
  <div class="flex flex-col items-center gap-4">
    <StepIndicator total={3} current={step} />
  </div>

  {#if step === 1}
    <Card title="Connect a Data Source">
      <p class="text-surface-600 mb-4 text-sm">
        Get an API token to push health data from apps and devices.
      </p>
      <Btn variant="primary" onclick={createToken}>
        <Icon name="key" size="sm" />Generate Token
      </Btn>
      {#if token}
        <div class="mt-4 space-y-3">
          <div>
            <p class="text-surface-500 mb-1 text-xs font-medium">API Token</p>
            <CopyToClipboard value={token} label="API Token" />
          </div>
          {#if webhookUrl}
            <div>
              <p class="text-surface-500 mb-1 text-xs font-medium">Webhook URL</p>
              <CopyToClipboard value={webhookUrl} label="Webhook URL" />
            </div>
          {/if}
        </div>
      {/if}
      <div class="mt-4 flex justify-end">
        <Btn variant="primary" onclick={() => (step = 2)}>Next</Btn>
      </div>
    </Card>
  {:else if step === 2}
    <Card title="Ersten Messwert erfassen">
      <div class="flex flex-col gap-4">
        <Input
          label="Metrik-Code / Typ-ID"
          name="metric_id"
          type="number"
          bind:value={entryMetricId}
          required
        />
        <Input
          label="Messwert"
          name="value"
          bind:value={entryValue}
          required
          placeholder="z. B. 75.5"
        />
        {#if error}<p class="text-xs font-medium text-rose-500">{error}</p>{/if}
        <div class="flex justify-between">
          <Btn variant="ghost" onclick={() => (step = 1)}>Zurück</Btn>
          <Btn variant="primary" onclick={createEntry}>Eintrag speichern</Btn>
        </div>
      </div>
    </Card>
  {:else if step === 3}
    <Card title="Erstes Ziel setzen">
      <div class="flex flex-col gap-4">
        <Input
          label="Metrik-Code / Typ-ID"
          name="metric_id"
          type="number"
          bind:value={goalMetricId}
          required
        />
        <Input
          label="Zielwert"
          name="target"
          type="number"
          step="0.1"
          bind:value={goalTarget}
          required
          placeholder="z. B. 70"
        />
        {#if error}<p class="text-xs font-medium text-rose-500">{error}</p>{/if}
        <div class="flex justify-between">
          <Btn variant="ghost" onclick={() => (step = 2)}>Zurück</Btn>
          <Btn variant="primary" onclick={createGoal}>Ziel speichern</Btn>
        </div>
      </div>
    </Card>
  {:else if step === 4}
    <Card>
      <div class="py-8 text-center">
        <Icon name="celebration" size="2xl" class="text-success-500" />
        <h1 class="text-surface-900 mt-4 text-xl font-semibold">You're all set!</h1>
        <p class="text-surface-500 mt-2 text-sm">Start tracking your health data.</p>
        <div class="mt-6">
          <Btn variant="primary" onclick={dismiss}>Go to Dashboard</Btn>
        </div>
      </div>
    </Card>
  {/if}
</div>
