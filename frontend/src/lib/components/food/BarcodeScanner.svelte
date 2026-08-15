<script lang="ts">
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import { BrowserMultiFormatOneDReader } from '@zxing/browser';

  interface Props {
    onScan: (barcode: string) => void;
    variant?: 'primary' | 'secondary';
    label?: string;
    controlled?: boolean;
    active?: boolean;
  }

  let {
    onScan,
    variant = 'primary',
    label = 'Scan barcode',
    controlled = false,
    active = $bindable(false)
  }: Props = $props();

  let cameraEl = $state<HTMLVideoElement | null>(null);
  let stopStream = $state<(() => void) | null>(null);
  let error = $state<string | null>(null);
  let frames = $state(0);

  function stop() {
    stopStream?.();
    stopStream = null;
    if (cameraEl) cameraEl.srcObject = null;
  }

  $effect(() => {
    if (!active || !cameraEl) return;
    error = null;
    frames = 0;

    const reader = new BrowserMultiFormatOneDReader();
    let cancelled = false;
    let localFrames = 0;

    reader
      .decodeFromConstraints(
        {
          video: {
            facingMode: 'environment',
            width: { ideal: 1920 },
            height: { ideal: 1080 }
          }
        },
        cameraEl,
        (result, decodeError) => {
          if (cancelled) return;
          localFrames++;
          frames = localFrames;
          if (result && result.getText()) {
            console.log('[scanner] FOUND:', result.getText());
            active = false;
            onScan(result.getText());
          } else if (localFrames % 30 === 0) {
            console.log(
              '[scanner] frame',
              localFrames,
              'error:',
              decodeError?.constructor?.name,
              decodeError?.message
            );
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
      .catch((e) => {
        console.error('[scanner] stream error:', e);
        error = e instanceof Error ? e.message : 'Camera unavailable';
        active = false;
      });

    return () => {
      cancelled = true;
      stop();
    };
  });
</script>

<div class="flex flex-col gap-2">
  {#if !controlled}
    <Btn
      {variant}
      onclick={() => (active = !active)}
      class={active ? 'border-primary-500 text-primary-600' : ''}
    >
      {#if active}
        <Icon name="close" size="sm" />
      {:else}
        <Icon name="camera" size="sm" />
      {/if}
      {active ? 'Stop scanning' : label}
    </Btn>
  {/if}

  {#if active}
    <div class="overflow-hidden rounded-lg border border-primary-300">
      <video bind:this={cameraEl} class="bg-surface-950 max-h-64 w-full" muted playsinline></video>
    </div>
    <p class="text-xs text-surface-400 tabular-nums">Scanning… {frames} frames</p>
  {/if}

  {#if error}
    <p class="text-xs text-error-600">{error}</p>
  {/if}
</div>
