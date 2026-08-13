import { describe, it, expect, vi } from 'vitest';
import { BrowserNetworkProvider } from '$lib/native/providers/browser-network';

describe('BrowserNetworkProvider', () => {
  it('reports navigator.onLine', async () => {
    vi.stubGlobal('navigator', { onLine: true });
    const provider = new BrowserNetworkProvider();
    expect(await provider.isOnline()).toBe(true);

    vi.stubGlobal('navigator', { onLine: false });
    expect(await provider.isOnline()).toBe(false);
  });

  it('registers and unregisters window listeners', () => {
    const addSpy = vi.fn();
    const removeSpy = vi.fn();
    vi.stubGlobal('window', { addEventListener: addSpy, removeEventListener: removeSpy });

    const provider = new BrowserNetworkProvider();
    const unsubscribe = provider.onChange(() => {});

    expect(addSpy).toHaveBeenCalledWith('online', expect.any(Function));
    expect(addSpy).toHaveBeenCalledWith('offline', expect.any(Function));

    unsubscribe();

    expect(removeSpy).toHaveBeenCalledWith('online', expect.any(Function));
    expect(removeSpy).toHaveBeenCalledWith('offline', expect.any(Function));

    vi.unstubAllGlobals();
  });
});
