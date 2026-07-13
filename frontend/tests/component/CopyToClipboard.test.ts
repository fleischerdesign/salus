import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CopyToClipboard from '$components/ui/CopyToClipboard.svelte';

beforeEach(() => {
  vi.stubGlobal('navigator', {
    clipboard: {
      writeText: vi.fn().mockResolvedValue(undefined),
    },
  });
});

describe('CopyToClipboard', () => {
  it('renders the value text', () => {
    const { container } = render(CopyToClipboard, { value: 'hello-world' });
    expect(container.textContent).toContain('hello-world');
  });

  it('calls clipboard.writeText on button click', async () => {
    const { container } = render(CopyToClipboard, { value: 'abc-123' });
    const btn = container.querySelector('button')!;
    await fireEvent.click(btn);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('abc-123');
  });

  it('shows copied state after click', async () => {
    vi.useFakeTimers();
    const { container } = render(CopyToClipboard, { value: 'test' });
    const btn = container.querySelector('button')!;
    await fireEvent.click(btn);
    expect(btn.getAttribute('aria-label')).toBe('Copied');
    vi.useRealTimers();
  });
});
