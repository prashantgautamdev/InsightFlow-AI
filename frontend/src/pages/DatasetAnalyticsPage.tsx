import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { UploadCloud, Loader2, Database, ArrowRight, Trash2 } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";
import { useState } from "react";

interface DatasetItem {
  id: string;
  file_name: string;
  file_type: string;
  n_rows: number | null;
  n_columns: number | null;
  status: string;
  created_at: string;
}

export default function DatasetAnalyticsPage() {
  const queryClient = useQueryClient();
  const [uploading, setUploading] = useState(false);

  const { data: datasets, isLoading } = useQuery<DatasetItem[]>({
    queryKey: ["datasets"],
    queryFn: async () => (await api.get("/datasets")).data,
  });

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await api.post("/datasets/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success("Dataset processed! EDA report ready.");
      queryClient.invalidateQueries({ queryKey: ["datasets"] });
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [queryClient]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  async function handleDelete(id: string) {
    await api.delete(`/datasets/${id}`);
    queryClient.invalidateQueries({ queryKey: ["datasets"] });
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold mb-1">Dataset Analytics</h1>
        <p className="text-muted text-sm">Upload a CSV or Excel file for an instant, complete Auto EDA report.</p>
      </div>

      <div className="glass-card p-6">
        <div
          {...getRootProps()}
          className={`rounded-2xl border-2 border-dashed p-10 text-center cursor-pointer transition-colors ${
            isDragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
          }`}
        >
          <input {...getInputProps()} />
          {uploading ? (
            <Loader2 className="animate-spin mx-auto text-primary-light mb-3" size={32} />
          ) : (
            <UploadCloud className="mx-auto text-muted mb-3" size={32} />
          )}
          <p className="font-medium">{uploading ? "Running EDA pipeline..." : "Drop CSV/Excel here, or click to browse"}</p>
          <p className="text-muted text-xs mt-1">CSV or XLSX, max 25MB</p>
        </div>
      </div>

      <div>
        <h2 className="font-semibold mb-3">Your Datasets</h2>
        {isLoading && (
          <div className="grid sm:grid-cols-2 gap-4">
            {[1, 2].map((i) => <div key={i} className="skeleton h-28" />)}
          </div>
        )}
        <div className="grid sm:grid-cols-2 gap-4">
          {datasets?.map((d) => (
            <div key={d.id} className="glass-card p-5 flex items-center gap-4">
              <div className="h-11 w-11 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                <Database className="text-primary-light" size={20} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">{d.file_name}</p>
                <p className="text-muted text-xs">
                  {d.n_rows ?? "—"} rows · {d.n_columns ?? "—"} cols · {d.status}
                </p>
              </div>
              {d.status === "completed" && (
                <Link to={`/dashboard/datasets/${d.id}`} className="btn-secondary !px-3 !py-2">
                  <ArrowRight size={16} />
                </Link>
              )}
              <button onClick={() => handleDelete(d.id)} className="text-muted hover:text-red-400 transition-colors p-2">
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
        {!isLoading && datasets?.length === 0 && (
          <p className="text-muted text-sm">No datasets uploaded yet.</p>
        )}
      </div>
    </div>
  );
}
