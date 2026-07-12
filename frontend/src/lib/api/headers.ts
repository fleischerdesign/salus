let _locale = 'en';

if (typeof localStorage !== 'undefined') {
  try {
    const raw = localStorage.getItem('salus_user');
    if (raw) {
      const user = JSON.parse(raw);
      if (user?.locale) _locale = user.locale;
    }
  } catch {
    /* ignore */
  }
}

export function setLocaleState(locale: string): void {
  _locale = locale;
}

export function getLocale(): string {
  return _locale;
}

export function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Accept-Language': _locale,
    'X-Salus-Sync-Version': '1'
  };
  const token = localStorage.getItem('salus_token');
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}
