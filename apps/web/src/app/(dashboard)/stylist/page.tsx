"use client";

import { useState, useRef, useEffect } from "react";
import { useChatHistory, useSendMessage } from "@/lib/stylist";
import { StylistResponse, StylistResponseSkeleton } from "@/components/wardrobe/StylistResponse";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Sparkles, Loader2, User, MessageSquare } from "lucide-react";

export default function StylistPage() {
  const { data: history, isLoading: historyLoading } = useChatHistory();
  const sendMutation = useSendMessage();
  const [input, setInput] = useState("");
  const [localMessages, setLocalMessages] = useState<
    Array<{ role: "user" | "assistant"; content: string }>
  >([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history, localMessages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = () => {
    const message = input.trim();
    if (!message || sendMutation.isPending) return;

    setInput("");

    // Optimistically add user message
    setLocalMessages((prev) => [...prev, { role: "user", content: message }]);

    sendMutation.mutate(message, {
      onSuccess: (data) => {
        setLocalMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply },
        ]);
      },
      onError: () => {
        setLocalMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "I'm sorry, I had trouble processing that. Could you try again?",
          },
        ]);
      },
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Merge server history + local messages
  const allMessages = [...(history || []), ...localMessages];
  const hasMessages = allMessages.length > 0;

  const quickPrompts = [
    "What should I wear today?",
    "What goes with my blue shirt?",
    "Suggest a casual weekend outfit",
    "Help me dress for a formal dinner",
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-3xl mx-auto">
      {/* Header */}
      <div className="pb-4 border-b border-zinc-800 mb-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-violet-600 to-fuchsia-600 shadow-lg shadow-violet-500/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              AI Stylist
            </h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              Your personal fashion advisor — ask anything about your wardrobe
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-6 pr-2 scrollbar-thin"
      >
        {historyLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-zinc-500" />
          </div>
        ) : !hasMessages ? (
          /* Empty state */
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600/20 to-fuchsia-600/20 border border-violet-500/20 mb-6">
              <MessageSquare className="h-8 w-8 text-violet-400" />
            </div>
            <h2 className="text-lg font-semibold text-zinc-200 mb-2">
              What would you like to wear?
            </h2>
            <p className="text-sm text-zinc-500 max-w-sm mb-6">
              I can help you pick outfits, suggest color pairings, or style any
              item in your wardrobe. Try asking:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-md">
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => {
                    setInput(prompt);
                    inputRef.current?.focus();
                  }}
                  className="text-left px-4 py-3 rounded-xl bg-zinc-800/50 border border-zinc-700/50 hover:border-violet-500/50 hover:bg-zinc-800 text-sm text-zinc-300 transition-all duration-200"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Message list */
          allMessages.map((msg, i) =>
            msg.role === "user" ? (
              <div key={i} className="flex gap-3 items-start justify-end">
                <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-violet-600/90 px-4 py-3 text-sm text-white shadow-lg shadow-violet-500/10">
                  {msg.content}
                </div>
                <div className="shrink-0 flex items-center justify-center w-9 h-9 rounded-full bg-zinc-700">
                  <User className="h-4 w-4 text-zinc-300" />
                </div>
              </div>
            ) : (
              <StylistResponse
                key={i}
                content={msg.content}
                animate={i >= (history?.length || 0)}
              />
            )
          )
        )}

        {/* Typing indicator */}
        {sendMutation.isPending && (
          <StylistResponseSkeleton />
        )}
      </div>

      {/* Input */}
      <div className="mt-4 pt-4 border-t border-zinc-800">
        <div className="flex gap-3">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about styling..."
            className="flex-1 bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-500 focus-visible:ring-violet-500"
            disabled={sendMutation.isPending}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || sendMutation.isPending}
            className="bg-violet-600 hover:bg-violet-500 text-white px-4"
          >
            {sendMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        <p className="text-xs text-zinc-600 mt-2 text-center">
          Velour AI uses your wardrobe data to give personalized recommendations
        </p>
      </div>
    </div>
  );
}
