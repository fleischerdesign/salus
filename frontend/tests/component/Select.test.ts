import { render } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Select from '$components/ui/Select.svelte';

describe('Select component', () => {
  const options = [
    { value: 'opt1', label: 'Option 1' },
    { value: 'opt2', label: 'Option 2' }
  ];

  it('renders select without icon and has standard pl-3.5 padding', () => {
    const { container } = render(Select, { options, value: 'opt1' });
    const select = container.querySelector('select');
    expect(select).toBeDefined();
    expect(select?.className).toContain('pl-3.5');
    expect(select?.className).not.toContain('pl-10');
  });

  it('renders select with icon positioned absolutely and select with pl-10', () => {
    const { container } = render(Select, { options, icon: 'category', value: 'opt1' });
    const select = container.querySelector('select');
    expect(select).toBeDefined();
    expect(select?.className).toContain('pl-10');
    expect(select?.className).not.toContain('pl-3.5');

    const iconWrapper = container.querySelector('.pointer-events-none.absolute.left-3\\.5');
    expect(iconWrapper).not.toBeNull();
    expect(iconWrapper?.className).toContain('absolute');
    expect(iconWrapper?.className).toContain('left-3.5');
    expect(iconWrapper?.className).toContain('top-1/2');
    expect(iconWrapper?.className).toContain('-translate-y-1/2');
  });
});
