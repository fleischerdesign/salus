import { render } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Card from '$components/ui/Card.svelte';

describe('Card', () => {
  it('renders children via container', () => {
    const { container } = render(Card);
    const el = container.querySelector('.rounded-md');
    expect(el).toBeDefined();
  });

  it('renders title when provided', () => {
    const { container } = render(Card, { title: 'My Title' });
    expect(container.textContent).toContain('My Title');
  });

  it('renders with elevated variant', () => {
    const { container } = render(Card, { variant: 'elevated' });
    const el = container.querySelector('.rounded-md');
    expect(el!.className).toContain('shadow-sm');
  });

  it('renders with flat variant', () => {
    const { container } = render(Card, { variant: 'flat' });
    const el = container.querySelector('.rounded-md');
    expect(el!.className).toContain('bg-surface-100');
  });

  it('renders with hoverable class', () => {
    const { container } = render(Card, { hoverable: true });
    const el = container.querySelector('.rounded-md');
    expect(el!.className).toContain('hover:shadow-md');
  });

  it('hides padding div when padding is false', () => {
    const { container } = render(Card, { padding: false });
    const paddingDiv = container.querySelector('.p-6');
    expect(paddingDiv).toBeNull();
  });
});
