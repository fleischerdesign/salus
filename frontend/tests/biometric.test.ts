import { describe, it, expect } from 'vitest';
import { BrowserBiometricProvider } from '$lib/native/providers/browser-biometric';

describe('BrowserBiometricProvider', () => {
  it('reports biometrics unavailable on web', async () => {
    const provider = new BrowserBiometricProvider();
    expect(await provider.isAvailable()).toBe(false);
  });

  it('never verifies identity on web', async () => {
    const provider = new BrowserBiometricProvider();
    expect(await provider.verifyIdentity('unlock')).toBe(false);
  });
});
