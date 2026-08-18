<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  interface ExerciseProgress {
    name: string;
    e1RM: number;
    bwRatio: number; // Ratio to 81.8kg bodyweight
    tier: 'Anfänger' | 'Fortgeschritten' | 'Athlet' | 'Elite';
    tierColor: string;
    history: { date: string; weight: number; reps: number; e1RM: number }[];
  }

  const exerciseProfiles: Record<string, ExerciseProgress> = {
    'Bankdrücken': {
      name: 'Bankdrücken (Langhantel)',
      e1RM: 143.0,
      bwRatio: 1.75,
      tier: 'Elite',
      tierColor: '#10b981',
      history: [
        { date: '01. Jun', weight: 100, reps: 8, e1RM: 124 },
        { date: '15. Jun', weight: 105, reps: 8, e1RM: 130 },
        { date: '01. Jul', weight: 110, reps: 6, e1RM: 132 },
        { date: '15. Jul', weight: 115, reps: 6, e1RM: 138 },
        { date: '01. Aug', weight: 120, reps: 5, e1RM: 140 },
        { date: '17. Aug', weight: 122.5, reps: 5, e1RM: 143 }
      ]
    },
    'Kniebeugen': {
      name: 'Kniebeugen (High Bar)',
      e1RM: 155.0,
      bwRatio: 1.90,
      tier: 'Athlet',
      tierColor: '#0284c7',
      history: [
        { date: '01. Jun', weight: 115, reps: 8, e1RM: 142 },
        { date: '15. Jun', weight: 120, reps: 6, e1RM: 144 },
        { date: '01. Jul', weight: 125, reps: 6, e1RM: 150 },
        { date: '15. Jul', weight: 127.5, reps: 5, e1RM: 152 },
        { date: '01. Aug', weight: 130, reps: 5, e1RM: 155 }
      ]
    },
    'Kreuzheben': {
      name: 'Kreuzheben (Konventionell)',
      e1RM: 190.0,
      bwRatio: 2.32,
      tier: 'Elite',
      tierColor: '#10b981',
      history: [
        { date: '01. Jun', weight: 140, reps: 6, e1RM: 168 },
        { date: '01. Jul', weight: 155, reps: 5, e1RM: 180 },
        { date: '01. Aug', weight: 165, reps: 4, e1RM: 190 }
      ]
    },
    'Overhead Press': {
      name: 'Schulterdrücken (Overhead Press)',
      e1RM: 82.5,
      bwRatio: 1.01,
      tier: 'Athlet',
      tierColor: '#0284c7',
      history: [
        { date: '01. Jun', weight: 60, reps: 8, e1RM: 74 },
        { date: '01. Jul', weight: 65, reps: 6, e1RM: 78 },
        { date: '01. Aug', weight: 70, reps: 5, e1RM: 82.5 }
      ]
    }
  };

  let selectedKey = $state<string>('Bankdrücken');
  let selectedProfile = $derived(exerciseProfiles[selectedKey] || exerciseProfiles['Bankdrücken']);

  // Relative Strength Tier Standards for 81.8 kg
  const tiers = [
    { name: 'Anfänger', maxRatio: 1.0, color: '#94a3b8' },
    { name: 'Fortgeschritten', maxRatio: 1.3, color: '#eab308' },
    { name: 'Athlet', maxRatio: 1.6, color: '#0284c7' },
    { name: 'Elite', maxRatio: 2.5, color: '#10b981' }
  ];
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
  
  <!-- Header with Exercise Pills -->
  <div class="flex items-center justify-between flex-wrap gap-3">
    <div>
      <div class="text-sm font-extrabold flex items-center gap-1.5 text-[var(--text-main)]">
        <Icon name="dumbbell" class="text-[var(--color-activity)]" />
        <span>1RM Maximalkraft-Entwicklung und Relativkraft</span>
      </div>
      <p class="text-xs text-[var(--text-muted)] mt-0.5">Berechnet nach Brzycki und Epley im Verhältnis zu 81.8 kg Körpergewicht</p>
    </div>

    <!-- Exercise Selector Pills -->
    <div class="flex gap-1.5 overflow-x-auto no-scrollbar">
      {#each Object.keys(exerciseProfiles) as k}
        <button
          type="button"
          onclick={() => selectedKey = k}
          class="px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap {selectedKey === k ? 'bg-[var(--color-primary)] text-white shadow-xs' : 'bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        >
          {k}
        </button>
      {/each}
    </div>
  </div>

  <!-- Main Score Cards -->
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
    
    <!-- 1RM Max -->
    <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-3.5 flex items-center justify-between">
      <div>
        <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase block">Geschätztes 1RM</span>
        <span class="text-2xl font-extrabold text-[var(--color-activity)] tabular-nums">
          {selectedProfile.e1RM} kg
        </span>
      </div>
      <Badge variant="success" class="text-[0.625rem]">+15.3% Zuwachs</Badge>
    </div>

    <!-- Relative Strength Ratio -->
    <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-3.5 flex items-center justify-between">
      <div>
        <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase block">Relativkraft-Koeffizient</span>
        <span class="text-2xl font-extrabold text-[var(--color-primary)] tabular-nums">
          {selectedProfile.bwRatio.toFixed(2)}&times;
        </span>
      </div>
      <span class="text-xs text-[var(--text-muted)] font-bold">des Körpergewichts</span>
    </div>

    <!-- Strength Tier -->
    <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-3.5 flex items-center justify-between">
      <div>
        <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase block">IPF / Wilks Einstufung</span>
        <span class="text-xl font-extrabold text-[var(--text-main)] block" style="color: {selectedProfile.tierColor};">
          {selectedProfile.tier}
        </span>
      </div>
      <div class="w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold text-xs" style="border-color: {selectedProfile.tierColor}; color: {selectedProfile.tierColor};">
        Stern
      </div>
    </div>

  </div>

  <!-- SVG Kraftverlauf-Spline -->
  <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 space-y-2">
    <div class="flex justify-between items-center text-xs">
      <span class="font-extrabold text-[var(--text-main)]">{selectedProfile.name} Verlauf:</span>
      <span class="text-[0.6875rem] text-[var(--text-muted)] font-semibold">6-Monats-Trajektorie</span>
    </div>

    <div class="w-full py-2">
      <svg class="w-full h-36" viewBox="0 0 500 120" preserveAspectRatio="none">
        <!-- Subtle Horizontal Grid Lines -->
        <line x1="0" y1="20" x2="500" y2="20" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="3 3" />
        <line x1="0" y1="60" x2="500" y2="60" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="3 3" />
        <line x1="0" y1="100" x2="500" y2="100" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="3 3" />

        <!-- Gradient Area Fill -->
        <defs>
          <linearGradient id="strengthAreaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#ea580c" stop-opacity="0.3" />
            <stop offset="100%" stop-color="#ea580c" stop-opacity="0.0" />
          </linearGradient>
        </defs>

        <path
          d="M 20 100 L 110 80 L 200 68 L 290 45 L 390 32 L 480 18 L 480 120 L 20 120 Z"
          fill="url(#strengthAreaGrad)"
        />

        <!-- Main Trend Stroke -->
        <path
          d="M 20 100 L 110 80 L 200 68 L 290 45 L 390 32 L 480 18"
          fill="none"
          stroke="var(--color-activity)"
          stroke-width="3.5"
          stroke-linecap="round"
        />

        <!-- Data Point Circles -->
        <circle cx="20" cy="100" r="4.5" fill="var(--color-activity)" stroke="#ffffff" stroke-width="2" />
        <circle cx="110" cy="80" r="4.5" fill="var(--color-activity)" stroke="#ffffff" stroke-width="2" />
        <circle cx="200" cy="68" r="4.5" fill="var(--color-activity)" stroke="#ffffff" stroke-width="2" />
        <circle cx="290" cy="45" r="4.5" fill="var(--color-activity)" stroke="#ffffff" stroke-width="2" />
        <circle cx="390" cy="32" r="4.5" fill="var(--color-activity)" stroke="#ffffff" stroke-width="2" />
        <circle cx="480" cy="18" r="6" fill="#10b981" stroke="#ffffff" stroke-width="2.5" />
      </svg>
    </div>

    <div class="flex justify-between text-[0.6875rem] text-[var(--text-muted)] px-2 font-semibold">
      <span>01. Juni ({selectedProfile.history[0]?.e1RM} kg)</span>
      <span>01. Juli ({selectedProfile.history[2]?.e1RM} kg)</span>
      <span class="font-bold text-emerald-500">Heute (PR: {selectedProfile.e1RM} kg)</span>
    </div>
  </div>

</div>
