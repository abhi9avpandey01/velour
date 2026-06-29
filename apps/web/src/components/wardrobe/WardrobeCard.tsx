import { WardrobeItem } from "@/lib/queries";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Heart, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function WardrobeCard({ item }: { item: WardrobeItem }) {
  const isProcessing = item.processing_status === "PENDING" || item.processing_status === "PROCESSING";

  return (
    <Card className="overflow-hidden relative group">
      <div className="aspect-[3/4] relative bg-zinc-100 dark:bg-zinc-800">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img 
          src={item.image_url} 
          alt={item.category || "Clothing item"} 
          className="object-cover w-full h-full"
        />
        
        {isProcessing && (
          <div className="absolute inset-0 bg-black/60 flex flex-col items-center justify-center text-white p-6 text-center backdrop-blur-sm transition-all">
            <Loader2 className="h-8 w-8 animate-spin mb-4" />
            <div className="mb-2 text-sm font-medium">AI Analyzing...</div>
            <p className="text-xs text-zinc-300 mb-4">Extracting metadata</p>
            <Progress value={50} className="w-full h-1" />
          </div>
        )}

        {/* Favorite Button Overlay (Mocked logic for vertical slice) */}
        {!isProcessing && (
          <Button 
            variant="ghost" 
            size="icon" 
            className="absolute top-2 right-2 bg-white/50 backdrop-blur opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white"
          >
            <Heart className="h-5 w-5 text-zinc-900" />
          </Button>
        )}
      </div>

      <CardContent className="p-4 space-y-3">
        {isProcessing ? (
          <div className="space-y-2 animate-pulse">
            <div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-2/3" />
            <div className="h-3 bg-zinc-200 dark:bg-zinc-700 rounded w-1/2" />
          </div>
        ) : (
          <>
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-lg leading-none">{item.category || "Unknown"}</h3>
                <p className="text-sm text-zinc-500 mt-1 capitalize">{item.color || "Unknown Color"}</p>
              </div>
              {item.confidence_score !== undefined && (
                <div className="text-xs font-medium px-2 py-1 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded-full">
                  {(item.confidence_score * 100).toFixed(0)}%
                </div>
              )}
            </div>
            
            <div className="flex flex-wrap gap-2 pt-2">
              <span className="inline-flex items-center rounded-md bg-zinc-100 px-2 py-1 text-xs font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                {item.season || "All Season"}
              </span>
              <span className="inline-flex items-center rounded-md bg-zinc-100 px-2 py-1 text-xs font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                {item.occasion || "Casual"}
              </span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
