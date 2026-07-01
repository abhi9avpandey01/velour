"use client";

import { useState, useEffect } from "react";
import { Sparkles } from "lucide-react";

interface StylistResponseProps {
  /** The AI styling advice text to display */
  content: string;
  /** Whether to animate the text appearing */
  animate?: boolean;
  /** Optional className override */
  className?: string;
}

/**
 * Renders AI styling advice in a chatbot message bubble format.
 * Features a Velour AI avatar, animated text reveal, and styled formatting.
 */
export function StylistResponse({ content, animate = true, className = "" }: StylistResponseProps) {
  const [displayedText, setDisplayedText] = useState(animate ? "" : content);
  const [isAnimating, setIsAnimating] = useState(animate);

  useEffect(() => {
    if (!animate) {
      setDisplayedText(content);
      return;
    }

    setDisplayedText("");
    setIsAnimating(true);
    let index = 0;

    const interval = setInterval(() => {
      if (index < content.length) {
        // Reveal in chunks of 3 characters for speed
        const chunkSize = 3;
        const nextIndex = Math.min(index + chunkSize, content.length);
        setDisplayedText(content.slice(0, nextIndex));
        index = nextIndex;
      } else {
        clearInterval(interval);
        setIsAnimating(false);
      }
    }, 12);

    return () => clearInterval(interval);
  }, [content, animate]);

  /**
   * Formats plain text with basic markdown-like bold (**text**) support.
   * Splits into paragraphs on double newlines for readability.
   */
  const formatContent = (text: string) => {
    const paragraphs = text.split(/\n\n+/);
    return paragraphs.map((paragraph, i) => {
      // Process bold markers
      const parts = paragraph.split(/(\*\*[^*]+\*\*)/g);
      const formatted = parts.map((part, j) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={j} className="text-violet-400 font-semibold">
              {part.slice(2, -2)}
            </strong>
          );
        }
        return <span key={j}>{part}</span>;
      });

      return (
        <p key={i} className={i > 0 ? "mt-3" : ""}>
          {formatted}
        </p>
      );
    });
  };

  return (
    <div className={`flex gap-3 items-start ${className}`}>
      {/* Avatar */}
      <div className="shrink-0 flex items-center justify-center w-9 h-9 rounded-full bg-gradient-to-br from-violet-600 to-fuchsia-600 shadow-lg shadow-violet-500/20">
        <Sparkles className="h-4 w-4 text-white" />
      </div>

      {/* Message Bubble */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-xs font-semibold text-violet-400 uppercase tracking-wider">
            Velour Stylist
          </span>
          {isAnimating && (
            <span className="flex gap-0.5">
              <span className="w-1 h-1 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-1 h-1 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-1 h-1 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
            </span>
          )}
        </div>

        <div className="rounded-2xl rounded-tl-sm bg-gradient-to-br from-zinc-800/80 to-zinc-900/80 border border-zinc-700/50 p-4 backdrop-blur-sm">
          <div className="text-sm text-zinc-300 leading-relaxed">
            {formatContent(displayedText)}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * A loading state placeholder for the StylistResponse component.
 */
export function StylistResponseSkeleton() {
  return (
    <div className="flex gap-3 items-start">
      <div className="shrink-0 flex items-center justify-center w-9 h-9 rounded-full bg-gradient-to-br from-violet-600 to-fuchsia-600 shadow-lg shadow-violet-500/20 animate-pulse">
        <Sparkles className="h-4 w-4 text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-xs font-semibold text-violet-400 uppercase tracking-wider">
            Velour Stylist
          </span>
          <span className="flex gap-0.5">
            <span className="w-1 h-1 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
            <span className="w-1 h-1 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
            <span className="w-1 h-1 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
          </span>
        </div>
        <div className="rounded-2xl rounded-tl-sm bg-gradient-to-br from-zinc-800/80 to-zinc-900/80 border border-zinc-700/50 p-4 space-y-3">
          <div className="h-3 w-3/4 bg-zinc-700 rounded animate-pulse" />
          <div className="h-3 w-full bg-zinc-700 rounded animate-pulse" />
          <div className="h-3 w-5/6 bg-zinc-700 rounded animate-pulse" />
          <div className="h-3 w-2/3 bg-zinc-700 rounded animate-pulse" />
        </div>
      </div>
    </div>
  );
}
