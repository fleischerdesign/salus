export function resize(
  node: HTMLElement,
  onResize: (width: number) => void
): { destroy: () => void } {
  const ro = new ResizeObserver((entries) => {
    for (const entry of entries) {
      onResize(entry.contentRect.width);
    }
  });
  ro.observe(node);
  return {
    destroy() {
      ro.disconnect();
    }
  };
}
