"use client";

import { useState, useRef, useEffect } from "react";
import { useCurrentUser, useUpdateProfile, useUploadAvatar, getApiError } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Upload, User, CheckCircle2 } from "lucide-react";

export default function ProfilePage() {
  const { data: user, isLoading } = useCurrentUser();
  const updateProfile = useUpdateProfile();
  const uploadAvatar = useUploadAvatar();
  
  const [username, setUsername] = useState("");
  const [isSaved, setIsSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (user) {
      setUsername(user.username);
    }
  }, [user]);

  if (isLoading || !user) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
      </div>
    );
  }

  const handleSave = async () => {
    try {
      setError(null);
      setIsSaved(false);
      await updateProfile.mutateAsync({ username });
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (err) {
      setError(getApiError(err));
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    try {
      setError(null);
      await uploadAvatar.mutateAsync(file);
    } catch (err) {
      setError(getApiError(err, "Failed to upload avatar"));
    }
    
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">Profile</h1>
      
      {error && (
        <div className="p-4 rounded-md bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Profile Picture</CardTitle>
          <CardDescription>Update your avatar.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col sm:flex-row items-center gap-6">
          <div className="relative h-24 w-24 rounded-full overflow-hidden bg-zinc-100 dark:bg-zinc-800 border-2 border-zinc-200 dark:border-zinc-700 flex items-center justify-center shrink-0">
            {user.profile_picture_url ? (
              <img 
                src={user.profile_picture_url} 
                alt="Profile" 
                className="h-full w-full object-cover"
              />
            ) : (
              <User className="h-10 w-10 text-zinc-400" />
            )}
            {uploadAvatar.isPending && (
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-white" />
              </div>
            )}
          </div>
          
          <div className="flex-1 space-y-2 text-center sm:text-left">
            <input 
              type="file" 
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/jpeg,image/png,image/webp"
              className="hidden" 
            />
            <Button 
              variant="outline" 
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadAvatar.isPending}
            >
              <Upload className="mr-2 h-4 w-4" />
              Upload New Picture
            </Button>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Recommended size: 256x256px. Max 10MB.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
          <CardDescription>Update your username and other details.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input 
              id="username" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Your username"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email address</Label>
            <Input 
              id="email" 
              value={user.email} 
              disabled 
              className="bg-zinc-50 dark:bg-zinc-800"
            />
            <p className="text-xs text-zinc-500 text-muted-foreground">Email cannot be changed.</p>
          </div>
        </CardContent>
        <CardFooter className="flex justify-between border-t border-zinc-100 dark:border-zinc-800 pt-6">
          <div className="text-sm text-green-600 flex items-center">
            {isSaved && (
              <>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Profile updated successfully
              </>
            )}
          </div>
          <Button 
            onClick={handleSave} 
            disabled={updateProfile.isPending || username === user.username}
          >
            {updateProfile.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Save Changes
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
