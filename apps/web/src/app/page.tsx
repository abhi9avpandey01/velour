"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/auth-store";

export default function Home() {
  const { token } = useAuthStore();

  return (
    <main className="flex flex-1 h-screen flex-col items-center justify-center px-6">
      <div className="flex flex-col items-center gap-6 text-center">
        {/* Brand */}
        <h1 className="text-6xl font-bold tracking-tight sm:text-8xl bg-gradient-to-r from-zinc-500 to-zinc-900 bg-clip-text text-transparent dark:from-zinc-400 dark:to-zinc-100">
          Velour
        </h1>

        {/* Tagline */}
        <p className="text-xl font-medium text-zinc-500 dark:text-zinc-400 sm:text-2xl">
          AI Personal Stylist
        </p>

        {/* Subtle divider */}
        <div className="mt-4 h-px w-24 bg-gradient-to-r from-transparent via-zinc-300 dark:via-zinc-700 to-transparent" />

        {/* Call to action */}
        <div className="mt-6 flex flex-col sm:flex-row gap-4">
          <Link href={token ? "/dashboard" : "/login"}>
            <Button size="lg" className="rounded-full px-8">
              {token ? "Go to Dashboard" : "Get Started"}
            </Button>
          </Link>
        </div>
      </div>
    </main>
  );
}
