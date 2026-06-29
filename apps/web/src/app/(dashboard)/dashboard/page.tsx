"use client";

import { useWardrobe } from "@/lib/queries";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PlusCircle, Shirt } from "lucide-react";
import Link from "next/link";
import { Progress } from "@/components/ui/progress";

export default function DashboardPage() {
  const { data: items, isLoading, isError } = useWardrobe();

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
  const processingItems = items?.filter(i => i.processing_status === "PENDING" || i.processing_status === "PROCESSING")?.length || 0;

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
            <CardTitle className="text-sm font-medium">Processing</CardTitle>
            <div className="h-4 w-4 rounded-full bg-blue-500 animate-pulse" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{processingItems}</div>
            <p className="text-xs text-zinc-500">Items being analyzed by AI</p>
          </CardContent>
        </Card>
      </div>

      <h2 className="text-xl font-bold mt-8 mb-4">Recently Uploaded</h2>
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
            <Card key={item.id} className="overflow-hidden">
              <div className="aspect-square relative bg-zinc-100 dark:bg-zinc-800">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img 
                  src={item.image_url} 
                  alt={item.category || "Clothing item"} 
                  className="object-cover w-full h-full"
                />
                {(item.processing_status === "PENDING" || item.processing_status === "PROCESSING") && (
                  <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center text-white p-4">
                    <div className="mb-2 text-sm font-medium">AI Analyzing...</div>
                    <Progress value={50} className="w-full" />
                  </div>
                )}
              </div>
              <CardContent className="p-4">
                <div className="font-medium truncate">{item.category || "Unknown"}</div>
                <div className="text-sm text-zinc-500 truncate">{item.color || "Unknown color"}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
