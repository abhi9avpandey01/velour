"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useLogin } from "@/lib/queries";
import { useAuthStore } from "@/lib/auth-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import Link from "next/link";
import { Loader2 } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const loginMutation = useLogin();
  
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate(
      { username, password },
      {
        onSuccess: (data) => {
          setAuth(data.access_token, data.user);
          toast.success("Logged in successfully!");
          router.push("/dashboard");
        },
        onError: (err: any) => {
          const detail = err.response?.data?.detail;
          if (Array.isArray(detail)) {
            toast.error(detail[0].msg || "Validation error");
          } else {
            toast.error(detail || "Login failed");
          }
        }
      }
    );
  };

  return (
    <div className="flex h-screen w-full items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">Login to Velour</CardTitle>
          <CardDescription>Enter your credentials to access your AI Stylist</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Email</Label>
              <Input 
                id="username" 
                type="text" 
                placeholder="email@example.com"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required 
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input 
                id="password" 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required 
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full" disabled={loginMutation.isPending}>
              {loginMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Sign In
            </Button>
            <div className="text-sm text-center text-zinc-500">
              Don&apos;t have an account?{" "}
              <Link href="/register" className="text-zinc-900 underline dark:text-zinc-50">
                Register
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
