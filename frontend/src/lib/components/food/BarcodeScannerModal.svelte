<script lang="ts">
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
    class="fixed inset-0 z-100 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md"
    onclick={(e) => {
      if (e.target === e.currentTarget) onclose();
    }}
    role="presentation"
  >
    <div
      class="w-full max-w-[440px] overflow-hidden rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] shadow-[var(--shadow-lift)]"
    >
      <!-- Topbar -->
      <div class="flex items-center justify-between border-b border-[var(--border-subtle)] p-4">
        <button
          type="button"
          class="btn btn-secondary px-3 py-1 text-xs"
          onclick={() => (isTorchOn = !isTorchOn)}
        >
          {isTorchOn ? ' Blitz: An' : ' Blitz: Aus'}
        </button>
        <span class="text-sm font-bold text-[var(--text-main)]">Lebensmittel-Scanner</span>
        <button type="button" class="btn btn-secondary p-1 text-xs" onclick={onclose}
          >&times;</button
        >
      </div>

      <!-- Viewfinder Area -->
      <div class="relative flex h-72 items-center justify-center overflow-hidden bg-black">
        <!-- Target Box -->
        <div
          class="relative flex h-40 w-56 items-center justify-center rounded-2xl border-2 border-white/80 shadow-[0_0_0_9999px_rgba(0,0,0,0.6)]"
        >
          <!-- Laser Animation Line -->
          <div
            class="absolute inset-x-2 h-0.5 animate-[scanLaser_2s_ease-in-out_infinite] bg-red-500 shadow-[0_0_8px_#ef4444]"
          ></div>

          <!-- Corner brackets -->
          <div
            class="absolute -top-1 -left-1 h-4 w-4 border-t-4 border-l-4 border-[var(--color-primary)]"
          ></div>
          <div
            class="absolute -top-1 -right-1 h-4 w-4 border-t-4 border-r-4 border-[var(--color-primary)]"
          ></div>
          <div
            class="absolute -bottom-1 -left-1 h-4 w-4 border-b-4 border-l-4 border-[var(--color-primary)]"
          ></div>
          <div
            class="absolute -right-1 -bottom-1 h-4 w-4 border-r-4 border-b-4 border-[var(--color-primary)]"
          ></div>
        </div>
      </div>

      <!-- Instructions & Mock Trigger -->
      <div class="space-y-3 bg-[var(--bg-surface-0)] p-4 text-center">
        <p class="text-xs text-[var(--text-muted)]">
          Halte den Barcode (EAN-13 / UPC) in das Sichtfeld zur automatischen Nährwerterfassung.
        </p>
        <Btn variant="primary" class="w-full" onclick={simulateScan}>Barcode-Scan simulieren</Btn>
      </div>
    </div>
  </div>
{/if}

<style>
  @keyframes scanLaser {
    0%,
    100% {
      top: 10%;
    }
    50% {
      top: 90%;
    }
  }
</style>
