import { render, screen } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Spinner from '$components/ui/Spinner.svelte';

describe('Spinner', () => {
  it('renders with status role and loading label', () => {
    render(Spinner);
    const el = screen.getByRole('status');
    expect(el).toBeDefined();
    expect(el.getAttribute('aria-label')).toBe('Loading');
  });

  it('renders with sm size', () => {
    const { container } = render(Spinner, { size: 'sm' });
    const el = container.firstElementChild;
    expect(el).toBeDefined();
  });

  it('renders with lg size', () => {
    const { container } = render(Spinner, { size: 'lg' });
    const el = container.firstElementChild;
    expect(el).toBeDefined();
  });
});
