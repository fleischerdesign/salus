<script lang="ts">
  import FormField from '$components/forms/FormField.svelte';
  import Input from '$components/ui/Input.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    times: string[];
    daysOfWeek: number[] | null;
    dosage: string;
    startDate: string;
    endDate: string;
    onSave: (data: {
      dosage: string;
      times: string[];
      days_of_week: number[] | null;
      start_date: string;
      end_date: string;
    }) => void;
    saving?: boolean;
  }

  let {
    times: initialTimes = [],
    daysOfWeek: initialDays = null,
    dosage: initialDosage = '',
    startDate: initialStartDate = '',
    endDate: initialEndDate = '',
    onSave,
    saving = false
  }: Props = $props();

  const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  let dosage = $state(initialDosage);
  let times = $state(initialTimes.length > 0 ? [...initialTimes] : ['08:00']);
  let daysOfWeek = $state(initialDays ?? [1, 2, 3, 4, 5, 6, 7]);
  let startDate = $state(initialStartDate || new Date().toISOString().split('T')[0]);
  let endDate = $state(initialEndDate);

  const isValid = $derived(dosage.trim().length > 0 && times.length > 0);

  function addTime() {
    times = [...times, '12:00'];
  }

  function removeTime(index: number) {
    times = times.filter((_, i) => i !== index);
  }

  function toggleDay(day: number) {
    if (daysOfWeek.includes(day)) {
      daysOfWeek = daysOfWeek.filter((d) => d !== day);
    } else {
      daysOfWeek = [...daysOfWeek, day];
    }
  }

  function handleSubmit() {
    if (!isValid) return;
    onSave({
      dosage: dosage.trim(),
      times,
      days_of_week: daysOfWeek.length === 7 ? null : daysOfWeek.sort(),
      start_date: startDate,
      end_date: endDate || ''
    });
    dosage = '';
    times = ['08:00'];
    daysOfWeek = [1, 2, 3, 4, 5, 6, 7];
    startDate = new Date().toISOString().split('T')[0];
    endDate = '';
  }
</script>

<div class="flex flex-col gap-4 rounded-lg border border-surface-200 bg-surface-50 p-4">
  <FormField label="Dosage">
    <Input name="dosage" placeholder="e.g. 1 Tablette, 5ml" bind:value={dosage} />
  </FormField>

  <FormField label="Times">
    <div class="flex flex-col gap-2">
      <!-- eslint-disable-next-line @typescript-eslint/no-unused-vars -->
      {#each times as _time, i}
        <div class="flex items-center gap-2">
          <Input name="time" type="time" bind:value={times[i]} />
          {#if times.length > 1}
            <button
              onclick={() => removeTime(i)}
              class="flex-shrink-0 rounded p-1 text-surface-400 hover:text-error-500"
            >
              <Icon name="close" size="sm" />
            </button>
          {/if}
        </div>
      {/each}
      <button onclick={addTime} class="self-start text-xs text-primary-600 hover:text-primary-700">
        + Add time
      </button>
    </div>
  </FormField>

  <FormField label="Days of Week">
    <div class="flex gap-1">
      {#each dayLabels as label, i}
        {@const dayNum = i + 1}
        <button
          type="button"
          onclick={() => toggleDay(dayNum)}
          class="flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium transition-colors"
          class:bg-primary-500={daysOfWeek.includes(dayNum)}
          class:text-white={daysOfWeek.includes(dayNum)}
          class:bg-surface-100={!daysOfWeek.includes(dayNum)}
          class:text-surface-600={!daysOfWeek.includes(dayNum)}
        >
          {label.slice(0, 1)}
        </button>
      {/each}
    </div>
  </FormField>

  <div class="grid grid-cols-2 gap-4">
    <FormField label="Start Date">
      <Input name="start_date" type="date" bind:value={startDate} />
    </FormField>
    <FormField label="End Date (optional)">
      <Input name="end_date" type="date" bind:value={endDate} />
    </FormField>
  </div>

  <div class="flex justify-end">
    <Btn variant="primary" onclick={handleSubmit} disabled={!isValid || saving}>
      {saving ? 'Saving...' : 'Add Schedule'}
    </Btn>
  </div>
</div>
