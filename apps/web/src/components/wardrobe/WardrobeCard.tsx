"use client";

import { useState } from "react";
import { WardrobeItem, useAnalyzeImage, useDeleteItem } from "@/lib/queries";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { StylistResponse, StylistResponseSkeleton } from "@/components/wardrobe/StylistResponse";
import { Heart, Sparkles, Loader2, Trash2 } from "lucide-react";
import { toast } from "sonner";

export function WardrobeCard({ item }: { item: WardrobeItem }) {
  const analyzeMutation = useAnalyzeImage();
  const deleteMutation = useDeleteItem();
  const [modalOpen, setModalOpen] = useState(false);
  const [stylingAdvice, setStylingAdvice] = useState<string | null>(null);

  const handleAnalyze = () => {
    setModalOpen(true);
    setStylingAdvice(null);
    
    analyzeMutation.mutate(item.id, {
      onSuccess: (data) => {
        const suggestions = data.attributes?.outfit_suggestions;
        const caption = data.attributes?.caption;
        setStylingAdvice(
          suggestions || caption || "This is a great piece! Try pairing it with complementary colors and accessories."
        );
      },
      onError: () => {
        setStylingAdvice(null);
        setModalOpen(false);
        toast.error("AI analysis failed.");
      }
    });
  };

  return (
    <>
      <Card className="overflow-hidden relative group">
        <div className="aspect-[3/4] relative bg-zinc-100 dark:bg-zinc-800">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img 
            src={item.thumbnail_url || item.image_url} 
            alt={item.name || item.category || "Clothing item"} 
            className="object-cover w-full h-full"
          />

          {/* Action buttons overlay */}
          <div className="absolute top-2 right-2 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button 
              variant="ghost" 
              size="icon" 
              className="bg-white/60 backdrop-blur hover:bg-white shadow-sm"
            >
              <Heart className={`h-5 w-5 ${item.favorite ? "fill-red-500 text-red-500" : "text-zinc-600"}`} />
            </Button>

            <Button
              variant="ghost"
              size="icon"
              className="bg-white/60 backdrop-blur hover:bg-white shadow-sm text-indigo-600"
              onClick={(e) => {
                e.preventDefault();
                handleAnalyze();
              }}
              disabled={analyzeMutation.isPending}
              title="Get Styling Advice"
            >
              {analyzeMutation.isPending ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Sparkles className="h-5 w-5" />
              )}
            </Button>

            <Button
              variant="ghost"
              size="icon"
              className="bg-white/60 backdrop-blur hover:bg-white hover:text-red-600 shadow-sm text-zinc-600"
              onClick={(e) => {
                e.preventDefault();
                if (window.confirm("Are you sure you want to delete this item?")) {
                  deleteMutation.mutate(item.id, {
                    onSuccess: () => toast.success("Item deleted successfully."),
                    onError: () => toast.error("Failed to delete item.")
                  });
                }
              }}
              disabled={deleteMutation.isPending}
              title="Delete Item"
            >
              {deleteMutation.isPending ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Trash2 className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>

        <CardContent className="p-4 space-y-2">
          <div className="flex justify-between items-start">
            <div className="min-w-0 flex-1">
              <h3 className="font-semibold text-base leading-tight truncate">{item.name || "Unknown"}</h3>
              <p className="text-sm text-zinc-500 mt-0.5 capitalize truncate">{item.color || "Unknown Color"}</p>
            </div>
            {item.wears_count > 0 && (
              <div className="text-xs font-medium px-2 py-1 bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300 rounded-full ml-2 shrink-0">
                {item.wears_count}×
              </div>
            )}
          </div>
          
          <div className="flex flex-wrap gap-1.5 pt-1">
            <span className="inline-flex items-center rounded-md bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
              {item.category}
            </span>
            <span className="inline-flex items-center rounded-md bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
              {item.season}
            </span>
            <span className="inline-flex items-center rounded-md bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
              {item.occasion}
            </span>
          </div>

          {item.brand && (
            <p className="text-xs text-zinc-400 truncate">{item.brand}</p>
          )}
        </CardContent>
      </Card>

      {/* Styling Advice Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={`Styling: ${item.name || item.category || "Your Item"}`}
      >
        <div className="space-y-4">
          {/* Item thumbnail */}
          <div className="flex items-center gap-4 p-3 rounded-xl bg-zinc-800/50 border border-zinc-700/50">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={item.thumbnail_url || item.image_url}
              alt={item.name || "Item"}
              className="w-16 h-16 rounded-lg object-cover"
            />
            <div className="min-w-0">
              <p className="font-medium text-zinc-100 truncate">{item.name || item.category || "Clothing Item"}</p>
              <p className="text-sm text-zinc-400 capitalize">{item.color} · {item.category}</p>
            </div>
          </div>

          {/* Stylist Response */}
          {stylingAdvice ? (
            <StylistResponse content={stylingAdvice} animate={true} />
          ) : (
            <StylistResponseSkeleton />
          )}
        </div>
      </Modal>
    </>
  );
}
