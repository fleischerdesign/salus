<script lang="ts">
  import Icon from '../ui/Icon.svelte';

  let portions = $state(2);
  const basePortions = 1;

  const baseIngredients = [
    { name: 'Hähnchenbrustfilet', amount: 150, unit: 'g', kcal: 165, protein: 34.5 },
    { name: 'Basmatireis (roh)', amount: 75, unit: 'g', kcal: 260, protein: 6.0 },
    { name: 'Brokkoli', amount: 120, unit: 'g', kcal: 40, protein: 3.5 },
    { name: 'Natives Olivenöl extra', amount: 10, unit: 'ml', kcal: 82, protein: 0.0 }
  ];

  let scaledIngredients = $derived(
    baseIngredients.map((item) => ({
      ...item,
      amount: Math.round((item.amount / basePortions) * portions),
      kcal: Math.round((item.kcal / basePortions) * portions),
      protein: Number(((item.protein / basePortions) * portions).toFixed(1))
    }))
  );

  let totalKcal = $derived(scaledIngredients.reduce((sum, item) => sum + item.kcal, 0));
  let totalProtein = $derived(
    Number(scaledIngredients.reduce((sum, item) => sum + item.protein, 0).toFixed(1))
  );
</script>

<div
  class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
>
  <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
    <div>
      <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
        <Icon name="restaurant" class="text-[var(--color-activity)]" />
        <h3 class="text-sm font-bold text-[var(--text-main)]">Rezept-Portionen-Skalierer</h3>
      </div>
      <p class="mt-0.5 text-xs text-[var(--text-muted)]">
        Dynamische Portions- und Nährwertberechnung
      </p>
    </div>

    <!-- Portion Controls -->
    <div
      class="flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-1"
    >
      <button
        type="button"
        class="h-7 w-7 cursor-pointer rounded bg-[var(--bg-surface-0)] text-xs font-bold hover:bg-[var(--bg-surface-100)]"
        onclick={() => (portions = Math.max(1, portions - 1))}
      >
        -
      </button>
      <span class="px-2 font-mono text-xs font-bold"
        >{portions} {portions === 1 ? 'Portion' : 'Portionen'}</span
      >
      <button
        type="button"
        class="h-7 w-7 cursor-pointer rounded bg-[var(--bg-surface-0)] text-xs font-bold hover:bg-[var(--bg-surface-100)]"
        onclick={() => (portions = Math.min(8, portions + 1))}
      >
        +
      </button>
    </div>
  </div>

  <div class="mb-3 w-full overflow-x-auto">
    <table class="w-full border-collapse text-left text-xs">
      <thead>
        <tr
          class="border-b border-[var(--border-subtle)] text-[0.6875rem] tracking-wider text-[var(--text-muted)] uppercase"
        >
          <th class="px-3 py-2.5">Zutat</th>
          <th class="px-3 py-2.5">Menge</th>
          <th class="px-3 py-2.5">Kalorien</th>
          <th class="px-3 py-2.5">Protein</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-[var(--border-subtle)]">
        {#each scaledIngredients as ing}
          <tr>
            <td class="px-3 py-2.5 font-semibold">{ing.name}</td>
            <td class="px-3 py-2.5 font-mono">{ing.amount} {ing.unit}</td>
            <td class="px-3 py-2.5 font-mono">{ing.kcal} kcal</td>
            <td class="px-3 py-2.5 font-mono font-bold text-[var(--color-vital)]">{ing.protein}g</td
            >
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <div
    class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-xs"
  >
    <span class="font-bold">Gesamt ({portions} Portionen):</span>
    <div class="flex items-center gap-4 font-mono font-bold">
      <span>{totalKcal} kcal</span>
      <span class="text-[var(--color-vital)]">{totalProtein}g Protein</span>
    </div>
  </div>
</div>
