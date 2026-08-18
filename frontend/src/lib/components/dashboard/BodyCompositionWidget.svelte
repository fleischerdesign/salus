<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    weight = 81.8,
    bodyFat = 13.8,
    leanMass = 70.5,
    waist = 82
  } = $props<{
    weight?: number;
    bodyFat?: number;
    leanMass?: number;
    waist?: number;
  }>();

  let fatMassKg = $derived(((weight * bodyFat) / 100).toFixed(1));
  let waterLiters = 54.2;
  let boneMassKg = 3.4;
</script>

<div
  class="space-y-5 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)] sm:p-6"
>
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-3">
      <div
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-cyan-500/10 font-bold text-cyan-500"
      >
        <Icon name="labs" size={20} />
      </div>
      <div>
        <h2 class="text-sm font-extrabold text-[var(--text-main)]">
          Körperzusammensetzung und Anthropometrie
        </h2>
        <p class="text-xs text-[var(--text-muted)]">
          Bioelektrische Impedanzanalyse (BIA) und Gewichtsvektor
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant="success" class="font-bold">Sportler-Kategorie</Badge>
    </div>
  </div>

  <!-- Main Segmental BIA Stacked Spectrum & Anthropometry -->
  <div class="grid grid-cols-1 gap-4 lg:grid-cols-12">
    <!-- Left Hero (7-Col): Segmented Mass Distribution Bar -->
    <div
      class="flex flex-col justify-between space-y-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 sm:p-5 lg:col-span-7"
    >
      <div class="flex items-start justify-between">
        <div>
          <span
            class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
          >
            Gesamtgewicht (30T-EMA)
          </span>
          <div class="mt-0.5 flex items-baseline gap-2">
            <span
              class="text-3xl font-extrabold tracking-tight text-[var(--text-main)] tabular-nums sm:text-4xl"
            >
              {weight}
            </span>
            <span class="text-xs font-semibold text-[var(--text-soft)]">kg</span>
            <span class="ml-1 text-xs font-bold text-emerald-500"> ↘ -0.7 kg (Fettabbau) </span>
          </div>
        </div>

        <div class="text-right">
          <span class="block text-[0.6875rem] font-bold text-cyan-500">KFA {bodyFat}%</span>
          <span class="text-xs text-[var(--text-muted)]">{fatMassKg} kg Depotfett</span>
        </div>
      </div>

      <!-- Segmented Multi-Color Mass Bar -->
      <div class="space-y-2">
        <div class="flex h-3 w-full overflow-hidden rounded-full bg-[var(--border-subtle)]">
          <!-- Muscle Mass (86.2%) -->
          <div
            class="h-full w-[86.2%] rounded-l-full bg-[var(--color-primary)]"
            title="Muskelmasse 70.5 kg"
          ></div>
          <!-- Fat Mass (13.8%) -->
          <div class="h-full w-[13.8%] rounded-r-full bg-amber-400" title="Fettmasse"></div>
        </div>

        <div class="grid grid-cols-3 gap-2 pt-1 text-[0.6875rem] font-semibold">
          <div class="flex items-center gap-1.5">
            <span class="h-2 w-2 rounded-full bg-[var(--color-primary)]"></span>
            <span class="text-[var(--text-main)]">{leanMass} kg Muskeln</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="h-2 w-2 rounded-full bg-amber-400"></span>
            <span class="text-[var(--text-main)]">{fatMassKg} kg Fett</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="h-2 w-2 rounded-full bg-cyan-400"></span>
            <span class="text-[var(--text-main)]">{waterLiters} L Wasser</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Hero (5-Col): Waist-to-Height Ratio & Skeletal Mass -->
    <div
      class="flex flex-col justify-between space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 sm:p-5 lg:col-span-5"
    >
      <!-- WHtR -->
      <div>
        <div class="mb-1 flex items-center justify-between text-xs">
          <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
            >Waist-to-Height Ratio (WHtR)</span
          >
          <span class="font-bold text-emerald-500">0.45 • Optimal</span>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums">{waist}</span>
          <span class="text-xs text-[var(--text-soft)]">cm Taillenumfang</span>
        </div>
        <div class="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-[var(--border-subtle)]">
          <div class="h-full rounded-full bg-emerald-500" style="width: 45%;"></div>
        </div>
      </div>

      <!-- Bone Mass & Visceral Score -->
      <div class="grid grid-cols-2 gap-2 border-t border-[var(--border-subtle)] pt-2 text-center">
        <div>
          <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
            >Knochenmasse</span
          >
          <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums"
            >{boneMassKg} kg</span
          >
        </div>
        <div>
          <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
            >Viszeralfett</span
          >
          <span class="text-sm font-extrabold text-emerald-500 tabular-nums">Stufe 3 (Niedrig)</span
          >
        </div>
      </div>
    </div>
  </div>
</div>
