import { render } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Input from '$components/ui/Input.svelte';

describe('Input component', () => {
  it('renders input without icon and has standard padding', () => {
    const { container } = render(Input, { placeholder: 'Enter text' });
    const input = container.querySelector('input');
    expect(input).toBeDefined();
    expect(input?.placeholder).toBe('Enter text');
    expect(input?.className).not.toContain('pl-10');
    expect(container.querySelector('svg, .icon, [data-icon]')).toBeNull();
  });

  it('renders input with icon positioned absolutely and input with pl-10', () => {
    const { container } = render(Input, { icon: 'search', placeholder: 'Search...' });
    const input = container.querySelector('input');
    expect(input).toBeDefined();
    expect(input?.className).toContain('pl-10');

    const iconWrapper = container.querySelector('.pointer-events-none.absolute.left-3\\.5');
    expect(iconWrapper).not.toBeNull();
    expect(iconWrapper?.className).toContain('absolute');
    expect(iconWrapper?.className).toContain('left-3.5');
    expect(iconWrapper?.className).toContain('top-1/2');
    expect(iconWrapper?.className).toContain('-translate-y-1/2');
  });

  it('renders input with label and unit', () => {
    const { container } = render(Input, { label: 'Weight', unit: 'kg', value: '75' });
    expect(container.textContent).toContain('Weight');
    expect(container.textContent).toContain('kg');
    const input = container.querySelector('input');
    expect(input?.value).toBe('75');
  });

  it('renders error state when error is provided', () => {
    const { container } = render(Input, { error: 'Invalid value' });
    const alert = container.querySelector('[role="alert"]');
    expect(alert).not.toBeNull();
    expect(alert?.textContent).toContain('Invalid value');
    const input = container.querySelector('input');
    expect(input?.className).toContain('border-rose-500');
  });
});
