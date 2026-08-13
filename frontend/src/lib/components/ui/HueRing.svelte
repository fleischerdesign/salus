<script lang="ts">
  import { pointToHue, hueGradient } from '$lib/theme/hue';

  interface Props {
    value: number;
    onchange?: (hue: number) => void;
    oncommit?: (hue: number) => void;
    size?: number;
  }

  let { value, onchange, oncommit, size = 160 }: Props = $props();

  let ringEl: HTMLDivElement | undefined;
  let dragging = $state(false);

  const thumbStyle = $derived.by(() => {
    const radians = ((value % 360) * Math.PI) / 180;
    const radius = (size - 24) / 2;
    const x = size / 2 + radius * Math.sin(radians);
    const y = size / 2 - radius * Math.cos(radians);
    return `left: ${x}px; top: ${y}px;`;
  });

  function hueFromEvent(event: PointerEvent): number {
    const rect = ringEl!.getBoundingClientRect();
    return pointToHue(
      event.clientX,
      event.clientY,
      rect.left + rect.width / 2,
      rect.top + rect.height / 2
    );
  }

  function onPointerDown(event: PointerEvent) {
    dragging = true;
    ringEl?.setPointerCapture(event.pointerId);
    onchange?.(hueFromEvent(event));
  }

  function onPointerMove(event: PointerEvent) {
    if (!dragging) return;
    onchange?.(hueFromEvent(event));
  }

  function onPointerUp(event: PointerEvent) {
    if (!dragging) return;
    dragging = false;
    oncommit?.(hueFromEvent(event));
  }

  function onKeydown(event: KeyboardEvent) {
    const step = event.shiftKey ? 10 : 1;
    let next = value;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') next = value - step;
    else if (event.key === 'ArrowRight' || event.key === 'ArrowUp') next = value + step;
    else return;
    event.preventDefault();
    next = ((next % 360) + 360) % 360;
    onchange?.(next);
    oncommit?.(next);
  }
</script>

<div
  bind:this={ringEl}
  class="relative cursor-pointer rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
  style="width: {size}px; height: {size}px; background: {hueGradient()}; touch-action: none;"
  role="slider"
  aria-label="Akzentfarbe"
  aria-valuemin="0"
  aria-valuemax="359"
  aria-valuenow={value}
  tabindex="0"
  onpointerdown={onPointerDown}
  onpointermove={onPointerMove}
  onpointerup={onPointerUp}
  onkeydown={onKeydown}
>
  <div
    class="absolute h-6 w-6 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white shadow-md ring-1 ring-black/10"
    style={thumbStyle}
  ></div>
</div>
