"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useUploadImage, getApiError } from "@/lib/queries";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { UploadCloud, FileImage, X, CheckCircle2, AlertCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export default function UploadPage() {
  const router = useRouter();
  const uploadMutation = useUploadImage();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      setFile(selectedFile);
      
      const objectUrl = URL.createObjectURL(selectedFile);
      setPreview(objectUrl);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [],
      "image/png": [],
      "image/webp": []
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const clearFile = () => {
    setFile(null);
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setPreview(null);
    uploadMutation.reset();
  };

  const handleUpload = () => {
    if (!file) return;
    
    uploadMutation.mutate(file, {
      onSuccess: () => {
        toast.success("Item uploaded successfully! AI is analyzing it now.");
        router.push("/wardrobe");
      },
      onError: (err: any) => {
        toast.error(getApiError(err, "Failed to upload image. Please try again."));
      }
    });
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Upload Clothing</h1>
        <p className="text-zinc-500 dark:text-zinc-400">Add new pieces to your digital wardrobe.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Select Image</CardTitle>
          <CardDescription>Upload a clear photo of your clothing item. Supported formats: JPG, PNG, WEBP (Max 10MB).</CardDescription>
        </CardHeader>
        <CardContent>
          {!file ? (
            <div 
              {...getRootProps()} 
              className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors flex flex-col items-center justify-center min-h-[300px]
                ${isDragActive ? "border-zinc-900 bg-zinc-50 dark:border-zinc-50 dark:bg-zinc-900/50" : "border-zinc-200 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900/20"}
                ${isDragReject ? "border-red-500 bg-red-50 dark:bg-red-950/20" : ""}
              `}
            >
              <input {...getInputProps()} />
              <UploadCloud className={`h-12 w-12 mb-4 ${isDragReject ? "text-red-500" : "text-zinc-400"}`} />
              {isDragReject ? (
                <p className="text-red-500 font-medium">File type not supported</p>
              ) : isDragActive ? (
                <p className="text-zinc-900 dark:text-zinc-50 font-medium">Drop the image here...</p>
              ) : (
                <>
                  <p className="text-zinc-900 dark:text-zinc-50 font-medium mb-1">Drag & drop an image, or click to select</p>
                  <p className="text-sm text-zinc-500">Ensure good lighting for better AI results</p>
                </>
              )}
            </div>
          ) : (
            <div className="border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-hidden bg-zinc-50 dark:bg-zinc-900/20">
              <div className="flex items-center justify-between p-4 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950">
                <div className="flex items-center space-x-3 truncate">
                  <div className="p-2 bg-zinc-100 dark:bg-zinc-800 rounded-lg">
                    <FileImage className="h-5 w-5 text-zinc-500" />
                  </div>
                  <div className="truncate">
                    <p className="text-sm font-medium truncate">{file.name}</p>
                    <p className="text-xs text-zinc-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={clearFile}
                  disabled={uploadMutation.isPending || uploadMutation.isSuccess}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="p-4 flex flex-col items-center justify-center bg-zinc-100/50 dark:bg-zinc-900/50">
                {preview && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img 
                    src={preview} 
                    alt="Preview" 
                    className="max-h-[300px] object-contain rounded-lg shadow-sm"
                  />
                )}
              </div>
              
              {(uploadMutation.isPending || uploadMutation.isSuccess || uploadMutation.isError) && (
                <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 space-y-4">
                  <div className="flex items-center justify-between text-sm font-medium">
                    <span className="flex items-center text-zinc-700 dark:text-zinc-300">
                      {uploadMutation.isPending && (
                        <><UploadCloud className="h-4 w-4 mr-2 animate-bounce" /> Uploading...</>
                      )}
                      {uploadMutation.isSuccess && (
                        <><CheckCircle2 className="h-4 w-4 mr-2 text-green-500" /> Upload Complete!</>
                      )}
                      {uploadMutation.isError && (
                        <><AlertCircle className="h-4 w-4 mr-2 text-red-500" /> Upload Failed</>
                      )}
                    </span>
                    {uploadMutation.isPending && <span>50%</span>}
                    {uploadMutation.isSuccess && <span className="text-green-500">100%</span>}
                  </div>
                  <Progress 
                    value={uploadMutation.isSuccess ? 100 : uploadMutation.isPending ? 50 : 0} 
                    className={`h-2 ${uploadMutation.isError ? "bg-red-200 dark:bg-red-900" : ""}`} 
                  />
                </div>
              )}
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-end space-x-4 border-t border-zinc-100 dark:border-zinc-800/50 p-6">
          <Button 
            variant="outline" 
            onClick={() => router.push("/wardrobe")}
            disabled={uploadMutation.isPending}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleUpload} 
            disabled={!file || uploadMutation.isPending || uploadMutation.isSuccess}
          >
            {uploadMutation.isPending ? "Uploading..." : "Upload & Analyze"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
