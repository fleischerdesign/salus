<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  interface MedItem {
    id: string;
    name: string;
    dosage: string;
    time: string;
    instructions: string;
    stock: number;
    taken: boolean;
  }

  let meds = $state<MedItem[]>([
    {
      id: '1',
      name: 'Telmisartan',
      dosage: '20 mg (1 Tab)',
      time: '08:00',
      instructions: 'Morgens nüchtern mit Wasser',
      stock: 5,
      taken: true
    },
    {
      id: '2',
      name: 'Omega-3 Triglyceride',
      dosage: '2.000 mg (2 Kapseln)',
      time: '12:30',
      instructions: 'Zur ersten Mahlzeit',
      stock: 42,
      taken: false
    },
    {
      id: '3',
      name: 'Magnesiumbisglycinat',
      dosage: '400 mg elementar',
      time: '21:30',
      instructions: '30 Min vor dem Schlafen',
      stock: 18,
      taken: false
    }
  ]);

  function toggleMed(index: number) {
    meds[index].taken = !meds[index].taken;
    if (navigator.vibrate) navigator.vibrate(20);
  }
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-[18px] shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="labs" class="text-[var(--color-primary)]" />
      <span>Tägliche Supplement- & Medikamenten-Dosen</span>
    </div>
    <Badge variant="default">1 von 3 eingenommen</Badge>
  </div>

  <div class="space-y-2">
    {#each meds as med, i}
      <div
        class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex items-center justify-between transition-all {med.taken ? 'opacity-70 bg-[var(--color-success-soft)]/20' : ''}"
      >
        <div class="flex items-start gap-3">
          <button
            type="button"
            onclick={() => toggleMed(i)}
            class="mt-0.5 w-6 h-6 rounded-full border-2 flex items-center justify-center cursor-pointer transition-all {med.taken ? 'bg-[var(--color-success)] border-[var(--color-success)] text-white' : 'border-[var(--border-strong)] bg-[var(--bg-surface-0)]'}"
          >
            {#if med.taken}
              <Icon name="check" size={14} />
            {/if}
          </button>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-[var(--text-main)] {med.taken ? 'line-through text-[var(--text-muted)]' : ''}">
                {med.name}
              </span>
              <span class="text-xs font-mono font-semibold text-[var(--text-soft)]">{med.dosage}</span>
              {#if med.stock <= 7}
                <Badge variant="vital" class="text-[0.625rem]">Noch {med.stock} Stk</Badge>
              {/if}
            </div>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">{med.instructions} • <span class="font-mono">{med.time} Uhr</span></p>
          </div>
        </div>
        <Badge variant={med.taken ? 'success' : 'default'}>
          {med.taken ? 'Erledigt' : 'Ausstehend'}
        </Badge>
      </div>
    {/each}
  </div>
</div>
