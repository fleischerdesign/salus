<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  let {
    open = false,
    onclose
  } = $props<{
    open: boolean;
    onclose: () => void;
  }>();

  let fieldSelections = $state<Record<string, 'mine' | 'theirs'>>({
    weight: 'mine',
    note: 'theirs'
  });

  function resolve() {
    alert('Konflikt gelöst: Änderungen wurden lokal zusammengeführt und an den Server synchronisiert.');
    onclose();
  }
</script>

{#if open}
  <div
    class="fixed inset-0 bg-black/65 backdrop-blur-md z-100 flex items-center justify-center p-4"
    onclick={(e) => {
      if (e.target === e.currentTarget) onclose();
    }}
    role="presentation"
  >
    <div class="glass-panel rounded-3xl p-6 max-w-[520px] w-full shadow-2xl space-y-4 animate-modal-pop">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded-full bg-[var(--color-vital-soft)] text-[var(--color-vital)] flex items-center justify-center font-bold text-xs">
            !
          </div>
          <h2 class="text-sm font-bold text-[var(--text-main)]">Offline-Konflikt auflösen</h2>
        </div>
        <button type="button" class="btn btn-secondary text-xs p-1" onclick={onclose}>&times;</button>
      </div>

      <p class="text-xs text-[var(--text-muted)] mb-4">
        Dieser Eintrag (Körpergewicht, 14.08.) wurde auf einem anderen Gerät parallel geändert. Wähle pro Feld den gewünschten Wert:
      </p>

      <div class="space-y-3 mb-5">
        <!-- Field 1: Weight -->
        <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3">
          <span class="text-xs font-bold block mb-2">Feld: Körpergewicht</span>
          <div class="grid grid-cols-2 gap-2">
            <button
              type="button"
              onclick={() => fieldSelections.weight = 'mine'}
              class="p-2 rounded-lg border text-left cursor-pointer transition-all {fieldSelections.weight === 'mine' ? 'border-[var(--color-primary)] bg-[var(--bg-surface-0)] shadow-xs' : 'border-transparent text-[var(--text-muted)]'}"
            >
              <span class="text-[0.6875rem] font-bold block text-[var(--color-primary)]">Lokal (Dieses Gerät)</span>
              <span class="text-sm font-mono font-bold">81.8 kg</span>
            </button>

            <button
              type="button"
              onclick={() => fieldSelections.weight = 'theirs'}
              class="p-2 rounded-lg border text-left cursor-pointer transition-all {fieldSelections.weight === 'theirs' ? 'border-[var(--color-primary)] bg-[var(--bg-surface-0)] shadow-xs' : 'border-transparent text-[var(--text-muted)]'}"
            >
              <span class="text-[0.6875rem] font-bold block text-[var(--color-circadian)]">Server (Anderes Gerät)</span>
              <span class="text-sm font-mono font-bold">82.0 kg</span>
            </button>
          </div>
        </div>

        <!-- Field 2: Note -->
        <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3">
          <span class="text-xs font-bold block mb-2">Feld: Notiz</span>
          <div class="grid grid-cols-2 gap-2">
            <button
              type="button"
              onclick={() => fieldSelections.note = 'mine'}
              class="p-2 rounded-lg border text-left cursor-pointer transition-all {fieldSelections.note === 'mine' ? 'border-[var(--color-primary)] bg-[var(--bg-surface-0)] shadow-xs' : 'border-transparent text-[var(--text-muted)]'}"
            >
              <span class="text-[0.6875rem] font-bold block text-[var(--color-primary)]">Lokal</span>
              <span class="text-xs">Nach dem Laufen gewogen</span>
            </button>

            <button
              type="button"
              onclick={() => fieldSelections.note = 'theirs'}
              class="p-2 rounded-lg border text-left cursor-pointer transition-all {fieldSelections.note === 'theirs' ? 'border-[var(--color-primary)] bg-[var(--bg-surface-0)] shadow-xs' : 'border-transparent text-[var(--text-muted)]'}"
            >
              <span class="text-[0.6875rem] font-bold block text-[var(--color-circadian)]">Server</span>
              <span class="text-xs">Morgens nüchtern</span>
            </button>
          </div>
        </div>
      </div>

      <div class="flex gap-2">
        <Btn variant="secondary" class="flex-1" onclick={onclose}>Abbrechen</Btn>
        <Btn variant="primary" class="flex-1" onclick={resolve}>Zusammenführen und Speichern</Btn>
      </div>
    </div>
  </div>
{/if}
