<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  interface Medication {
    id: string;
    name: string;
    type: 'medication' | 'supplement';
    dosage: string;
    timing: 'Morgens' | 'Mittags' | 'Abends' | 'Nachts';
    instructions: string;
    stock: number;
    packSize: number;
    adherencePct: number;
    takenToday: boolean;
  }

  let meds = $state<Medication[]>([
    {
      id: '1',
      name: 'Telmisartan',
      type: 'medication',
      dosage: '20 mg (1 Tab)',
      timing: 'Morgens',
      instructions: 'Nüchtern mit einem Glas Wasser',
      stock: 5,
      packSize: 98,
      adherencePct: 98,
      takenToday: true
    },
    {
      id: '2',
      name: 'Omega-3 Triglyceride (EPA/DHA)',
      type: 'supplement',
      dosage: '2.000 mg (2 Kapseln)',
      timing: 'Mittags',
      instructions: 'Zur fettreichsten Mahlzeit des Tages',
      stock: 42,
      packSize: 120,
      adherencePct: 92,
      takenToday: false
    },
    {
      id: '3',
      name: 'Vitamin D3 + K2 (MK-7)',
      type: 'supplement',
      dosage: '5.000 I.E. / 200 µg',
      timing: 'Mittags',
      instructions: 'Zusammen mit Omega-3',
      stock: 60,
      packSize: 100,
      adherencePct: 95,
      takenToday: false
    },
    {
      id: '4',
      name: 'Magnesiumbisglycinat',
      type: 'supplement',
      dosage: '400 mg elementar',
      timing: 'Abends',
      instructions: '30–45 Minuten vor dem Einschlafen',
      stock: 18,
      packSize: 90,
      adherencePct: 89,
      takenToday: false
    }
  ]);

  function toggle(id: string) {
    const item = meds.find(m => m.id === id);
    if (item) {
      item.takenToday = !item.takenToday;
      if (navigator.vibrate) navigator.vibrate(20);
    }
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Medikamente & Supplement-Zentrale</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Präzise Dosierungs-Zeitpläne, Restbestands-Tracking und klinische Adhärenz
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Monats-Adhärenz: 94.2%</Badge>
      <Btn variant="primary" size="sm" onclick={() => alert('Neues Präparat anlegen geöffnet')}>
        + Präparat hinzufügen
      </Btn>
    </div>
  </div>

  <!-- Re-Order Warning Banner (if stock low) -->
  {#if meds.some(m => m.stock <= 7)}
    <div class="bg-[var(--color-vital-soft)]/30 border border-[var(--color-vital)]/40 rounded-2xl p-4 flex items-center justify-between flex-wrap gap-3">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-[var(--color-vital)] text-white flex items-center justify-center font-bold text-sm">
          !
        </div>
        <div>
          <span class="text-xs font-bold text-[var(--color-vital)] block">Kritisches Rezept- / Nachbestell-Limit erreicht</span>
          <p class="text-xs text-[var(--text-main)] mt-0.5">
            <strong>Telmisartan 20mg</strong> hat nur noch 5 Tabletten Vorrat (Reicht noch 5 Tage).
          </p>
        </div>
      </div>
      <Btn variant="secondary" size="sm" onclick={() => alert('Rezept-Anfrage an Praxis übermittelt')}>
        Rezept beim Arzt anfordern
      </Btn>
    </div>
  {/if}

  <!-- Medication Schedule Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
    <!-- Schedule (8-Col) -->
    <div class="lg:col-span-8 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
      <div class="flex items-center justify-between mb-4">
        <span class="text-sm font-bold">Heutiger Einnahme-Plan</span>
        <span class="text-xs text-[var(--text-muted)]">1 von 4 eingenommen</span>
      </div>

      <div class="space-y-3">
        {#each meds as med}
          <div
            class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-4 flex items-center justify-between transition-all {med.takenToday ? 'bg-[var(--color-success-soft)]/20 border-[var(--color-success)]/30' : ''}"
          >
            <div class="flex items-start gap-3">
              <button
                type="button"
                onclick={() => toggle(med.id)}
                class="mt-1 w-6 h-6 rounded-full border-2 flex items-center justify-center cursor-pointer transition-all {med.takenToday ? 'bg-[var(--color-success)] border-[var(--color-success)] text-white' : 'border-[var(--border-strong)] bg-[var(--bg-surface-0)]'}"
              >
                {#if med.takenToday}
                  <Icon name="check" size={14} />
                {/if}
              </button>

              <div>
                <div class="flex items-center gap-2">
                  <span class="text-sm font-bold text-[var(--text-main)] {med.takenToday ? 'line-through text-[var(--text-muted)]' : ''}">
                    {med.name}
                  </span>
                  <Badge variant={med.type === 'medication' ? 'vital' : 'primary'} class="text-[0.625rem]">
                    {med.dosage}
                  </Badge>
                </div>
                <p class="text-xs text-[var(--text-muted)] mt-0.5">{med.instructions}</p>
                <div class="flex items-center gap-3 text-[0.6875rem] text-[var(--text-soft)] mt-1 font-mono">
                  <span>Timing: {med.timing}</span>
                  <span>•</span>
                  <span>Vorrat: {med.stock} von {med.packSize}</span>
                  <span>•</span>
                  <span class="text-[var(--color-success)]">Adhärenz: {med.adherencePct}%</span>
                </div>
              </div>
            </div>

            <Badge variant={med.takenToday ? 'success' : 'default'}>
              {med.takenToday ? 'Erledigt' : 'Fällig'}
            </Badge>
          </div>
        {/each}
      </div>
    </div>

    <!-- Adherence Stats & Inventory (4-Col) -->
    <div class="lg:col-span-4 space-y-4">
      <!-- Monthly Adherence Card -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <span class="text-sm font-bold block mb-2">Adhärenz-Statistik</span>
        <div class="text-3xl font-extrabold font-mono text-[var(--color-success)] my-1">
          94.2 %
        </div>
        <p class="text-xs text-[var(--text-muted)] mb-3">
          Ausgezeichnete Therapietreue. Keine kritischen Auslassungen in den letzten 30 Tagen.
        </p>
        <div class="h-2 rounded-full bg-[var(--bg-surface-100)] overflow-hidden">
          <div class="h-full bg-[var(--color-success)]" style="width: 94.2%"></div>
        </div>
      </div>

      <!-- Interaction Safety Check -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)] mb-2">
          <Icon name="labs" class="text-[var(--color-primary)]" />
          <span>Interaktions-Prüfung</span>
        </div>
        <p class="text-xs text-[var(--text-muted)]">
          Keine bekannten pharmakologischen Wechselwirkungen zwischen Telmisartan und den eingenommenen Mikronährstoffen.
        </p>
        <Badge variant="success" class="mt-3">Geprüft nach ABDA-Datenbank</Badge>
      </div>
    </div>
  </div>
</div>
