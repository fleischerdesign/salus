<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  const splitQuery = useQuery(async () => {
    const plans = await db.workout.toArray();
    return plans.filter((p) => !p.deleted_at);
  });

  const plans = $derived(splitQuery.value ?? []);
  const daysOfWeek = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
</script>

<div class="rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-text-main">
      <Icon name="fitness_center" class="text-primary" />
      <span>Wöchentliche Trainings-Periodisierung</span>
    </div>
    <Badge variant="activity">{plans.length} Pläne hinterlegt</Badge>
  </div>

  {#if plans.length === 0}
    <div class="space-y-1 py-6 text-center text-xs text-text-muted">
      <p class="font-semibold text-text-main">Noch kein Trainingssplit definiert</p>
      <p class="text-[0.6875rem]">
        Erstelle Trainingspläne, um deinen wöchentlichen Periodisierungs-Split zu strukturieren.
      </p>
    </div>
  {:else}
    <div class="grid grid-cols-2 gap-2 sm:grid-cols-4 md:grid-cols-7">
      {#each daysOfWeek as day, idx}
        {@const plan = plans[idx % plans.length]}
        <div
          class="flex flex-col justify-between rounded-2xl border border-border-subtle bg-surface-50 p-3"
        >
          <div class="mb-1 flex items-center justify-between">
            <span
              class="rounded bg-surface-0 px-1.5 py-0.5 font-mono text-xs font-bold text-text-main"
            >
              {day}
            </span>
          </div>
          <div class="mt-1 truncate text-xs font-bold text-text-main">
            {plan?.name || 'Regeneration'}
          </div>
          <p class="mt-0.5 truncate text-[0.6875rem] text-text-muted">
            {plan?.description || 'Individuell'}
          </p>
        </div>
      {/each}
    </div>
  {/if}
</div>
