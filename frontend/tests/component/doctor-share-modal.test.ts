import { render } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import DoctorShareModal from '$components/labs/DoctorShareModal.svelte';

describe('DoctorShareModal', () => {
  it('uses natural German copy without cryptographic jargon overload', async () => {
    const { container } = render(DoctorShareModal, {
      open: true,
      onclose: () => {}
    });
    const text = container.textContent ?? '';

    expect(text).toContain('Arzt-Freigabe');
    expect(text).toContain('Sicherer, zeitlich begrenzter Zugang');

    expect(text).not.toContain('Zero-Knowledge');
    expect(text).not.toContain('Kryptografisch');
    expect(text).not.toContain('kryptografisch');
    expect(text).not.toContain('Ende-zu-Ende Arzt-Freigabe');
    expect(text).not.toMatch(/ECDH|E2EE|Pseudo./i);
  });
});