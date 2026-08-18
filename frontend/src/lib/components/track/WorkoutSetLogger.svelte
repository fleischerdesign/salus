<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import type { WorkoutSet } from '$lib/types/workouts';

  let sets = $state<WorkoutSet[]>([
    {
      id: '1',
      setNumber: 1,
      type: 'normal',
      previous: { weightKg: 32, reps: 10, rpe: '8.0' },
      weightKg: 34.0,
      reps: 10,
      rpe: 8.0,
      completed: true
    },
    {
      id: '2',
      setNumber: 2,
      type: 'normal',
      previous: { weightKg: 32, reps: 8, rpe: '8.5' },
      weightKg: 34.0,
      reps: 8,
      rpe: 8.5,
      completed: true
    },
    {
      id: '3',
      setNumber: 3,
      type: 'normal',
      previous: { weightKg: 32, reps: 8, rpe: '9.0' },
      weightKg: 34.0,
      reps: 8,
      rpe: 9.0,
      completed: false
    }
  ]);

  let restSeconds = $state(90);
  let isTimerRunning = $state(false);
  let timerId: ReturnType<typeof setInterval> | null = null;

  let formattedTime = $derived(
    `${String(Math.floor(restSeconds / 60)).padStart(2, '0')}:${String(restSeconds % 60).padStart(2, '0')}`
  );

  function startTimer() {
    if (timerId) clearInterval(timerId);
    restSeconds = 90;
    isTimerRunning = true;
    timerId = setInterval(() => {
      restSeconds--;
      if (restSeconds <= 0) {
        if (timerId) clearInterval(timerId);
        isTimerRunning = false;
        alert('Pausenzeit beendet! Nächster Satz bereit.');
      }
    }, 1000);
  }

  function addSeconds(sec: number) {
    restSeconds += sec;
  }

  function completeSet(index: number) {
    sets[index].completed = true;
    startTimer();
  }
</script>

<div
  class="rounded-[var(--radius-lg)] border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-4 shadow-[var(--shadow-card)]"
>
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
      <Icon name="fitness-center" class="text-[var(--color-activity)]" />
      <span>Übung 2 von 5: Schrägbankdrücken (Kurzhanteln)</span>
    </div>
    <Badge variant="activity">Pause: 90s</Badge>
  </div>

  <div class="mb-4 w-full overflow-x-auto">
    <table class="w-full border-collapse text-left text-xs">
      <thead>
        <tr
          class="border-b border-[var(--border-subtle)] text-[0.6875rem] tracking-wider text-[var(--text-muted)] uppercase"
        >
          <th class="px-3 py-2">Satz</th>
          <th class="px-3 py-2">Vorwoche</th>
          <th class="px-3 py-2">Gewicht</th>
          <th class="px-3 py-2">Wdh.</th>
          <th class="px-3 py-2">RPE</th>
          <th class="px-3 py-2">Status</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-[var(--border-subtle)]">
        {#each sets as set, i}
          <tr class="text-[var(--text-main)]">
            <td class="px-3 py-2.5 font-bold">{set.setNumber}</td>
            <td class="px-3 py-2.5 font-mono text-[var(--text-muted)]">{set.previous}</td>
            <td class="px-3 py-2.5">
              <input
                type="number"
                step="0.5"
                bind:value={set.weightKg}
                class="w-16 rounded border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-1.5 py-0.5 font-mono text-xs font-bold"
              /> kg
            </td>
            <td class="px-3 py-2.5">
              <input
                type="number"
                bind:value={set.reps}
                class="w-12 rounded border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-1.5 py-0.5 font-mono text-xs font-bold"
              />
            </td>
            <td class="px-3 py-2.5">
              <Badge variant="default">{set.rpe}</Badge>
            </td>
            <td class="px-3 py-2.5">
              {#if set.completed}
                <Badge variant="success">Erledigt</Badge>
              {:else}
                <Btn variant="primary" size="sm" onclick={() => completeSet(i)}>Abhaken</Btn>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <!-- Pausentimer Bar -->
  <div
    class="flex items-center justify-between rounded-[var(--radius-md)] border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3"
  >
    <div>
      <div class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Pausentimer</div>
      <div class="font-mono text-xl font-extrabold text-[var(--color-primary)] tabular-nums">
        {formattedTime}
      </div>
    </div>
    <div class="flex gap-2">
      <Btn variant="secondary" size="sm" onclick={() => addSeconds(30)}>+ 30s</Btn>
      <Btn variant="secondary" size="sm" onclick={startTimer}
        >{isTimerRunning ? 'Neustart' : 'Starten'}</Btn
      >
    </div>
  </div>
</div>
