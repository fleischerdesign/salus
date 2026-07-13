import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

let onSyncCalls: number;
let mockEventSource: MockEventSource | null;
let globalEventSourceListeners: Record<string, EventListener[]> = {};

class MockEventSource {
  url: string;
  listeners: Record<string, EventListener[]> = {};
  readyState: number = 0;
  onerror: ((ev: Event) => void) | null = null;
  onopen: ((ev: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    mockEventSource = this;
  }

  addEventListener(type: string, listener: EventListener) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(listener);
  }

  dispatchEvent(type: string) {
    for (const fn of this.listeners[type] || []) {
      fn(new Event(type));
    }
  }

  close() {
    this.readyState = 2;
  }
}

function setup() {
  vi.stubGlobal('EventSource', MockEventSource);
  vi.stubGlobal(
    'localStorage',
    (() => {
      let store: Record<string, string> = {};
      return {
        getItem: (key: string) => store[key] ?? null,
        setItem: (key: string, value: string) => {
          store[key] = value;
        },
        removeItem: (key: string) => {
          delete store[key];
        }
      };
    })()
  );
  onSyncCalls = 0;
  mockEventSource = null;
}

function teardown() {
  vi.unstubAllGlobals();
}

describe('connectLiveSync', () => {
  beforeEach(() => setup());
  afterEach(async () => {
    const mod = await import('$lib/db/live-events');
    mod.disconnectLiveSync();
    teardown();
  });

  it('creates EventSource with sync events URL', async () => {
    localStorage.setItem('salus_token', 'test-token');
    const mod = await import('$lib/db/live-events');
    mod.connectLiveSync(() => {
      onSyncCalls++;
    });
    expect(mockEventSource).not.toBeNull();
    expect(mockEventSource!.url).toBe('/api/v1/sync/events');
  });

  it('does not connect without token', async () => {
    localStorage.removeItem('salus_token');
    const mod = await import('$lib/db/live-events');
    mod.connectLiveSync(() => {
      onSyncCalls++;
    });
    expect(mockEventSource).toBeNull();
  });

  it('calls onSync after debounce on sync event', async () => {
    vi.useFakeTimers();
    localStorage.setItem('salus_token', 'test-token');
    const mod = await import('$lib/db/live-events');
    mod.connectLiveSync(() => {
      onSyncCalls++;
    });

    mockEventSource!.dispatchEvent('sync');
    mockEventSource!.dispatchEvent('sync');
    mockEventSource!.dispatchEvent('sync');

    vi.advanceTimersByTime(1999);
    expect(onSyncCalls).toBe(0);

    vi.advanceTimersByTime(1);
    expect(onSyncCalls).toBe(1);

    vi.useRealTimers();
  });

  it('disconnect prevents callback and closes EventSource', async () => {
    vi.useFakeTimers();
    localStorage.setItem('salus_token', 'test-token');
    const mod = await import('$lib/db/live-events');
    mod.connectLiveSync(() => {
      onSyncCalls++;
    });

    const es = mockEventSource!;
    expect(es.readyState).toBe(0);

    mod.disconnectLiveSync();
    expect(es.readyState).toBe(2);
    expect(onSyncCalls).toBe(0);

    vi.useRealTimers();
  });
});
