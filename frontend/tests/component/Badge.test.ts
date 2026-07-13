import { render } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Badge from '$components/ui/Badge.svelte';

describe('Badge', () => {
  it('renders and has accessible variant classes', () => {
    const { container } = render(Badge, { variant: 'primary' });
    const span = container.querySelector('span');
    expect(span).toBeDefined();
    expect(span!.className).toContain('bg-primary-50');
  });

  it('renders with default variant', () => {
    const { container } = render(Badge);
    const span = container.querySelector('span');
    expect(span!.className).toContain('bg-surface-100');
  });

  it('renders with success variant', () => {
    const { container } = render(Badge, { variant: 'success' });
    const span = container.querySelector('span');
    expect(span!.className).toContain('bg-success-100');
  });

  it('renders with warning variant', () => {
    const { container } = render(Badge, { variant: 'warning' });
    const span = container.querySelector('span');
    expect(span!.className).toContain('bg-warning-100');
  });

  it('renders with error variant', () => {
    const { container } = render(Badge, { variant: 'error' });
    const span = container.querySelector('span');
    expect(span!.className).toContain('bg-error-100');
  });
});
