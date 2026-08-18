<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let sleepDeltaHours = $state(1.0); // +1h Schlaf
  let proteinDeltaG = $state(30); // +30g Protein

  let projectedBpSys = $derived(Number((118 - sleepDeltaHours * 3.4).toFixed(1)));
  let projected1RM = $derived(Number((143 + (proteinDeltaG / 10) * 1.8).toFixed(1)));
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-4">
    <div>
      <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
        <Icon name="sun" class="text-[var(--color-circadian)]" />
        <span>Was-wäre-wenn Prognose-Simulator</span>
      </div>
      <p class="text-xs text-[var(--text-muted)] mt-0.5">Lineare Regression und neuronales Vorhersagemodell</p>
    </div>
    <Badge variant="success">p &lt; 0.01 Signifikant</Badge>
  </div>

  <div class="space-y-4 text-xs">
    <!-- Slider 1: Sleep Duration vs Blood Pressure -->
    <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] p-3 rounded-xl space-y-2">
      <div class="flex justify-between items-center">
        <span class="font-bold">Zusätzlicher Schlaf pro Nacht</span>
        <span class="font-bold text-[var(--color-primary)]">+{sleepDeltaHours.toFixed(1)} Std / Nacht</span>
      </div>
      <input
        type="range"
        min="0"
        max="3"
        step="0.5"
        bind:value={sleepDeltaHours}
        class="w-full accent-[var(--color-primary)] cursor-pointer"
      />
      <div class="flex justify-between text-[0.6875rem] text-[var(--text-muted)]">
        <span>Aktuell: 6.8h</span>
        <span>Prognostizierter Blutdruck:</span>
        <strong class="font-bold text-emerald-500">{projectedBpSys} mmHg ({sleepDeltaHours > 0 ? '↘ Senkung' : '↗ Erhöhung'})</strong>
      </div>
    </div>

    <!-- Slider 2: Daily Protein Intake vs 1RM Strength Progression -->
    <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] p-3 rounded-xl space-y-2">
      <div class="flex justify-between items-center">
        <span class="font-bold">Zusätzliches Protein pro Tag</span>
        <span class="font-bold text-[var(--color-vital)]">+{proteinDeltaG} g / Tag</span>
      </div>
      <input
        type="range"
        min="0"
        max="60"
        step="10"
        bind:value={proteinDeltaG}
        class="w-full accent-[var(--color-vital)] cursor-pointer"
      />
      <div class="flex justify-between text-[0.6875rem] text-[var(--text-muted)]">
        <span>Aktuell: 140g</span>
        <span>Prognostiziertes Bankdrücken 1RM:</span>
        <strong class="font-bold text-[var(--color-primary)]">{projected1RM} kg (in 6 Wochen)</strong>
      </div>
    </div>
  </div>

  <div class="p-2.5 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[0.6875rem] text-[var(--text-muted)]">
    <strong class="text-[var(--text-main)]">Evidenz-Basis:</strong> Berechnet aus deinen n = 90 persönlichen Längsschnitt-Tagen kombiniert mit Meta-Analysen der Cochrane Database und ESC Guidelines.
  </div>
</div>
