import { render } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import E2EEShareCard from '$components/labs/E2EEShareCard.svelte';

describe('E2EEShareCard', () => {
  it('uses plain-language share copy without crypto jargon', async () => {
    const { container } = render(E2EEShareCard);
    const text = container.textContent ?? '';

    expect(text).toContain('Sichere Arztfreigabe');
    expect(text).toContain('Ende-zu-Ende verschlüsselter Zugangslink');
    expect(text).toContain('Arzt-Freigabelink erstellen');

    expect(text).not.toMatch(/ECDH|E2EE|AES-256|Zero-Knowledge/i);
    expect(text).not.toContain('Kryptographisch');
    expect(text).not.toContain('kryptographisch');
    expect(text).not.toContain('Schlüsselpaar');
    expect(text).not.toContain('Einmallink');
  });
});