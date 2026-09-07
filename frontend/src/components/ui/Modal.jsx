import { useEffect, useRef } from "react"
import { createPortal } from "react-dom"

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  onConfirm,
  confirmText = "Confirmar",
  confirmVariant = "primary",
}) {
  const dialogRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden"
      dialogRef.current?.querySelector("button")?.focus()
    } else {
      document.body.style.overflow = ""
    }
    return () => {
      document.body.style.overflow = ""
    }
  }, [isOpen])

  const handleConfirm = async () => {
    if (onConfirm) await onConfirm()
    onClose()
  }

  if (!isOpen) return null

  return createPortal(
    <div className="fixed inset-0 z-[90] flex items-center justify-center p-4" onClick={onClose}>
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        aria-hidden="true"
        style={{ animation: "fadeIn 0.2s ease-out" }}
      />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className="relative bg-neutral-900/95 border border-white/[0.08] rounded-2xl p-6 max-w-lg w-full shadow-2xl"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={(e) => {
          if (e.key === "Escape") onClose()
        }}
        style={{ animation: "fadeInUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)" }}
      >
        {title && (
          <h3
            id="modal-title"
            className="text-lg font-bold text-white mb-4 flex items-center gap-2"
          >
            <span className="w-2 h-2 rounded-full bg-green-500" />
            {title}
          </h3>
        )}
        <div className="text-sm text-neutral-300 leading-relaxed">{children}</div>
        <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-white/[0.06]">
          <button onClick={onClose} className="btn btn-ghost text-xs">
            Cancelar
          </button>
          {onConfirm && (
            <button
              onClick={handleConfirm}
              className={`btn ${confirmVariant === "primary" ? "btn-primary" : "btn-ghost"} text-xs`}
            >
              {confirmText}
            </button>
          )}
        </div>
      </div>
    </div>,
    document.body
  )
}
