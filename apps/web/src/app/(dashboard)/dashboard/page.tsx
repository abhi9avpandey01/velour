"use client";

import { useWardrobe, useDeleteItem } from "@/lib/queries";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PlusCircle, Shirt, Heart, Trash2, Loader2, MessageSquare } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

export default function DashboardPage() {
  const { data: items, isLoading, isError } = useWardrobe();
  const deleteMutation = useDeleteItem();

  if (isLoading) {
    return <div className="animate-pulse space-y-4">
      <div className="h-32 bg-zinc-200 dark:bg-zinc-800 rounded-xl" />
      <div className="h-64 bg-zinc-200 dark:bg-zinc-800 rounded-xl" />
    </div>;
  }

  if (isError) {
    return <div className="text-red-500">Failed to load dashboard data.</div>;
  }

  const totalItems = items?.length || 0;
  const recentItems = items?.slice(0, 4) || [];
  const favoriteItems = items?.filter(i => i.favorite)?.length || 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
          <p className="text-zinc-500 dark:text-zinc-400">Manage your wardrobe and styling preferences.</p>
        </div>
        <Link href="/upload">
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            Add Clothing
          </Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Items</CardTitle>
            <Shirt className="h-4 w-4 text-zinc-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalItems}</div>
            <p className="text-xs text-zinc-500">Pieces in your digital wardrobe</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Favorites</CardTitle>
            <Heart className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{favoriteItems}</div>
            <p className="text-xs text-zinc-500">Items marked as favorite</p>
          </CardContent>
        </Card>

        <Link href="/stylist" className="block">
          <Card className="border-violet-500/30 bg-gradient-to-br from-violet-950/40 to-fuchsia-950/20 hover:border-violet-500/50 transition-colors cursor-pointer h-full">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-violet-300">AI Stylist</CardTitle>
              <MessageSquare className="h-4 w-4 text-violet-400" />
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold text-violet-200">Chat Now</div>
              <p className="text-xs text-violet-400/80">Ask what to wear today</p>
            </CardContent>
          </Card>
        </Link>
      </div>

      <h2 className="text-xl font-bold mt-8 mb-4">Recently Added</h2>
      {recentItems.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Shirt className="h-12 w-12 text-zinc-300 dark:text-zinc-700 mb-4" />
            <h3 className="text-lg font-medium">Your wardrobe is empty</h3>
            <p className="text-sm text-zinc-500 mb-4">Upload your first item to get started.</p>
            <Link href="/upload">
              <Button variant="outline">Upload Image</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {recentItems.map((item) => (
            <Card key={item.id} className="overflow-hidden group">
              <div className="aspect-square relative bg-zinc-100 dark:bg-zinc-800">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img 
                  src={item.thumbnail_url || item.image_url} 
                  alt={item.name || item.category || "Clothing item"} 
                  className="object-cover w-full h-full"
                />
                
                {/* Action buttons overlay */}
                <div className="absolute top-2 left-2 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
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

                {item.favorite && (
                  <div className="absolute top-2 right-2 p-1 bg-white/80 rounded-full">
                    <Heart className="h-3 w-3 fill-red-500 text-red-500" />
                  </div>
                )}
              </div>
              <CardContent className="p-4">
                <div className="font-medium truncate">{item.name || item.category || "Unknown"}</div>
                <div className="text-sm text-zinc-500 truncate capitalize">{item.color || "Unknown color"}</div>
                {item.brand && <div className="text-xs text-zinc-400 truncate">{item.brand}</div>}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
