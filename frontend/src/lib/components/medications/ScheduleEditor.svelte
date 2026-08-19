<script lang="ts">
  import { todayString } from '$lib/utils/datetime';
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

  let times = $state<string[]>([]);
  let daysOfWeek = $state<number[]>([]);
  let dosage = $state('');
  let startDate = $state('');
  let endDate = $state('');

  $effect(() => {
    times = initialTimes.length > 0 ? [...initialTimes] : ['08:00'];
    daysOfWeek = initialDays ? [...initialDays] : [1, 2, 3, 4, 5, 6, 7];
    dosage = initialDosage;
    startDate = initialStartDate || todayString();
    endDate = initialEndDate;
  });

  const dayLabels = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];

  function toggleDay(day: number) {
    if (daysOfWeek.includes(day)) {
      if (daysOfWeek.length > 1) {
        daysOfWeek = daysOfWeek.filter((d) => d !== day);
      }
    } else {
      daysOfWeek = [...daysOfWeek, day].sort((a, b) => a - b);
    }
  }

  function addTime() {
    times = [...times, '12:00'];
  }

  function removeTime(index: number) {
    times = times.filter((_, i) => i !== index);
  }

  const isValid = $derived(
    dosage.trim().length > 0 && times.length > 0 && daysOfWeek.length > 0 && startDate.length > 0
  );

  function handleSubmit() {
    if (!isValid) return;
    onSave({
      dosage: dosage.trim(),
      times: [...times],
      days_of_week: daysOfWeek.length === 7 ? null : [...daysOfWeek],
      start_date: startDate,
      end_date: endDate || ''
    });
    dosage = '';
    times = ['08:00'];
    daysOfWeek = [1, 2, 3, 4, 5, 6, 7];
    startDate = todayString();
    endDate = '';
  }
</script>

<div class="flex flex-col gap-4 rounded-2xl border border-border-subtle bg-surface-50 p-4 text-xs">
  <Input
    label="Dosierung"
    name="dosage"
    placeholder="z. B. 1 Tablette, 5ml"
    bind:value={dosage}
    required
  />

  <div>
    <span class="mb-1.5 block text-xs font-bold text-text-main">Uhrzeiten</span>
    <div class="flex flex-col gap-2">
      {#each times as _time, i}
        <div class="flex items-center gap-2">
          <Input name="time" type="time" bind:value={times[i]} />
          {#if times.length > 1}
            <button
              type="button"
              onclick={() => removeTime(i)}
              class="flex h-8 w-8 flex-shrink-0 cursor-pointer items-center justify-center rounded-xl text-text-muted transition-colors hover:bg-rose-500/10 hover:text-rose-500"
            >
              <Icon name="close" size="sm" />
            </button>
          {/if}
        </div>
      {/each}
      <button
        type="button"
        onclick={addTime}
        class="cursor-pointer self-start pt-1 text-xs font-bold text-primary hover:underline"
      >
        + Weitere Uhrzeit hinzufügen
      </button>
    </div>
  </div>

  <div>
    <span class="mb-1.5 block text-xs font-bold text-text-main">Wochentage</span>
    <div class="flex gap-1.5">
      {#each dayLabels as label, i}
        {@const dayNum = i + 1}
        <button
          type="button"
          onclick={() => toggleDay(dayNum)}
          class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-xl text-xs font-bold transition-all {daysOfWeek.includes(
            dayNum
          )
            ? 'bg-primary text-white shadow-xs'
            : 'border border-border-subtle bg-surface-0 text-text-muted'}"
        >
          {label}
        </button>
      {/each}
    </div>
  </div>

  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
    <Input label="Startdatum" name="start_date" type="date" bind:value={startDate} required />
    <Input label="Enddatum (optional)" name="end_date" type="date" bind:value={endDate} />
  </div>

  <div class="flex justify-end pt-2">
    <Btn
      variant="primary"
      size="md"
      onclick={handleSubmit}
      disabled={!isValid || saving}
      loading={saving}
    >
      Zeitplan hinzufügen
    </Btn>
  </div>
</div>
