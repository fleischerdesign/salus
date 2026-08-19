<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import { BrowserMultiFormatOneDReader } from '@zxing/browser';

  interface Props {
    open: boolean;
    onclose: () => void;
    ondetect?: (barcode: string) => void;
  }

  let { open = false, onclose, ondetect }: Props = $props();

  let videoEl = $state<HTMLVideoElement | null>(null);
  let stopStream = $state<(() => void) | null>(null);
  let cameraError = $state<string | null>(null);
  let isScanning = $state(false);
  let manualBarcode = $state('');

  function stopCamera() {
    if (stopStream) {
      stopStream();
      stopStream = null;
    }
    if (videoEl && videoEl.srcObject) {
      const stream = videoEl.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoEl.srcObject = null;
    }
    isScanning = false;
  }

  $effect(() => {
    if (!open) {
      stopCamera();
      cameraError = null;
      manualBarcode = '';
      return;
    }

    cameraError = null;
    isScanning = true;

    // Small delay to ensure video element is mounted in DOM
    const timer = setTimeout(() => {
      if (!videoEl) return;

      const reader = new BrowserMultiFormatOneDReader();
      let cancelled = false;

      reader
        .decodeFromConstraints(
          {
            video: {
              facingMode: 'environment',
              width: { ideal: 1280 },
              height: { ideal: 720 }
            }
          },
          videoEl,
          (result, _error) => {
            if (cancelled) return;
            if (result && result.getText()) {
              const code = result.getText().trim();
              if (code) {
                cancelled = true;
                stopCamera();
                ondetect?.(code);
                onclose();
              }
            }
          }
        )
        .then((controls) => {
          if (cancelled) {
            controls.stop();
            return;
          }
          stopStream = () => controls.stop();
        })
        .catch((err) => {
          console.warn('[BarcodeScanner] Camera access failed:', err);
          cameraError =
            err instanceof Error ? err.message : 'Kamera nicht verfügbar oder Zugriff verweigert.';
          isScanning = false;
        });

      return () => {
        cancelled = true;
        stopCamera();
      };
    }, 100);

    return () => {
      clearTimeout(timer);
      stopCamera();
    };
  });

  function handleManualSubmit() {
    const code = manualBarcode.trim();
    if (!code) return;
    stopCamera();
    ondetect?.(code);
    onclose();
  }
</script>

<Modal
  {open}
  title="Barcode scannen"
  subtitle="Halte die EAN-13 oder den UPC-Barcode eines Lebensmittels vor die Kamera"
  icon="qr_code_scanner"
  size="lg"
  onclose={() => {
    stopCamera();
    onclose();
  }}
>
  <div class="space-y-4">
    <!-- Camera Viewport Container -->
    <div
      class="relative flex h-64 w-full items-center justify-center overflow-hidden rounded-2xl border border-[var(--border-subtle)] bg-black shadow-inner"
    >
      <video bind:this={videoEl} class="h-full w-full object-cover" muted playsinline autoplay
      ></video>

      <!-- Viewfinder Overlay & Reticle -->
      {#if isScanning && !cameraError}
        <div class="pointer-events-none absolute inset-0 flex items-center justify-center">
          <!-- Target Frame -->
          <div
            class="relative h-36 w-60 rounded-xl border-2 border-[var(--color-primary)]/80 shadow-[0_0_0_9999px_rgba(0,0,0,0.5)]"
          >
            <!-- Animated Center Laser Line -->
            <div
              class="absolute inset-x-2 h-0.5 animate-pulse bg-[var(--color-primary)] shadow-[0_0_8px_var(--color-primary)]"
              style="top: 50%;"
            ></div>
          </div>
        </div>
      {/if}

      <!-- Fallback when camera is disabled or errored -->
      {#if cameraError}
        <div
          class="absolute inset-0 flex flex-col items-center justify-center bg-[var(--bg-surface-50)] p-4 text-center"
        >
          <div
            class="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-amber-500"
          >
            <Icon name="videocam_off" size="md" />
          </div>
          <p class="text-xs font-bold text-[var(--text-main)]">Kein Kamerabild verfügbar</p>
          <p class="mt-1 max-w-xs text-[0.6875rem] text-[var(--text-muted)]">
            Der Kamerazugriff wurde im Browser blockiert oder es ist keine Webcam angeschlossen.
          </p>
        </div>
      {/if}
    </div>

    <!-- Manual Barcode Input Fallback -->
    <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4">
      <form
        onsubmit={(e) => {
          e.preventDefault();
          handleManualSubmit();
        }}
        class="space-y-3"
      >
        <div class="text-xs font-bold text-[var(--text-main)]">
          Barcode manuell eingeben oder simulieren
        </div>
        <div class="flex gap-2">
          <div class="flex-1">
            <Input type="text" placeholder="z. B. 4008400404127 (EAN)" bind:value={manualBarcode} />
          </div>
          <Btn variant="primary" size="md" type="submit" disabled={!manualBarcode.trim()}>
            Suchen
          </Btn>
        </div>
      </form>
    </div>

    <!-- Modal Actions -->
    <div class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-3">
      <span class="text-[0.6875rem] text-[var(--text-muted)]">
        Unterstützt EAN-13, EAN-8, UPC-A, UPC-E
      </span>
      <Btn
        variant="secondary"
        size="md"
        onclick={() => {
          stopCamera();
          onclose();
        }}
      >
        Schließen
      </Btn>
    </div>
  </div>
</Modal>
