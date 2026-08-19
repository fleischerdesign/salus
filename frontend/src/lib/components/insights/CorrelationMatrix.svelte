<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let selectedFact = $state<string | null>(
    'Starker Zusammenhang (r = -0.74, p = 0.001): Über 7.5h Schlaf senken den systolischen Blutdruck um durchschnittlich 6.2 mmHg.'
  );

  function selectCell(text: string) {
    selectedFact = text;
  }
</script>

<div class="rounded-lg border border-border-subtle bg-surface-0 p-4 shadow-card">
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-text-main">
      <Icon name="insights" class="text-primary" />
      <span>Biometrische Korrelations-Matrix (n = 90 Tage)</span>
    </div>
    <Badge variant="success">p &lt; 0.01 signifikant</Badge>
  </div>

  <div class="mb-3 grid grid-cols-4 gap-1.5 text-xs">
    <!-- Header -->
    <div class="rounded bg-surface-50 p-2 text-center font-bold text-text-muted">Faktor</div>
    <div class="rounded bg-surface-50 p-2 text-center font-bold text-text-muted">Schlaf</div>
    <div class="rounded bg-surface-50 p-2 text-center font-bold text-text-muted">Blutdruck</div>
    <div class="rounded bg-surface-50 p-2 text-center font-bold text-text-muted">1RM Kraft</div>

    <!-- Row 1 -->
    <div class="rounded bg-surface-50 p-2 font-bold">Schlafqualität</div>
    <div class="rounded bg-surface-50 p-2 text-center font-mono">1.00</div>
    <button
      type="button"
      onclick={() =>
        selectCell(
          'Schlaf vs Blutdruck: r = -0.74 (p = 0.001). Tieferer Schlaf korreliert signifikant mit optimalem Blutdruck.'
        )}
      class="cursor-pointer rounded bg-success-soft p-2 text-center font-mono font-bold text-success transition-all hover:brightness-110"
    >
      -0.74*
    </button>
    <button
      type="button"
      onclick={() =>
        selectCell(
          'Schlaf vs 1RM: r = +0.62 (p = 0.004). Erholte Muskelgruppen bringen 8% höhere Maximalkraft.'
        )}
      class="cursor-pointer rounded bg-primary-soft p-2 text-center font-mono font-bold text-primary transition-all hover:brightness-110"
    >
      +0.62*
    </button>

    <!-- Row 2 -->
    <div class="rounded bg-surface-50 p-2 font-bold">Syst. Blutdruck</div>
    <button
      type="button"
      onclick={() => selectCell('Blutdruck vs Schlaf: r = -0.74 (p = 0.001).')}
      class="cursor-pointer rounded bg-success-soft p-2 text-center font-mono font-bold text-success transition-all hover:brightness-110"
    >
      -0.74*
    </button>
    <div class="rounded bg-surface-50 p-2 text-center font-mono">1.00</div>
    <div class="rounded bg-surface-50 p-2 text-center font-mono text-text-muted">-0.12</div>

    <!-- Row 3 -->
    <div class="rounded bg-surface-50 p-2 font-bold">Protein (g/Tag)</div>
    <div class="rounded bg-surface-50 p-2 text-center font-mono text-text-muted">+0.22</div>
    <div class="rounded bg-surface-50 p-2 text-center font-mono text-text-muted">-0.08</div>
    <button
      type="button"
      onclick={() =>
        selectCell(
          'Protein vs 1RM Kraft: r = +0.81 (p < 0.001). Hohe Proteinzufuhr korreliert extrem stark mit linearem Kraftzuwachs.'
        )}
      class="cursor-pointer rounded bg-primary-soft p-2 text-center font-mono font-bold text-primary transition-all hover:brightness-110"
    >
      +0.81*
    </button>
  </div>

  {#if selectedFact}
    <div class="rounded-sm border border-border-subtle bg-surface-50 p-2.5 text-xs text-text-muted">
      <strong class="text-text-main">Erkenntnis:</strong>
      {selectedFact}
    </div>
  {/if}
</div>
