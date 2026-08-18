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

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-[var(--radius-lg)] p-4 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="insights" class="text-[var(--color-primary)]" />
      <span>Biometrische Korrelations-Matrix (n = 90 Tage)</span>
    </div>
    <Badge variant="success">p &lt; 0.01 signifikant</Badge>
  </div>

  <div class="grid grid-cols-4 gap-1.5 mb-3 text-xs">
    <!-- Header -->
    <div class="bg-[var(--bg-surface-50)] p-2 rounded text-center font-bold text-[var(--text-muted)]">Faktor</div>
    <div class="bg-[var(--bg-surface-50)] p-2 rounded text-center font-bold text-[var(--text-muted)]">Schlaf</div>
    <div class="bg-[var(--bg-surface-50)] p-2 rounded text-center font-bold text-[var(--text-muted)]">Blutdruck</div>
    <div class="bg-[var(--bg-surface-50)] p-2 rounded text-center font-bold text-[var(--text-muted)]">1RM Kraft</div>

    <!-- Row 1 -->
    <div class="bg-[var(--bg-surface-50)] p-2 rounded font-bold">Schlafqualität</div>
    <div class="bg-[var(--bg-surface-50)] p-2 rounded text-center font-mono">1.00</div>
    <button
      type="button"
      onclick={() => selectCell('Schlaf vs Blutdruck: r = -0.74 (p = 0.001). Tieferer Schlaf korreliert signifikant mit optimalem Blutdruck.')}
      class="bg-[var(--color-success-soft)] text-[var(--color-success)] p-2 rounded text-center font-mono font-bold hover:brightness-110 transition-all cursor-pointer"
    >
      -0.74*
    </button>
    <button
      type="button"
      onclick={() => selectCell('Schlaf vs 1RM: r = +0.62 (p = 0.004). Erholte Muskelgruppen bringen 8% höhere Maximalkraft.')}
      class="bg-[var(--color-primary-soft)] text-[var(--color-primary)] p-2 rounded text-center font-mono font-bold hover:brightness-110 transition-all cursor-pointer"
    >
      +0.62*
    </button>

    <!-- Row 2 -->
    <div class="bg-[var(--bg-surface-50)] p-2 rounded font-bold">Syst. Blutdruck</div>
    <button
      type="button"
      onclick={() => selectCell('Blutdruck vs Schlaf: r = -0.74 (p = 0.001).')}
      class="bg-[var(--color-success-soft)] text-[var(--color-success)] p-2 rounded text-center font-mono font-bold hover:brightness-110 transition-all cursor-pointer"
    >
      -0.74*
    </button>
    <div class="bg-[var(--bg-surface-50)] p-2 rounded text-center font-mono">1.00</div>
    <div class="bg-[var(--bg-surface-50)] p-2 rounded text-center font-mono text-[var(--text-muted)]">-0.12</div>

    <!-- Row 3 -->
    <div class="bg-[var(--bg-surface-50)] p-2 rounded font-bold">Protein (g/Tag)</div>
    <div class="bg-[var(--bg-surface-50)] p-2 rounded text-center font-mono text-[var(--text-muted)]">+0.22</div>
    <div class="bg-[var(--bg-surface-50)] p-2 rounded text-center font-mono text-[var(--text-muted)]">-0.08</div>
    <button
      type="button"
      onclick={() => selectCell('Protein vs 1RM Kraft: r = +0.81 (p < 0.001). Hohe Proteinzufuhr korreliert extrem stark mit linearem Kraftzuwachs.')}
      class="bg-[var(--color-primary-soft)] text-[var(--color-primary)] p-2 rounded text-center font-mono font-bold hover:brightness-110 transition-all cursor-pointer"
    >
      +0.81*
    </button>
  </div>

  {#if selectedFact}
    <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-[var(--radius-sm)] p-2.5 text-xs text-[var(--text-muted)]">
      <strong class="text-[var(--text-main)]">Erkenntnis:</strong> {selectedFact}
    </div>
  {/if}
</div>
