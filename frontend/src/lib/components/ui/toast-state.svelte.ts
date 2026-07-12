export interface ToastOptions {
  persistent?: boolean;
  progress?: boolean;
  duration?: number;
}

interface ToastItem {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info' | 'loading' | 'warning';
  progress?: boolean;
  progressValue?: number;
}

const DEFAULT_DURATION = 5000;

let toasts = $state<ToastItem[]>([]);
let nextId = 0;

function dismiss(id: number) {
  toasts = toasts.filter((t) => t.id !== id);
}

function addToast(
  message: string,
  type: 'success' | 'error' | 'info' | 'loading' | 'warning' = 'info',
  options: ToastOptions = {}
): number {
  const id = nextId++;
  toasts = [...toasts, { id, message, type, progress: options.progress ?? false }];

  if (!options.persistent) {
    const duration = options.duration ?? DEFAULT_DURATION;
    setTimeout(() => {
      dismiss(id);
    }, duration);
  }

  return id;
}

export function toast(
  message: string,
  type: 'success' | 'error' | 'info' | 'loading' | 'warning' = 'info',
  options: ToastOptions = {}
): number {
  return addToast(message, type, options);
}

export function dismissToast(id: number): void {
  dismiss(id);
}

export function updateToast(id: number, message: string): void {
  toasts = toasts.map((t) => (t.id === id ? { ...t, message } : t));
}

export function updateToastProgress(id: number, message: string, value: number): void {
  toasts = toasts.map((t) => (t.id === id ? { ...t, message, progressValue: value } : t));
}

export function getToasts(): ToastItem[] {
  return toasts;
}
