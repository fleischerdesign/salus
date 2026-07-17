<script lang="ts">
  import EmptyState from '$components/ui/EmptyState.svelte';
  import MedicationCard from './MedicationCard.svelte';
  import type { Medication } from '$lib/db/types';

  interface Props {
    medications: Medication[];
    nextDoses: Record<string, string | null>;
    adherenceRates: Record<string, number>;
    onToggle: (medicationId: string) => void;
    onCreate: () => void;
  }

  let { medications, nextDoses, adherenceRates, onToggle, onCreate }: Props = $props();
</script>

{#if medications.length === 0}
  <EmptyState
    icon="pill"
    title="No medications"
    description="Track your medications, schedules, and inventory."
  >
    <button onclick={onCreate} class="btn btn-primary mt-4"> Add Medication </button>
  </EmptyState>
{:else}
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
    {#each medications as med (med.id)}
      <MedicationCard
        medication={med}
        nextDose={nextDoses[med.id] ?? null}
        adherenceRate={adherenceRates[med.id] ?? 0}
        onToggle={() => onToggle(med.id)}
      />
    {/each}
  </div>
{/if}
