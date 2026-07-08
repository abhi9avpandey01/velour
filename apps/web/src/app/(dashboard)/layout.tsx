"use client";

import { useAuthStore } from "@/lib/auth-store";
import { useCurrentUser } from "@/lib/queries";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Shirt, Upload, Home, LogOut, Loader2, MessageSquare, Sun, Moon, User } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { token, logout } = useAuthStore();
  const { data: currentUser } = useCurrentUser();
  const router = useRouter();
  const pathname = usePathname();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const actualToken = useAuthStore.getState().token;
    if (!actualToken) {
      router.push("/login");
    }
  }, [router]);

  if (!mounted || !token) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: Home },
    { name: "Wardrobe", href: "/wardrobe", icon: Shirt },
    { name: "Stylist", href: "/stylist", icon: MessageSquare },
    { name: "Upload", href: "/upload", icon: Upload },
    { name: "Profile", href: "/profile", icon: User },
  ];

  return (
    <div className="flex min-h-screen w-full bg-transparent">
      {/* Sidebar */}
      <aside className="w-64 border-r-2 border-dashed border-zinc-300 bg-white dark:border-zinc-700 dark:bg-zinc-900 hidden md:block">
        <div className="flex h-16 items-center px-6 border-b border-zinc-200 dark:border-zinc-800">
          <h1 className="text-xl font-bold tracking-tight text-zinc-900 dark:text-white">Velour</h1>
        </div>
        <nav className="p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-50"
                    : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/50 dark:hover:text-zinc-50"
                }`}
              >
                <Icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b border-zinc-200 bg-white px-6 dark:border-zinc-800 dark:bg-zinc-900">
          <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-50">
            {currentUser ? `Welcome, ${currentUser.username}` : "Welcome"}
          </h2>
          <div className="flex items-center space-x-4">
            {currentUser?.profile_picture_url ? (
              <img
                src={currentUser.profile_picture_url}
                alt="Profile"
                className="h-8 w-8 rounded-full object-cover border border-zinc-200 dark:border-zinc-800"
              />
            ) : (
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-800">
                <User className="h-4 w-4 text-zinc-600 dark:text-zinc-400" />
              </div>
            )}
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
