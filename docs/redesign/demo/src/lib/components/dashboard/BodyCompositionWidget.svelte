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

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 sm:p-6 shadow-[var(--shadow-card)] space-y-5">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-2">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-2xl bg-cyan-500/10 text-cyan-500 flex items-center justify-center font-bold shrink-0">
        <Icon name="labs" size={20} />
      </div>
      <div>
        <h2 class="text-sm font-extrabold text-[var(--text-main)]">Körperzusammensetzung und Anthropometrie</h2>
        <p class="text-xs text-[var(--text-muted)]">Bioelektrische Impedanzanalyse (BIA) und Gewichtsvektor</p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant="success" class="font-bold">Sportler-Kategorie</Badge>
    </div>
  </div>

  <!-- Main Segmental BIA Stacked Spectrum & Anthropometry -->
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
    
    <!-- Left Hero (7-Col): Segmented Mass Distribution Bar -->
    <div class="lg:col-span-7 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 sm:p-5 flex flex-col justify-between space-y-4">
      <div class="flex items-start justify-between">
        <div>
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase tracking-wider block">
            Gesamtgewicht (30T-EMA)
          </span>
          <div class="flex items-baseline gap-2 mt-0.5">
            <span class="text-3xl sm:text-4xl font-extrabold text-[var(--text-main)] tabular-nums tracking-tight">
              {weight}
            </span>
            <span class="text-xs font-semibold text-[var(--text-soft)]">kg</span>
            <span class="text-xs font-bold text-emerald-500 ml-1">
              ↘ -0.7 kg (Fettabbau)
            </span>
          </div>
        </div>

        <div class="text-right">
          <span class="text-[0.6875rem] font-bold text-cyan-500 block">KFA {bodyFat}%</span>
          <span class="text-xs text-[var(--text-muted)]">{fatMassKg} kg Depotfett</span>
        </div>
      </div>

      <!-- Segmented Multi-Color Mass Bar -->
      <div class="space-y-2">
        <div class="w-full h-3 rounded-full overflow-hidden flex bg-[var(--border-subtle)]">
          <!-- Muscle Mass (86.2%) -->
          <div class="h-full bg-[var(--color-primary)] w-[86.2%] rounded-l-full" title="Muskelmasse 70.5 kg"></div>
          <!-- Fat Mass (13.8%) -->
          <div class="h-full bg-amber-400 w-[13.8%] rounded-r-full" title="Fettmasse"></div>
        </div>

        <div class="grid grid-cols-3 gap-2 text-[0.6875rem] font-semibold pt-1">
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-[var(--color-primary)]"></span>
            <span class="text-[var(--text-main)]">{leanMass} kg Muskeln</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-amber-400"></span>
            <span class="text-[var(--text-main)]">{fatMassKg} kg Fett</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-cyan-400"></span>
            <span class="text-[var(--text-main)]">{waterLiters} L Wasser</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Hero (5-Col): Waist-to-Height Ratio & Skeletal Mass -->
    <div class="lg:col-span-5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 sm:p-5 flex flex-col justify-between space-y-3">
      
      <!-- WHtR -->
      <div>
        <div class="flex justify-between items-center text-xs mb-1">
          <span class="font-bold text-[var(--text-muted)] uppercase text-[0.625rem]">Waist-to-Height Ratio (WHtR)</span>
          <span class="font-bold text-emerald-500">0.45 • Optimal</span>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums">{waist}</span>
          <span class="text-xs text-[var(--text-soft)]">cm Taillenumfang</span>
        </div>
        <div class="w-full bg-[var(--border-subtle)] h-1.5 rounded-full overflow-hidden mt-1.5">
          <div class="bg-emerald-500 h-full rounded-full" style="width: 45%;"></div>
        </div>
      </div>

      <!-- Bone Mass & Visceral Score -->
      <div class="grid grid-cols-2 gap-2 pt-2 border-t border-[var(--border-subtle)] text-center">
        <div>
          <span class="text-[0.625rem] text-[var(--text-muted)] uppercase font-bold block">Knochenmasse</span>
          <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums">{boneMassKg} kg</span>
        </div>
        <div>
          <span class="text-[0.625rem] text-[var(--text-muted)] uppercase font-bold block">Viszeralfett</span>
          <span class="text-sm font-extrabold text-emerald-500 tabular-nums">Stufe 3 (Niedrig)</span>
        </div>
      </div>

    </div>

  </div>
</div>
