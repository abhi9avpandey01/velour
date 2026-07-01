"use client";

import { useEffect, useRef } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ModalProps {
  /** Whether the modal is open */
  open: boolean;
  /** Callback when modal is closed */
  onClose: () => void;
  /** Modal title */
  title?: string;
  /** Modal content */
  children: React.ReactNode;
}

/**
 * A lightweight modal dialog component.
 * Uses a backdrop overlay with glassmorphism and smooth transitions.
 */
export function Modal({ open, onClose, title, children }: ModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (open) {
      document.addEventListener("keydown", handleEsc);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEsc);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose();
      }}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      {/* Modal Content */}
      <div className="relative w-full max-w-lg max-h-[85vh] overflow-y-auto rounded-2xl bg-zinc-900 border border-zinc-700/50 shadow-2xl shadow-violet-500/10 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between p-5 pb-0">
            <h3 className="text-lg font-semibold text-zinc-100">{title}</h3>
            <Button
              variant="ghost"
              size="icon"
              className="text-zinc-400 hover:text-zinc-100 h-8 w-8"
              onClick={onClose}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}

        {/* Body */}
        <div className="p-5">
          {children}
        </div>

        {/* Close button if no title */}
        {!title && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-3 right-3 text-zinc-400 hover:text-zinc-100 h-8 w-8"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
