"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useUploadImage, useAnalyzeImage, useDeleteItem, getApiError } from "@/lib/queries";
import type { AnalysisResult } from "@/lib/queries";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { StylistResponse, StylistResponseSkeleton } from "@/components/wardrobe/StylistResponse";
import {
  UploadCloud,
  FileImage,
  X,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Loader2,
  Palette,
  Shirt,
  Layers,
  Gem,
  ArrowRight,
  RotateCcw,
  Trash2,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

type FlowStep = "select" | "uploaded" | "analyzing" | "results";

export default function UploadPage() {
  const router = useRouter();
  const uploadMutation = useUploadImage();
  const analyzeMutation = useAnalyzeImage();
  const deleteMutation = useDeleteItem();

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [itemId, setItemId] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [step, setStep] = useState<FlowStep>("select");

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
      "image/webp": [],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    disabled: step !== "select",
  });

  const clearFile = () => {
    setFile(null);
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setPreview(null);
    setItemId(null);
    setAnalysisResult(null);
    setStep("select");
    uploadMutation.reset();
    analyzeMutation.reset();
  };

  const handleDelete = () => {
    if (itemId) {
      deleteMutation.mutate(itemId, {
        onSuccess: () => {
          toast.success("Image deleted successfully.");
          clearFile();
        },
        onError: (err: any) => {
          toast.error(getApiError(err, "Failed to delete image."));
        }
      });
    } else {
      clearFile();
    }
  };

  const handleUpload = () => {
    if (!file) return;

    uploadMutation.mutate(file, {
      onSuccess: (data) => {
        setItemId(data.item_id);
        setStep("uploaded");
        toast.success("Image uploaded successfully!");
      },
      onError: (err: any) => {
        toast.error(getApiError(err, "Failed to upload image. Please try again."));
      },
    });
  };

  const handleAnalyze = () => {
    if (!itemId) return;

    setStep("analyzing");
    analyzeMutation.mutate(itemId, {
      onSuccess: (data) => {
        setAnalysisResult(data);
        setStep("results");
        toast.success("AI analysis complete!");
      },
      onError: (err: any) => {
        setStep("uploaded");
        toast.error(getApiError(err, "AI analysis failed. Please try again."));
      },
    });
  };

  // Step indicator data
  const steps = [
    { key: "upload", label: "Upload", done: step === "uploaded" || step === "analyzing" || step === "results" },
    { key: "analyze", label: "Analyze", done: step === "results" },
    { key: "done", label: "Done", done: false },
  ];

  const attrs = analysisResult?.attributes;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Upload Clothing</h1>
        <p className="text-zinc-500 dark:text-zinc-400">
          Add new pieces to your digital wardrobe.
        </p>
      </div>

      {/* ── Step Indicator ─────────────────────────────── */}
      <div className="flex items-center gap-2">
        {steps.map((s, i) => (
          <div key={s.key} className="flex items-center gap-2">
            <div
              className={`
                flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold transition-colors
                ${s.done
                  ? "bg-green-500 text-white"
                  : (i === 0 && (step === "select" || uploadMutation.isPending))
                    || (i === 1 && (step === "uploaded" || step === "analyzing"))
                    || (i === 2 && step === "results")
                    ? "bg-violet-600 text-white"
                    : "bg-zinc-200 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-500"
                }
              `}
            >
              {s.done ? <CheckCircle2 className="h-4 w-4" /> : i + 1}
            </div>
            <span className={`text-sm font-medium ${
              s.done
                ? "text-green-500"
                : "text-zinc-500 dark:text-zinc-400"
            }`}>
              {s.label}
            </span>
            {i < steps.length - 1 && (
              <div className={`w-12 h-0.5 mx-1 transition-colors ${
                s.done ? "bg-green-500" : "bg-zinc-200 dark:bg-zinc-800"
              }`} />
            )}
          </div>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            {step === "select" && "Select Image"}
            {(step === "uploaded" || step === "analyzing") && "Analyze Your Item"}
            {step === "results" && "Analysis Results"}
          </CardTitle>
          <CardDescription>
            {step === "select" &&
              "Upload a clear photo of your clothing item. Supported formats: JPG, PNG, WEBP (Max 10MB)."}
            {step === "uploaded" &&
              "Your image has been uploaded. Click below to run AI analysis and extract attributes."}
            {step === "analyzing" &&
              "AI is analyzing your image — removing background, identifying attributes, and generating embeddings…"}
            {step === "results" &&
              "Here's what the AI found. Review the details and finish when you're ready."}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* ── Dropzone (step: select, no file) ─────── */}
          {step === "select" && !file && (
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
          )}

          {/* ── Image Preview (all steps once file chosen) ─────── */}
          {file && (
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
                {step === "select" && (
                  <Button variant="ghost" size="icon" onClick={clearFile} disabled={uploadMutation.isPending}>
                    <X className="h-4 w-4" />
                  </Button>
                )}
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

              {/* ── Upload progress bar ─────── */}
              {(uploadMutation.isPending || uploadMutation.isSuccess || uploadMutation.isError) && step === "select" && (
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

          {/* ── Analyzing spinner ─────── */}
          {step === "analyzing" && (
            <div className="flex flex-col items-center justify-center py-8 space-y-4">
              <div className="relative">
                <div className="absolute inset-0 rounded-full bg-violet-500/20 animate-ping" />
                <div className="relative flex items-center justify-center w-16 h-16 rounded-full bg-violet-600">
                  <Sparkles className="h-7 w-7 text-white animate-pulse" />
                </div>
              </div>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 text-center max-w-sm">
                Running background removal, attribute extraction, and embedding generation.
                This may take a few seconds…
              </p>
              <Loader2 className="h-5 w-5 text-violet-500 animate-spin" />
            </div>
          )}

          {/* ── Analysis Results ─────── */}
          {step === "results" && attrs && (
            <div className="space-y-5">
              {/* Compact attribute pills */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <ResultCard icon={<Shirt className="h-5 w-5" />} label="Category" value={attrs.category} />
                <ResultCard icon={<Palette className="h-5 w-5" />} label="Color" value={attrs.primary_color} />
                <ResultCard icon={<Gem className="h-5 w-5" />} label="Material" value={attrs.material} />
                <ResultCard icon={<Layers className="h-5 w-5" />} label="Pattern" value={attrs.pattern} />
              </div>

              {/* AI Stylist Response — conversational chatbot bubble */}
              {attrs.outfit_suggestions ? (
                <StylistResponse content={attrs.outfit_suggestions} animate={true} />
              ) : attrs.caption ? (
                <StylistResponse content={attrs.caption} animate={true} />
              ) : null}

              {attrs.overall_confidence !== undefined && (
                <div className="flex items-center gap-3">
                  <span className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">
                    Confidence
                  </span>
                  <Progress value={attrs.overall_confidence * 100} className="h-2 flex-1" />
                  <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                    {(attrs.overall_confidence * 100).toFixed(0)}%
                  </span>
                </div>
              )}
            </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-end space-x-4 border-t border-zinc-100 dark:border-zinc-800/50 p-6">
          {/* ── Step: select (file chosen) ─────── */}
          {step === "select" && (
            <>
              <Button variant="outline" onClick={() => router.push("/wardrobe")} disabled={uploadMutation.isPending}>
                Cancel
              </Button>
              <Button onClick={handleUpload} disabled={!file || uploadMutation.isPending}>
                {uploadMutation.isPending ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Uploading…</>
                ) : (
                  <><UploadCloud className="h-4 w-4 mr-2" /> Upload Image</>
                )}
              </Button>
            </>
          )}

          {/* ── Step: uploaded ─────── */}
          {step === "uploaded" && (
            <>
              <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
                <Trash2 className="h-4 w-4 mr-2" /> Delete
              </Button>
              <Button variant="outline" onClick={clearFile}>
                <RotateCcw className="h-4 w-4 mr-2" /> Start Over
              </Button>
              <Button onClick={handleAnalyze}>
                <Sparkles className="h-4 w-4 mr-2" /> Analyze with AI
              </Button>
            </>
          )}

          {/* ── Step: analyzing ─────── */}
          {step === "analyzing" && (
            <Button disabled>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" /> Analyzing…
            </Button>
          )}

          {/* ── Step: results ─────── */}
          {step === "results" && (
            <>
              <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
                <Trash2 className="h-4 w-4 mr-2" /> Delete
              </Button>
              <Button variant="outline" onClick={clearFile}>
                <RotateCcw className="h-4 w-4 mr-2" /> Upload Another
              </Button>
              <Button onClick={() => router.push("/wardrobe")}>
                Finish &amp; Go to Wardrobe <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}

/* ── Small result card component ──────────────────────── */
function ResultCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value?: string | null;
}) {
  return (
    <div className="flex flex-col items-center gap-2 p-4 rounded-lg bg-zinc-100 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700 text-center">
      <div className="text-violet-500">{icon}</div>
      <p className="text-[11px] font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
        {label}
      </p>
      <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200 capitalize">
        {value || "—"}
      </p>
    </div>
  );
}
