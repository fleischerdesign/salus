import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import Btn from '$components/ui/Btn.svelte';

describe('Btn', () => {
  it('renders as a button element by default', () => {
    const { container } = render(Btn);
    const btn = container.querySelector('button');
    expect(btn).toBeDefined();
  });

  it('renders as an anchor when href is provided', () => {
    const { container } = render(Btn, { href: '/test' });
    const link = container.querySelector('a');
    expect(link).toBeDefined();
    expect(link!.getAttribute('href')).toBe('/test');
  });

  it('fires onclick when clicked', async () => {
    const onclick = vi.fn();
    const { container } = render(Btn, { onclick });
    const btn = container.querySelector('button')!;
    await fireEvent.click(btn);
    expect(onclick).toHaveBeenCalledOnce();
  });

  it('has disabled attribute when disabled', () => {
    const { container } = render(Btn, { disabled: true });
    const btn = container.querySelector('button');
    expect(btn!.disabled).toBe(true);
  });

  it('sets aria-busy when loading', () => {
    const { container } = render(Btn, { loading: true });
    const btn = container.querySelector('button');
    expect(btn!.getAttribute('aria-busy')).toBe('true');
  });

  it('renders with primary variant', () => {
    const { container } = render(Btn, { variant: 'primary' });
    const btn = container.querySelector('button');
    expect(btn!.className).toContain('bg-primary-500');
  });

  it('renders with sm size', () => {
    const { container } = render(Btn, { size: 'sm' });
    const btn = container.querySelector('button');
    expect(btn!.className).toContain('h-8');
  });
});
