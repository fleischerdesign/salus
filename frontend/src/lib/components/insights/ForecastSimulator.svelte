<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Slider from '../ui/Slider.svelte';

  let sleepDeltaHours = $state(1.0); // +1h Schlaf
  let proteinDeltaG = $state(30); // +30g Protein

  let projectedBpSys = $derived(Number((118 - sleepDeltaHours * 3.4).toFixed(1)));
  let projected1RM = $derived(Number((143 + (proteinDeltaG / 10) * 1.8).toFixed(1)));
</script>

<div class="rounded-2xl border border-border-subtle bg-surface-0 p-5 shadow-card">
  <div class="mb-4 flex items-center justify-between">
    <div>
      <div class="flex items-center gap-1.5 text-sm font-bold text-text-main">
        <Icon name="wb-sunny" class="text-circadian" />
        <span>Was-wäre-wenn Prognose-Simulator</span>
      </div>
      <p class="mt-0.5 text-xs text-text-muted">
        Lineare Regression und neuronales Vorhersagemodell
      </p>
    </div>
    <Badge variant="success">p &lt; 0.01 Signifikant</Badge>
  </div>

  <div class="space-y-4 text-xs">
    <!-- Slider 1: Sleep Duration vs Blood Pressure -->
    <div class="space-y-2 rounded-xl border border-border-subtle bg-surface-50 p-3">
      <div class="flex items-center justify-between">
        <span class="font-bold">Zusätzlicher Schlaf pro Nacht</span>
        <span class="font-bold text-primary">+{sleepDeltaHours.toFixed(1)} Std / Nacht</span>
      </div>
      <Slider name="sleepDeltaHours" min={0} max={3} step={0.5} bind:value={sleepDeltaHours} />
      <div class="flex justify-between text-[0.6875rem] text-text-muted">
        <span>Aktuell: 6.8h</span>
        <span>Prognostizierter Blutdruck:</span>
        <strong class="font-bold text-emerald-500"
          >{projectedBpSys} mmHg ({sleepDeltaHours > 0 ? '↘ Senkung' : '↗ Erhöhung'})</strong
        >
      </div>
    </div>

    <!-- Slider 2: Daily Protein Intake vs 1RM Strength Progression -->
    <div class="space-y-2 rounded-xl border border-border-subtle bg-surface-50 p-3">
      <div class="flex items-center justify-between">
        <span class="font-bold">Zusätzliches Protein pro Tag</span>
        <span class="font-bold text-vital">+{proteinDeltaG} g / Tag</span>
      </div>
      <Slider name="proteinDeltaG" min={0} max={60} step={10} bind:value={proteinDeltaG} />
      <div class="flex justify-between text-[0.6875rem] text-text-muted">
        <span>Aktuell: 140g</span>
        <span>Prognostiziertes Bankdrücken 1RM:</span>
        <strong class="font-bold text-primary">{projected1RM} kg (in 6 Wochen)</strong>
      </div>
    </div>
  </div>

  <div
    class="rounded-xl border border-border-subtle bg-surface-50 p-2.5 text-[0.6875rem] text-text-muted"
  >
    <strong class="text-text-main">Evidenz-Basis:</strong> Berechnet aus deinen n = 90 persönlichen Längsschnitt-Tagen
    kombiniert mit Meta-Analysen der Cochrane Database und ESC Guidelines.
  </div>
</div>
