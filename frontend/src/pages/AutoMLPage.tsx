import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from "recharts";
import { Loader2, Cpu, Trophy } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";

interface DatasetItem { id: string; file_name: string; status: string; columns_meta: Record<string, string> }
interface AutoMLResult {
  models_trained: { name: string; metrics: Record<string, number> }[];
  best_model: string;
  metrics: Record<string, number>;
  feature_importance: Record<string, number>;
  confusion_matrix: { labels: string[]; matrix: number[][] } | null;
}

export default function AutoMLPage() {
  const [datasetId, setDatasetId] = useState("");
  const [targetColumn, setTargetColumn] = useState("");
  const [taskType, setTaskType] = useState<"classification" | "regression">("classification");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AutoMLResult | null>(null);

  const { data: datasets } = useQuery<DatasetItem[]>({
    queryKey: ["datasets"],
    queryFn: async () => (await api.get("/datasets")).data,
  });

  const selected = datasets?.find((d) => d.id === datasetId);
  const columns = selected ? Object.keys(selected.columns_meta || {}) : [];

  async function runAutoML() {
    if (!datasetId || !targetColumn) {
      toast.error("Select a dataset and target column");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const { data } = await api.post("/automl/run", {
        dataset_id: datasetId, target_column: targetColumn, task_type: taskType,
      });
      setResult(data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "AutoML run failed");
    } finally {
      setLoading(false);
    }
  }

  const modelComparisonData = result?.models_trained.map((m) => ({
    name: m.name,
    ...m.metrics,
  })) ?? [];

  const metricKeys = result?.models_trained[0] ? Object.keys(result.models_trained[0].metrics) : [];
  const featureImportanceData = result
    ? Object.entries(result.feature_importance)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([name, value]) => ({ name, importance: value }))
    : [];

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold mb-1">AutoML</h1>
        <p className="text-muted text-sm">Train and compare Logistic Regression, Random Forest, and XGBoost in one click.</p>
      </div>

      <div className="glass-card p-6 grid sm:grid-cols-3 gap-5">
        <div>
          <label className="label-text">Dataset</label>
          <select value={datasetId} onChange={(e) => { setDatasetId(e.target.value); setTargetColumn(""); }} className="input-field">
            <option value="">Select dataset</option>
            {datasets?.filter((d) => d.status === "completed").map((d) => (
              <option key={d.id} value={d.id}>{d.file_name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label-text">Target column</label>
          <select value={targetColumn} onChange={(e) => setTargetColumn(e.target.value)} className="input-field" disabled={!columns.length}>
            <option value="">Select column</option>
            {columns.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="label-text">Task type</label>
          <select value={taskType} onChange={(e) => setTaskType(e.target.value as any)} className="input-field">
            <option value="classification">Classification</option>
            <option value="regression">Regression</option>
          </select>
        </div>
        <button onClick={runAutoML} disabled={loading} className="btn-primary sm:col-span-3">
          {loading ? <Loader2 className="animate-spin" size={18} /> : <><Cpu size={18} /> Run AutoML</>}
        </button>
      </div>

      {result && (
        <div className="space-y-5">
          <div className="glass-card p-6 flex items-center gap-4">
            <div className="h-11 w-11 rounded-xl bg-accent-green/10 flex items-center justify-center">
              <Trophy className="text-accent-green" size={20} />
            </div>
            <div>
              <p className="font-semibold">Best Model: {result.best_model}</p>
              <p className="text-muted text-sm">
                {Object.entries(result.metrics).map(([k, v]) => `${k}: ${v}`).join(" · ")}
              </p>
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="font-semibold mb-4">Model Comparison</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={modelComparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="#94A3B8" fontSize={12} />
                <YAxis stroke="#94A3B8" fontSize={12} />
                <Tooltip contentStyle={{ background: "#13131A", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12 }} />
                <Legend />
                {metricKeys.map((key, i) => (
                  <Bar key={key} dataKey={key} fill={["#7C3AED", "#22D3EE", "#F472B6", "#34D399"][i % 4]} radius={[6, 6, 0, 0]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>

          {featureImportanceData.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="font-semibold mb-4">Feature Importance (Top 10)</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={featureImportanceData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis type="number" stroke="#94A3B8" fontSize={11} />
                  <YAxis type="category" dataKey="name" stroke="#94A3B8" fontSize={11} width={110} />
                  <Tooltip contentStyle={{ background: "#13131A", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12 }} />
                  <Bar dataKey="importance" fill="#7C3AED" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {result.confusion_matrix && (
            <div className="glass-card p-6">
              <h3 className="font-semibold mb-4">Confusion Matrix</h3>
              <table className="text-sm">
                <thead>
                  <tr>
                    <th></th>
                    {result.confusion_matrix.labels.map((l) => <th key={l} className="px-3 py-1 text-muted text-xs">{l}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {result.confusion_matrix.matrix.map((row, i) => (
                    <tr key={i}>
                      <td className="px-3 py-1 text-muted text-xs">{result.confusion_matrix!.labels[i]}</td>
                      {row.map((v, j) => (
                        <td key={j} className="px-3 py-1 text-center bg-primary/10 border border-border">{v}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
