<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Btn from '../ui/Btn.svelte';

  let {
    open = false,
    onclose,
    ondetect
  } = $props<{
    open: boolean;
    onclose: () => void;
    ondetect?: (barcode: string) => void;
  }>();

  let isTorchOn = $state(false);

  function simulateScan() {
    alert('Barcode 4008400404127 erkannt: "Haferflocken zart (Bio)" • 370 kcal, 13.5g Protein.');
    ondetect?.('4008400404127');
    onclose();
  }
</script>

{#if open}
  <div
    class="fixed inset-0 bg-black/80 backdrop-blur-md z-100 flex items-center justify-center p-4"
    onclick={(e) => {
      if (e.target === e.currentTarget) onclose();
    }}
    role="presentation"
  >
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl max-w-[440px] w-full overflow-hidden shadow-[var(--shadow-lift)]">
      <!-- Topbar -->
      <div class="flex items-center justify-between p-4 border-b border-[var(--border-subtle)]">
        <button
          type="button"
          class="btn btn-secondary text-xs px-3 py-1"
          onclick={() => isTorchOn = !isTorchOn}
        >
          {isTorchOn ? ' Blitz: An' : ' Blitz: Aus'}
        </button>
        <span class="text-sm font-bold text-[var(--text-main)]">Lebensmittel-Scanner</span>
        <button type="button" class="btn btn-secondary text-xs p-1" onclick={onclose}>&times;</button>
      </div>

      <!-- Viewfinder Area -->
      <div class="relative bg-black h-72 flex items-center justify-center overflow-hidden">
        <!-- Target Box -->
        <div class="relative w-56 h-40 border-2 border-white/80 rounded-2xl flex items-center justify-center shadow-[0_0_0_9999px_rgba(0,0,0,0.6)]">
          <!-- Laser Animation Line -->
          <div class="absolute inset-x-2 h-0.5 bg-red-500 shadow-[0_0_8px_#ef4444] animate-[scanLaser_2s_ease-in-out_infinite]"></div>
          
          <!-- Corner brackets -->
          <div class="absolute -top-1 -left-1 w-4 h-4 border-t-4 border-l-4 border-[var(--color-primary)]"></div>
          <div class="absolute -top-1 -right-1 w-4 h-4 border-t-4 border-r-4 border-[var(--color-primary)]"></div>
          <div class="absolute -bottom-1 -left-1 w-4 h-4 border-b-4 border-l-4 border-[var(--color-primary)]"></div>
          <div class="absolute -bottom-1 -right-1 w-4 h-4 border-b-4 border-r-4 border-[var(--color-primary)]"></div>
        </div>
      </div>

      <!-- Instructions & Mock Trigger -->
      <div class="p-4 bg-[var(--bg-surface-0)] text-center space-y-3">
        <p class="text-xs text-[var(--text-muted)]">
          Halte den Barcode (EAN-13 / UPC) in das Sichtfeld zur automatischen Nährwerterfassung.
        </p>
        <Btn variant="primary" class="w-full" onclick={simulateScan}>
          Barcode-Scan simulieren
        </Btn>
      </div>
    </div>
  </div>
{/if}

<style>
  @keyframes scanLaser {
    0%, 100% { top: 10%; }
    50% { top: 90%; }
  }
</style>
