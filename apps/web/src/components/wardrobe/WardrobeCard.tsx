import { WardrobeItem } from "@/lib/queries";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Heart } from "lucide-react";

export function WardrobeCard({ item }: { item: WardrobeItem }) {
  return (
    <Card className="overflow-hidden relative group">
      <div className="aspect-[3/4] relative bg-zinc-100 dark:bg-zinc-800">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img 
          src={item.thumbnail_url || item.image_url} 
          alt={item.name || item.category || "Clothing item"} 
          className="object-cover w-full h-full"
        />

        {/* Favorite indicator / toggle */}
        <Button 
          variant="ghost" 
          size="icon" 
          className="absolute top-2 right-2 bg-white/60 backdrop-blur opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white"
        >
          <Heart className={`h-5 w-5 ${item.favorite ? "fill-red-500 text-red-500" : "text-zinc-600"}`} />
        </Button>
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
  );
}
