<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import type { MuscleGroup } from '../../types/workouts';

  interface MuscleVolumeData {
    name: MuscleGroup;
    setsWeekly: number;
    volumeKg: number;
    recoveryHoursLeft: number;
    status: 'optimal' | 'low' | 'overreaching';
    statusText: string;
    exercises: string[];
    color: string;
  }

  const muscleData: Record<string, MuscleVolumeData> = {
    'Brust': {
      name: 'Brust',
      setsWeekly: 14,
      volumeKg: 4850,
      recoveryHoursLeft: 18,
      status: 'optimal',
      statusText: 'MAV (Optimaler Wachstumsreiz: 10–18 Sätze)',
      exercises: ['Bankdrücken (Langhantel)', 'Schrägbankdrücken (Kurzhantel)', 'Dips mit Zusatzgewicht'],
      color: '#10b981' // Green
    },
    'Rücken': {
      name: 'Rücken',
      setsWeekly: 16,
      volumeKg: 5200,
      recoveryHoursLeft: 36,
      status: 'optimal',
      statusText: 'MAV (Optimaler Wachstumsreiz: 12–20 Sätze)',
      exercises: ['Klimmzüge mit Zusatzgewicht', 'Langhantelrudern', 'Latzug enger Griff'],
      color: '#10b981' // Green
    },
    'Schultern': {
      name: 'Schultern',
      setsWeekly: 11,
      volumeKg: 2100,
      recoveryHoursLeft: 8,
      status: 'optimal',
      statusText: 'MAV (Optimal: 10–16 Sätze)',
      exercises: ['Overhead Press', 'Seitheben am Kabelzug', 'Face Pulls'],
      color: '#10b981'
    },
    'Trizeps': {
      name: 'Trizeps',
      setsWeekly: 9,
      volumeKg: 1400,
      recoveryHoursLeft: 4,
      status: 'low',
      statusText: 'MEV (Erhaltungsvolumen: 6–10 Sätze)',
      exercises: ['Trizepsdrücken am Kabelzug', 'Dips'],
      color: '#0284c7' // Blue/Cyan
    },
    'Bizeps': {
      name: 'Bizeps',
      setsWeekly: 8,
      volumeKg: 950,
      recoveryHoursLeft: 12,
      status: 'low',
      statusText: 'MEV (Erhaltungsvolumen: 6–10 Sätze)',
      exercises: ['Incline Dumbbell Curls', 'Hammer Curls'],
      color: '#0284c7'
    },
    'Quadrizeps': {
      name: 'Quadrizeps',
      setsWeekly: 15,
      volumeKg: 7800,
      recoveryHoursLeft: 42,
      status: 'optimal',
      statusText: 'MAV (Optimaler Wachstumsreiz: 12–18 Sätze)',
      exercises: ['Kniebeugen (High Bar)', 'Beinpresse 45°', 'Beinstrecker'],
      color: '#10b981'
    },
    'Hamstrings': {
      name: 'Hamstrings',
      setsWeekly: 10,
      volumeKg: 4200,
      recoveryHoursLeft: 30,
      status: 'optimal',
      statusText: 'MAV (Optimal: 10–14 Sätze)',
      exercises: ['Rumänisches Kreuzheben', 'Beinbeuger liegend'],
      color: '#10b981'
    },
    'Waden': {
      name: 'Waden',
      setsWeekly: 6,
      volumeKg: 1200,
      recoveryHoursLeft: 0,
      status: 'low',
      statusText: 'MEV (6–12 Sätze)',
      exercises: ['Wadenheben stehend'],
      color: '#0284c7'
    },
    'Bauch': {
      name: 'Bauch',
      setsWeekly: 6,
      volumeKg: 600,
      recoveryHoursLeft: 0,
      status: 'low',
      statusText: 'MEV (6–12 Sätze)',
      exercises: ['Hanging Leg Raises', 'Cable Crunches'],
      color: '#0284c7'
    },
    'Gesäß': {
      name: 'Gesäß',
      setsWeekly: 12,
      volumeKg: 5600,
      recoveryHoursLeft: 38,
      status: 'optimal',
      statusText: 'MAV (Optimal: 10–16 Sätze)',
      exercises: ['Kniebeugen', 'Rumänisches Kreuzheben'],
      color: '#10b981'
    }
  };

  let selectedMuscleKey = $state<string>('Brust');
  let selected = $derived(muscleData[selectedMuscleKey] || muscleData['Brust']);
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
  
  <!-- Header with Legend -->
  <div class="flex items-center justify-between flex-wrap gap-2">
    <div>
      <div class="text-sm font-extrabold flex items-center gap-1.5 text-[var(--text-main)]">
        <Icon name="dumbbell" class="text-[var(--color-activity)]" />
        <span>7-Tage Muskel-Volumen und Regeneration</span>
      </div>
      <p class="text-xs text-[var(--text-muted)] mt-0.5">Wissenschaftliche MEV/MAV/MRV Hypertrophie-Zonen</p>
    </div>

    <!-- Volume Legend -->
    <div class="flex items-center gap-2 text-[0.625rem] font-bold">
      <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[#0284c7]"></span> MEV (&lt;10 Sätze)</span>
      <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[#10b981]"></span> MAV (Optimal 10–18)</span>
      <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[#ef4444]"></span> MRV (&gt;20 Sätze)</span>
    </div>
  </div>

  <!-- Dual Silhouette Graphic: Anterior (Vorderseite) & Posterior (Rückseite) -->
  <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-around gap-4">
    
    <!-- 1. ANTERIOR (VORDERSEITE) -->
    <div class="flex flex-col items-center">
      <span class="text-[0.6875rem] font-extrabold text-[var(--text-muted)] uppercase mb-1">Vorderseite (Anterior)</span>
      <svg width="130" height="230" viewBox="0 0 130 230" class="select-none">
        <!-- Head -->
        <circle cx="65" cy="22" r="14" fill="var(--bg-surface-100)" stroke="var(--border-subtle)" stroke-width="1.5" />
        <!-- Neck -->
        <rect x="60" y="34" width="10" height="8" fill="var(--bg-surface-100)" />
        
        <!-- Chest (Pectoralis) -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Brust'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Brust'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <path d="M 46 45 Q 65 52 84 45 L 86 68 Q 65 76 44 68 Z" fill={muscleData['Brust'].color} stroke={selectedMuscleKey === 'Brust' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>

        <!-- Shoulders (Anterior Deltoids) -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Schultern'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Schultern'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <circle cx="36" cy="50" r="9" fill={muscleData['Schultern'].color} stroke={selectedMuscleKey === 'Schultern' ? '#ffffff' : 'none'} stroke-width="2" />
          <circle cx="94" cy="50" r="9" fill={muscleData['Schultern'].color} stroke={selectedMuscleKey === 'Schultern' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>

        <!-- Biceps -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Bizeps'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Bizeps'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <rect x="25" y="62" width="10" height="26" rx="4" fill={muscleData['Bizeps'].color} stroke={selectedMuscleKey === 'Bizeps' ? '#ffffff' : 'none'} stroke-width="2" />
          <rect x="95" y="62" width="10" height="26" rx="4" fill={muscleData['Bizeps'].color} stroke={selectedMuscleKey === 'Bizeps' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>

        <!-- Forearms -->
        <rect x="22" y="91" width="9" height="30" rx="3" fill="var(--bg-surface-100)" />
        <rect x="99" y="91" width="9" height="30" rx="3" fill="var(--bg-surface-100)" />

        <!-- Abs (Rectus Abdominis) -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Bauch'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Bauch'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <rect x="52" y="72" width="26" height="38" rx="4" fill={muscleData['Bauch'].color} stroke={selectedMuscleKey === 'Bauch' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>

        <!-- Quadriceps (Oberschenkel vorne) -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Quadrizeps'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Quadrizeps'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <path d="M 43 115 L 61 115 L 59 175 L 47 175 Z" fill={muscleData['Quadrizeps'].color} stroke={selectedMuscleKey === 'Quadrizeps' ? '#ffffff' : 'none'} stroke-width="2" />
          <path d="M 69 115 L 87 115 L 83 175 L 71 175 Z" fill={muscleData['Quadrizeps'].color} stroke={selectedMuscleKey === 'Quadrizeps' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>

        <!-- Calves / Shins -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Waden'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Waden'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <rect x="47" y="180" width="11" height="42" rx="4" fill={muscleData['Waden'].color} stroke={selectedMuscleKey === 'Waden' ? '#ffffff' : 'none'} stroke-width="2" />
          <rect x="72" y="180" width="11" height="42" rx="4" fill={muscleData['Waden'].color} stroke={selectedMuscleKey === 'Waden' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>
      </svg>
    </div>

    <!-- 2. POSTERIOR (RÜCKSEITE) -->
    <div class="flex flex-col items-center">
      <span class="text-[0.6875rem] font-extrabold text-[var(--text-muted)] uppercase mb-1">Rückseite (Posterior)</span>
      <svg width="130" height="230" viewBox="0 0 130 230" class="select-none">
        <!-- Head -->
        <circle cx="65" cy="22" r="14" fill="var(--bg-surface-100)" stroke="var(--border-subtle)" stroke-width="1.5" />
        
        <!-- Upper Back / Traps -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Rücken'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Rücken'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <path d="M 45 42 L 85 42 L 88 80 L 42 80 Z" fill={muscleData['Rücken'].color} stroke={selectedMuscleKey === 'Rücken' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>

        <!-- Rear Delts -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Schultern'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Schultern'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <circle cx="36" cy="50" r="9" fill={muscleData['Schultern'].color} />
          <circle cx="94" cy="50" r="9" fill={muscleData['Schultern'].color} />
        </g>

        <!-- Triceps -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Trizeps'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Trizeps'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <rect x="25" y="62" width="10" height="26" rx="4" fill={muscleData['Trizeps'].color} stroke={selectedMuscleKey === 'Trizeps' ? '#ffffff' : 'none'} stroke-width="2" />
          <rect x="95" y="62" width="10" height="26" rx="4" fill={muscleData['Trizeps'].color} stroke={selectedMuscleKey === 'Trizeps' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>

        <!-- Glutes (Gesäß) -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Gesäß'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Gesäß'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <path d="M 44 85 L 86 85 L 84 115 L 46 115 Z" fill={muscleData['Gesäß'].color} stroke={selectedMuscleKey === 'Gesäß' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>

        <!-- Hamstrings (Beinbeuger) -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Hamstrings'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Hamstrings'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <path d="M 44 118 L 61 118 L 59 175 L 46 175 Z" fill={muscleData['Hamstrings'].color} stroke={selectedMuscleKey === 'Hamstrings' ? '#ffffff' : 'none'} stroke-width="2" />
          <path d="M 69 118 L 86 118 L 84 175 L 71 175 Z" fill={muscleData['Hamstrings'].color} stroke={selectedMuscleKey === 'Hamstrings' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>

        <!-- Calves (Waden hinten) -->
        <g role="button" tabindex="0" onclick={() => selectedMuscleKey = 'Waden'} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectedMuscleKey = 'Waden'; }} class="transition-all hover:opacity-80 cursor-pointer">
          <rect x="47" y="180" width="11" height="42" rx="4" fill={muscleData['Waden'].color} stroke={selectedMuscleKey === 'Waden' ? '#ffffff' : 'none'} stroke-width="2" />
          <rect x="72" y="180" width="11" height="42" rx="4" fill={muscleData['Waden'].color} stroke={selectedMuscleKey === 'Waden' ? '#ffffff' : 'none'} stroke-width="2" />
        </g>
      </svg>
    </div>

  </div>

  <!-- Interactive Detail Card for Selected Muscle -->
  <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 space-y-2.5">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div class="flex items-center gap-2">
        <span class="w-3 h-3 rounded-full" style="background-color: {selected.color};"></span>
        <h3 class="text-sm font-extrabold text-[var(--text-main)]">{selected.name}</h3>
        <Badge variant={selected.status === 'optimal' ? 'success' : 'default'} class="text-[0.625rem]">
          {selected.statusText}
        </Badge>
      </div>

      <div class="text-xs font-bold text-[var(--text-main)] tabular-nums">
        {selected.setsWeekly} Sätze &bull; {selected.volumeKg.toLocaleString('de-DE')} kg Tonnage
      </div>
    </div>

    <!-- Recovery Status Bar -->
    <div class="space-y-1">
      <div class="flex justify-between text-[0.6875rem] text-[var(--text-muted)]">
        <span>Erholungsstatus:</span>
        <span class="font-bold {selected.recoveryHoursLeft === 0 ? 'text-emerald-500' : 'text-amber-500'}">
          {selected.recoveryHoursLeft === 0 ? 'Vollständig regeneriert (Bereit für Training)' : `Noch ca. ${selected.recoveryHoursLeft}h Regeneration empfohlen`}
        </span>
      </div>
      <div class="h-1.5 rounded-full bg-[var(--border-subtle)] overflow-hidden">
        <div
          class="h-full bg-[var(--color-primary)] transition-all duration-500"
          style="width: {Math.min(100, ((48 - selected.recoveryHoursLeft) / 48) * 100)}%;"
        ></div>
      </div>
    </div>

    <!-- Contributing Exercises -->
    <div class="pt-2 border-t border-[var(--border-subtle)]/60 text-xs">
      <span class="text-[0.6875rem] text-[var(--text-muted)] font-semibold block mb-1">Aktivierte Übungen diese Woche:</span>
      <div class="flex flex-wrap gap-1.5">
        {#each selected.exercises as ex}
          <span class="px-2 py-0.5 rounded-lg bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[0.6875rem] text-[var(--text-main)]">
            {ex}
          </span>
        {/each}
      </div>
    </div>
  </div>

</div>
