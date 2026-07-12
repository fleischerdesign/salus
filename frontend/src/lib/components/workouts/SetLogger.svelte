<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import { untrack } from 'svelte';

  type LogState = 'pending' | 'logging' | 'logged' | 'failed';

  interface Props {
    setNumber: number;
    suggestedWeight: number;
    suggestedReps: number;
    suggestedRpe: number;
    prWeight?: number;
    prEst1rm?: number;
    logState: LogState;
    onlog: (data: { weight: number; reps: number; rpe: number }) => void;
    onunlog: () => void;
    class?: string;
  }

  let {
    setNumber,
    suggestedWeight,
    suggestedReps,
    suggestedRpe,
    prWeight = 0,
    prEst1rm = 0,
    logState,
    onlog,
    onunlog,
    class: extraClass = '',
  }: Props = $props();

  let weight = $state(untrack(() => suggestedWeight));
  let reps = $state(untrack(() => suggestedReps));
  let rpe = $state(untrack(() => suggestedRpe));

  const est1rm = $derived(
    reps <= 0 ? 0 : reps === 1 ? weight : weight / (1.0278 - 0.0278 * reps),
  );

  const isPR = $derived(
    (prWeight > 0 && weight > prWeight) || (prEst1rm > 0 && est1rm > prEst1rm),
  );

  function adjust(field: 'weight' | 'reps' | 'rpe', delta: number) {
    if (logState !== 'pending' && logState !== 'failed') return;
    if (field === 'weight') weight = Math.max(0, +(weight + delta).toFixed(1));
    else if (field === 'reps') reps = Math.max(0, Math.round(reps + delta));
    else rpe = Math.max(5, Math.min(10, +(rpe + delta).toFixed(1)));
  }

  function updateWeight(e: Event) {
    const v = parseFloat((e.target as HTMLInputElement).value);
    if (!isNaN(v)) weight = +v.toFixed(1);
  }

  function updateReps(e: Event) {
    const v = parseInt((e.target as HTMLInputElement).value);
    if (!isNaN(v)) reps = v;
  }

  function updateRpe(e: Event) {
    const v = parseFloat((e.target as HTMLInputElement).value);
    if (!isNaN(v)) rpe = +v.toFixed(1);
  }

  function handleClick() {
    if (logState === 'logged') onunlog();
    else if (logState === 'pending' || logState === 'failed') onlog({ weight, reps, rpe });
  }

  const isOn = $derived(logState === 'logged');
  const isBusy = $derived(logState === 'logging');
  const isRpe10 = $derived(rpe >= 10);

  const stepperClass = 'flex items-center rounded-md border border-surface-200 bg-surface-0 overflow-hidden';
  const btnClass = 'flex h-7 w-7 items-center justify-center text-xs font-semibold text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-600';
  const inputClass = 'h-7 w-14 border-none bg-transparent text-center text-xs tabular-nums text-surface-900 outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none';

  const checkBtn = $derived(
    'flex h-8 w-8 shrink-0 items-center justify-center rounded-full border transition-all duration-150 ' +
    (isOn
      ? 'border-success-500 bg-success-500 text-white hover:border-error-500 hover:bg-error-500'
      : isBusy
        ? 'border-surface-300 bg-surface-50 cursor-wait'
        : logState === 'failed'
          ? 'border-error-500 bg-error-50 text-error-600'
          : 'border-surface-300 bg-surface-50 text-surface-400 hover:border-primary-400 hover:text-primary-600'),
  );
</script>

<div class="flex items-center gap-3 rounded-lg px-3 py-2 transition-opacity duration-200 {isOn ? 'bg-surface-50/50 opacity-70' : 'bg-surface-50/50'} {extraClass}">
  <!-- Set number -->
  <span class="w-7 shrink-0 text-xs font-bold tabular-nums text-surface-500">{setNumber}</span>

  <!-- Weight stepper -->
  <div class="flex items-center gap-1.5">
    <span class="text-[10px] font-medium uppercase text-surface-400">kg</span>
    <div class={stepperClass}>
      <button type="button" class={btnClass} onclick={() => adjust('weight', -2.5)} disabled={isOn} aria-label="Decrease weight">−</button>
      <input type="number" value={weight} oninput={updateWeight} class={inputClass} disabled={isOn} step="0.5" />
      <button type="button" class={btnClass} onclick={() => adjust('weight', 2.5)} disabled={isOn} aria-label="Increase weight">+</button>
    </div>
  </div>

  <!-- Reps stepper -->
  <div class="flex items-center gap-1.5">
    <span class="text-[10px] font-medium uppercase text-surface-400">reps</span>
    <div class={stepperClass}>
      <button type="button" class={btnClass} onclick={() => adjust('reps', -1)} disabled={isOn} aria-label="Decrease reps">−</button>
      <input type="number" value={reps} oninput={updateReps} class={inputClass} disabled={isOn} step="1" />
      <button type="button" class={btnClass} onclick={() => adjust('reps', 1)} disabled={isOn} aria-label="Increase reps">+</button>
    </div>
  </div>

  <!-- RPE stepper -->
  <div class="flex items-center gap-1.5">
    <span class="text-[10px] font-medium uppercase text-surface-400">RPE</span>
    <div class="{stepperClass} {isRpe10 && isOn ? 'border-error-300' : ''}">
      <button type="button" class={btnClass} onclick={() => adjust('rpe', -0.5)} disabled={isOn} aria-label="Decrease RPE">−</button>
      <input
        type="number"
        value={rpe}
        oninput={updateRpe}
        class="{inputClass} {isRpe10 && isOn ? 'text-error-600 font-bold' : ''}"
        disabled={isOn}
        step="0.5"
        min="5"
        max="10"
      />
      <button type="button" class={btnClass} onclick={() => adjust('rpe', 0.5)} disabled={isOn} aria-label="Increase RPE">+</button>
    </div>
  </div>

  <!-- Spacer → pushes 1RM + check button to the right -->
  <div class="flex-1"></div>

  <!-- Est. 1RM -->
  <span class="flex items-center gap-1 text-xs font-semibold tabular-nums {isPR ? 'text-warning-600' : 'text-surface-400'}" style="min-width: 68px;">
    1RM: {est1rm > 0 ? est1rm.toFixed(1) : '--'}
    {#if isPR}
      <Icon name="trophy" size="sm" class="text-warning-500" />
    {/if}
  </span>

  <!-- Check-circle button -->
  <button type="button" class={checkBtn} onclick={handleClick} disabled={isBusy} aria-label={isOn ? 'Remove set' : 'Log set'}>
    {#if isBusy}
      <Icon name="sync" size="sm" class="animate-spin" />
    {:else if isOn}
      <Icon name="check" size="sm" />
    {:else if logState === 'failed'}
      <Icon name="sync-problem" size="sm" />
    {:else}
      <Icon name="check" size="sm" />
    {/if}
  </button>
</div>
