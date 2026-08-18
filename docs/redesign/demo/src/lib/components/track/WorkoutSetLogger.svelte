<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import type { WorkoutSet } from '../../types';

  let sets = $state<WorkoutSet[]>([
    { setNumber: 1, previous: '32 kg × 10', weightKg: 34.0, reps: 10, rpe: '@8.0', completed: true },
    { setNumber: 2, previous: '32 kg × 8', weightKg: 34.0, reps: 8, rpe: '@8.5', completed: true },
    { setNumber: 3, previous: '32 kg × 8', weightKg: 34.0, reps: 8, rpe: '@9.0', completed: false }
  ]);

  let restSeconds = $state(90);
  let isTimerRunning = $state(false);
  let timerId: any = null;

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
        clearInterval(timerId);
        isTimerRunning = false;
        alert('Pausenzeit beendet! Nächster Satz bereit.');
      }
    }, 1000);
  }

  function addSeconds(s: number) {
    restSeconds += s;
  }

  function completeSet(index: number) {
    sets[index].completed = true;
    startTimer();
  }
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-[var(--radius-lg)] p-4 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="dumbbell" class="text-[var(--color-activity)]" />
      <span>Übung 2 von 5: Schrägbankdrücken (Kurzhanteln)</span>
    </div>
    <Badge variant="activity">Pause: 90s</Badge>
  </div>

  <div class="w-full overflow-x-auto mb-4">
    <table class="w-full text-left text-xs border-collapse">
      <thead>
        <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.6875rem]">
          <th class="py-2 px-3">Satz</th>
          <th class="py-2 px-3">Vorwoche</th>
          <th class="py-2 px-3">Gewicht</th>
          <th class="py-2 px-3">Wdh.</th>
          <th class="py-2 px-3">RPE</th>
          <th class="py-2 px-3">Status</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-[var(--border-subtle)]">
        {#each sets as set, i}
          <tr class="text-[var(--text-main)]">
            <td class="py-2.5 px-3 font-bold">{set.setNumber}</td>
            <td class="py-2.5 px-3 text-[var(--text-muted)] font-mono">{set.previous}</td>
            <td class="py-2.5 px-3">
              <input
                type="number"
                step="0.5"
                bind:value={set.weightKg}
                class="w-16 px-1.5 py-0.5 rounded bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] font-mono font-bold text-xs"
              /> kg
            </td>
            <td class="py-2.5 px-3">
              <input
                type="number"
                bind:value={set.reps}
                class="w-12 px-1.5 py-0.5 rounded bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] font-mono font-bold text-xs"
              />
            </td>
            <td class="py-2.5 px-3">
              <Badge variant="default">{set.rpe}</Badge>
            </td>
            <td class="py-2.5 px-3">
              {#if set.completed}
                <Badge variant="success">Erledigt</Badge>
              {:else}
                <Btn variant="primary" size="sm" onclick={() => completeSet(i)}>
                  Abhaken
                </Btn>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <!-- Pausentimer Bar -->
  <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-[var(--radius-md)] p-3 flex items-center justify-between">
    <div>
      <div class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Pausentimer</div>
      <div class="text-xl font-extrabold font-mono text-[var(--color-primary)] tabular-nums">
        {formattedTime}
      </div>
    </div>
    <div class="flex gap-2">
      <Btn variant="secondary" size="sm" onclick={() => addSeconds(30)}>+ 30s</Btn>
      <Btn variant="secondary" size="sm" onclick={startTimer}>Neustart</Btn>
    </div>
  </div>
</div>
