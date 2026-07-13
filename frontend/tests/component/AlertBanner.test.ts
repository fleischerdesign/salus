import { render } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import AlertBanner from '$components/ui/AlertBanner.svelte';

describe('AlertBanner', () => {
  it('renders with message prop', () => {
    const { container } = render(AlertBanner, { message: 'Something went wrong' });
    const alert = container.querySelector('[role="alert"]');
    expect(alert).toBeDefined();
    expect(container.textContent).toContain('Something went wrong');
  });

  it('renders with warning variant', () => {
    const { container } = render(AlertBanner, { variant: 'warning', message: 'Warning' });
    const alert = container.querySelector('[role="alert"]');
    expect(alert!.className).toContain('bg-warning-50');
  });

  it('renders with success variant', () => {
    const { container } = render(AlertBanner, { variant: 'success', message: 'Success' });
    const alert = container.querySelector('[role="alert"]');
    expect(alert!.className).toContain('bg-success-50');
  });

  it('renders with error variant (default)', () => {
    const { container } = render(AlertBanner, { message: 'Error' });
    const alert = container.querySelector('[role="alert"]');
    expect(alert!.className).toContain('bg-error-50');
  });
});
