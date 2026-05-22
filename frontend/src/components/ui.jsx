import { useState, useEffect, useCallback, useRef, createContext, useContext } from 'react';
import { createPortal } from 'react-dom';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev, { id, message, type, duration, exiting: false }]);
    setTimeout(() => {
      setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t));
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 300);
    }, duration);
  }, []);

  const toast = {
    success: (msg) => addToast(msg, 'success'),
    error: (msg) => addToast(msg, 'error'),
    warning: (msg) => addToast(msg, 'warning'),
    info: (msg) => addToast(msg, 'info'),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <ToastContainer toasts={toasts} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}

function ToastContainer({ toasts }) {
  if (toasts.length === 0) return null;

  const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
  const colors = {
    success: 'border-green-500/30 bg-green-500/10',
    error: 'border-red-500/30 bg-red-500/10',
    warning: 'border-yellow-500/30 bg-yellow-500/10',
    info: 'border-blue-500/30 bg-blue-500/10',
  };
  const iconColors = {
    success: 'text-green-400 bg-green-500/20',
    error: 'text-red-400 bg-red-500/20',
    warning: 'text-yellow-400 bg-yellow-500/20',
    info: 'text-blue-400 bg-blue-500/20',
  };

  return (
    <div className="fixed top-6 right-6 z-[100] flex flex-col gap-3 max-w-sm">
      {toasts.map(t => (
        <div
          key={t.id}
          className={`${t.exiting ? 'toast-exit' : 'toast'} flex items-start gap-3 px-4 py-3 rounded-xl border backdrop-blur-xl ${colors[t.type]}`}
        >
          <span className={`w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${iconColors[t.type]}`}>
            {icons[t.type]}
          </span>
          <p className="text-sm text-neutral-200 leading-relaxed">{t.message}</p>
        </div>
      ))}
    </div>
  );
}

export function Modal({ isOpen, onClose, title, children, onConfirm, confirmText = 'Confirmar', confirmVariant = 'primary' }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      dialogRef.current?.querySelector('button')?.focus();
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  const handleConfirm = async () => {
    if (onConfirm) await onConfirm();
    onClose();
  };

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-[90] flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" aria-hidden="true" style={{ animation: 'fadeIn 0.2s ease-out' }} />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className="relative bg-neutral-900/95 border border-white/[0.08] rounded-2xl p-6 max-w-lg w-full shadow-2xl"
        onClick={e => e.stopPropagation()}
        onKeyDown={e => { if (e.key === 'Escape') onClose(); }}
        style={{ animation: 'fadeInUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)' }}
      >
        {title && (
          <h3 id="modal-title" className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            {title}
          </h3>
        )}
        <div className="text-sm text-neutral-300 leading-relaxed">
          {children}
        </div>
        <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-white/[0.06]">
          <button onClick={onClose} className="btn btn-ghost text-xs">
            Cancelar
          </button>
          {onConfirm && (
            <button onClick={handleConfirm} className={`btn ${confirmVariant === 'primary' ? 'btn-primary' : 'btn-ghost'} text-xs`}>
              {confirmText}
            </button>
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}

export function Spinner({ size = 'sm', className = '' }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' };
  return (
    <div className={`${sizes[size]} border-2 border-neutral-700 border-t-green-500 rounded-full animate-spin ${className}`} />
  );
}

export { default as AiModeToggle } from './AiModeToggle';
