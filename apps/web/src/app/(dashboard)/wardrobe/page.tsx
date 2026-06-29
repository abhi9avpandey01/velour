"use client";

import { useWardrobe } from "@/lib/queries";
import { WardrobeCard } from "@/components/wardrobe/WardrobeCard";
import { Button } from "@/components/ui/button";
import { PlusCircle, Loader2 } from "lucide-react";
import Link from "next/link";

export default function WardrobePage() {
  const { data: items, isLoading, isError } = useWardrobe();

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Your Wardrobe</h1>
          <p className="text-zinc-500 dark:text-zinc-400">All your clothing items, analyzed by AI.</p>
        </div>
        <Link href="/upload">
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            Add Item
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="flex flex-1 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
        </div>
      ) : isError ? (
        <div className="flex flex-1 items-center justify-center text-red-500">
          Failed to load wardrobe.
        </div>
      ) : items?.length === 0 ? (
        <div className="flex flex-1 flex-col items-center justify-center text-center border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl p-8">
          <h3 className="text-lg font-medium">Your wardrobe is empty</h3>
          <p className="text-sm text-zinc-500 mt-2 mb-4">Start building your digital closet by uploading some photos.</p>
          <Link href="/upload">
            <Button>Upload Photos</Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 pb-10">
          {items?.map((item) => (
            <WardrobeCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
