<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let portions = $state(2);
  const basePortions = 1;

  const baseIngredients = [
    { name: 'Hähnchenbrustfilet', amount: 150, unit: 'g', kcal: 165, protein: 34.5 },
    { name: 'Basmatireis (roh)', amount: 75, unit: 'g', kcal: 260, protein: 6.0 },
    { name: 'Brokkoli', amount: 120, unit: 'g', kcal: 40, protein: 3.5 },
    { name: 'Natives Olivenöl extra', amount: 10, unit: 'ml', kcal: 82, protein: 0.0 }
  ];

  let scaledIngredients = $derived(
    baseIngredients.map(item => ({
      ...item,
      amount: Math.round((item.amount / basePortions) * portions),
      kcal: Math.round((item.kcal / basePortions) * portions),
      protein: Number(((item.protein / basePortions) * portions).toFixed(1))
    }))
  );

  let totalKcal = $derived(scaledIngredients.reduce((sum, item) => sum + item.kcal, 0));
  let totalProtein = $derived(Number(scaledIngredients.reduce((sum, item) => sum + item.protein, 0).toFixed(1)));
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
    <div>
      <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
        <Icon name="food" class="text-[var(--color-activity)]" />
        <h3 class="text-sm font-bold text-[var(--text-main)]">Rezept-Portionen-Skalierer</h3>
      </div>
      <p class="text-xs text-[var(--text-muted)] mt-0.5">Dynamische Portions- und Nährwertberechnung</p>
    </div>
    
    <!-- Portion Controls -->
    <div class="flex items-center gap-2 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-lg p-1">
      <button
        type="button"
        class="w-7 h-7 rounded bg-[var(--bg-surface-0)] font-bold text-xs cursor-pointer hover:bg-[var(--bg-surface-100)]"
        onclick={() => portions = Math.max(1, portions - 1)}
      >
        -
      </button>
      <span class="font-mono font-bold text-xs px-2">{portions} {portions === 1 ? 'Portion' : 'Portionen'}</span>
      <button
        type="button"
        class="w-7 h-7 rounded bg-[var(--bg-surface-0)] font-bold text-xs cursor-pointer hover:bg-[var(--bg-surface-100)]"
        onclick={() => portions = Math.min(8, portions + 1)}
      >
        +
      </button>
    </div>
  </div>

  <div class="w-full overflow-x-auto mb-3">
    <table class="w-full text-left text-xs border-collapse">
      <thead>
        <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.6875rem]">
          <th class="py-2.5 px-3">Zutat</th>
          <th class="py-2.5 px-3">Menge</th>
          <th class="py-2.5 px-3">Kalorien</th>
          <th class="py-2.5 px-3">Protein</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-[var(--border-subtle)]">
        {#each scaledIngredients as ing}
          <tr>
            <td class="py-2.5 px-3 font-semibold">{ing.name}</td>
            <td class="py-2.5 px-3 font-mono">{ing.amount} {ing.unit}</td>
            <td class="py-2.5 px-3 font-mono">{ing.kcal} kcal</td>
            <td class="py-2.5 px-3 font-mono font-bold text-[var(--color-vital)]">{ing.protein}g</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <div class="flex items-center justify-between p-3 bg-[var(--bg-surface-50)] rounded-xl border border-[var(--border-subtle)] text-xs">
    <span class="font-bold">Gesamt ({portions} Portionen):</span>
    <div class="flex items-center gap-4 font-mono font-bold">
      <span>{totalKcal} kcal</span>
      <span class="text-[var(--color-vital)]">{totalProtein}g Protein</span>
    </div>
  </div>
</div>
