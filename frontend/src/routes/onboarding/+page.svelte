<script lang="ts">
  import { db } from '$lib/db/database';
  import { auth } from '$stores/auth.svelte';
  import { createToken as issueOnboardingToken } from '$lib/mutations/account';
  import { dismissOnboarding } from '$lib/mutations/account';
  import { createMeasurement } from '$lib/mutations/measurement';
  import { createGoal as createGoalMutation } from '$lib/mutations/goal';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import FormField from '$components/forms/FormField.svelte';
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
      <p class="mb-4 text-sm text-surface-600">
        Get an API token to push health data from apps and devices.
      </p>
      <Btn variant="primary" onclick={createToken}>
        <Icon name="key" size="sm" />Generate Token
      </Btn>
      {#if token}
        <div class="mt-4 space-y-3">
          <div>
            <p class="mb-1 text-xs font-medium text-surface-500">API Token</p>
            <CopyToClipboard value={token} label="API Token" />
          </div>
          {#if webhookUrl}
            <div>
              <p class="mb-1 text-xs font-medium text-surface-500">Webhook URL</p>
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
    <Card title="Log Your First Entry">
      <div class="flex flex-col gap-4">
        <FormField label="Metric Type ID" required>
          <Input name="metric_id" type="number" bind:value={entryMetricId} required />
        </FormField>
        <FormField label="Value" required>
          <Input name="value" bind:value={entryValue} required placeholder="e.g. 75.5" />
        </FormField>
        {#if error}<p class="text-sm text-error-500">{error}</p>{/if}
        <div class="flex justify-between">
          <Btn variant="ghost" onclick={() => (step = 1)}>Back</Btn>
          <Btn variant="primary" onclick={createEntry}>Save Entry</Btn>
        </div>
      </div>
    </Card>
  {:else if step === 3}
    <Card title="Set a Goal">
      <div class="flex flex-col gap-4">
        <FormField label="Metric Type ID" required>
          <Input name="metric_id" type="number" bind:value={goalMetricId} required />
        </FormField>
        <FormField label="Target Value" required>
          <Input
            name="target"
            type="number"
            step="0.1"
            bind:value={goalTarget}
            required
            placeholder="e.g. 70"
          />
        </FormField>
        {#if error}<p class="text-sm text-error-500">{error}</p>{/if}
        <div class="flex justify-between">
          <Btn variant="ghost" onclick={() => (step = 2)}>Back</Btn>
          <Btn variant="primary" onclick={createGoal}>Save Goal</Btn>
        </div>
      </div>
    </Card>
  {:else if step === 4}
    <Card>
      <div class="py-8 text-center">
        <Icon name="celebration" size="2xl" class="text-success-500" />
        <h2 class="mt-4 text-xl font-semibold text-surface-900">You're all set!</h2>
        <p class="mt-2 text-sm text-surface-500">Start tracking your health data.</p>
        <div class="mt-6">
          <Btn variant="primary" onclick={dismiss}>Go to Dashboard</Btn>
        </div>
      </div>
    </Card>
  {/if}
</div>
