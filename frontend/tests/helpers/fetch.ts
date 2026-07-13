import { vi, type Mock } from 'vitest';

interface MockResponse {
  status?: number;
  body?: unknown;
}

function createMockResponse({ status = 200, body }: MockResponse): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
    text: async () => (body ? JSON.stringify(body) : ''),
    headers: new Headers()
  } as Response;
}

export function createFetchMock(responses: MockResponse[]): Mock {
  let index = 0;
  return vi.fn(async (_url?: string, _init?: RequestInit) => {
    const response = responses[Math.min(index++, responses.length - 1)];
    return createMockResponse(response);
  });
}
