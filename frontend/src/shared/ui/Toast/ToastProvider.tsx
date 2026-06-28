import { createContext, useCallback, useMemo, useState, type ReactNode } from 'react';
import { Toast, ToastViewport, type ToastVariant } from './Toast';

interface ToastItem {
  id: string;
  message: string;
  variant: ToastVariant;
}

interface ToastContextValue {
  showToast: (message: string, variant?: ToastVariant) => void;
  success: (message: string) => void;
  error: (message: string) => void;
  warning: (message: string) => void;
  info: (message: string) => void;
}

interface ToastProviderProps {
  children: ReactNode;
}

const TOAST_AUTO_CLOSE_MS = 4000;

export const ToastContext = createContext<ToastContextValue | null>(null);

function createToastId() {
  return crypto.randomUUID();
}

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((currentToasts) => currentToasts.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback((message: string, variant: ToastVariant = 'info') => {
    const toast: ToastItem = {
      id: createToastId(),
      message,
      variant,
    };

    setToasts((currentToasts) => [...currentToasts, toast]);
  }, []);

  const value = useMemo<ToastContextValue>(
    () => ({
      showToast,
      success: (message: string) => showToast(message, 'success'),
      error: (message: string) => showToast(message, 'error'),
      warning: (message: string) => showToast(message, 'warning'),
      info: (message: string) => showToast(message, 'info'),
    }),
    [showToast],
  );

  return (
    <ToastContext.Provider value={value}>
      {children}

      <ToastViewport position="top-right">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            variant={toast.variant}
            autoCloseMs={TOAST_AUTO_CLOSE_MS}
            onClose={() => removeToast(toast.id)}
          >
            {toast.message}
          </Toast>
        ))}
      </ToastViewport>
    </ToastContext.Provider>
  );
}
