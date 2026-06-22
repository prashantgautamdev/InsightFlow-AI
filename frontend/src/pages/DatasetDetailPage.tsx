import { Fragment } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import { ArrowLeft, Download, Sparkles } from "lucide-react";
import { api } from "@/api/client";

interface EDAReport {
  dataset_id: string;
  summary: Record<string, any>;
  missing_values: Record<string, { missing_count: number; missing_pct: number }>;
  statistics: Record<string, any>;
  correlation: { columns: string[]; matrix: number[][] };
  outliers: Record<string, { count: number }>;
  ai_insights: string[];
}

function CorrelationHeatmap({ correlation }: { correlation: EDAReport["correlation"] }) {
  if (!correlation.columns?.length) return <p className="text-muted text-sm">Not enough numeric columns for correlation.</p>;
  const { columns, matrix } = correlation;
  const cell = 44;

  function colorFor(v: number) {
    const intensity = Math.abs(v);
    return v >= 0
      ? `rgba(124,58,237,${0.15 + intensity * 0.7})`
      : `rgba(244,114,182,${0.15 + intensity * 0.7})`;
  }

  return (
    <div className="overflow-x-auto">
      <div style={{ display: "grid", gridTemplateColumns: `100px repeat(${columns.length}, ${cell}px)` }}>
        <div />
        {columns.map((c) => (
          <div key={c} className="text-[10px] text-muted text-center px-1 truncate" style={{ width: cell }}>{c}</div>
        ))}
        {columns.map((rowName, i) => (
          <Fragment key={rowName}>
            <div className="text-xs text-muted truncate pr-2 flex items-center">{rowName}</div>
            {matrix[i].map((v, j) => (
              <div
                key={j}
                title={`${v}`}
                className="flex items-center justify-center text-[10px] font-medium border border-background"
                style={{ width: cell, height: cell, background: colorFor(v) }}
              >
                {v?.toFixed(2)}
              </div>
            ))}
          </Fragment>
        ))}
      </div>
    </div>
  );
}

export default function DatasetDetailPage() {
  const { datasetId } = useParams();

  const { data, isLoading } = useQuery<EDAReport>({
    queryKey: ["eda", datasetId],
    queryFn: async () => (await api.get(`/datasets/${datasetId}/eda`)).data,
    enabled: !!datasetId,
  });

  async function downloadPdf() {
    const res = await api.get(`/reports/dataset/${datasetId}/pdf`, { responseType: "blob" });
    const url = URL.createObjectURL(new Blob([res.data]));
    const a = document.createElement("a");
    a.href = url;
    a.download = "eda_report.pdf";
    a.click();
  }

  if (isLoading) return <div className="skeleton h-64 max-w-5xl" />;
  if (!data) return <p className="text-muted">Report not found.</p>;

  const missingChartData = Object.entries(data.missing_values)
    .map(([col, v]) => ({ column: col, missing_pct: v.missing_pct }))
    .filter((d) => d.missing_pct > 0)
    .sort((a, b) => b.missing_pct - a.missing_pct)
    .slice(0, 10);

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <Link to="/dashboard/datasets" className="inline-flex items-center gap-1.5 text-muted hover:text-white text-sm">
          <ArrowLeft size={16} /> Back to datasets
        </Link>
        <button onClick={downloadPdf} className="btn-secondary"><Download size={16} /> PDF Report</button>
      </div>

      <div>
        <h1 className="text-2xl font-bold mb-1">EDA Report</h1>
        <p className="text-muted text-sm">
          {data.summary.n_rows} rows · {data.summary.n_columns} columns · {data.summary.duplicate_rows} duplicate rows
        </p>
      </div>

      <div className="glass-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="text-accent-cyan" size={18} />
          <h3 className="font-semibold">AI-Generated Insights</h3>
        </div>
        <ul className="space-y-2">
          {data.ai_insights.map((insight, i) => (
            <li key={i} className="text-sm text-muted flex gap-2">
              <span className="text-primary-light">•</span> {insight}
            </li>
          ))}
        </ul>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4">Missing Values (Top 10)</h3>
          {missingChartData.length === 0 ? (
            <p className="text-muted text-sm">No missing values detected 🎉</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={missingChartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis type="number" stroke="#94A3B8" fontSize={11} unit="%" />
                <YAxis type="category" dataKey="column" stroke="#94A3B8" fontSize={11} width={90} />
                <Tooltip contentStyle={{ background: "#13131A", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12 }} />
                <Bar dataKey="missing_pct" fill="#F472B6" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4">Outlier Counts (IQR method)</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={Object.entries(data.outliers).map(([col, v]) => ({ column: col, count: v.count }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="column" stroke="#94A3B8" fontSize={10} angle={-30} textAnchor="end" height={60} />
              <YAxis stroke="#94A3B8" fontSize={11} />
              <Tooltip contentStyle={{ background: "#13131A", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12 }} />
              <Bar dataKey="count" fill="#22D3EE" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card p-6">
        <h3 className="font-semibold mb-4">Correlation Heatmap</h3>
        <CorrelationHeatmap correlation={data.correlation} />
      </div>

      <div className="glass-card p-6 overflow-x-auto">
        <h3 className="font-semibold mb-4">Column Statistics</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-muted text-xs uppercase border-b border-border">
              <th className="py-2 pr-4">Column</th>
              <th className="py-2 pr-4">Type</th>
              <th className="py-2 pr-4">Mean / Top</th>
              <th className="py-2 pr-4">Std / Unique</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(data.statistics).map(([col, stats]: [string, any]) => (
              <tr key={col} className="border-b border-border/50">
                <td className="py-2 pr-4 font-medium">{col}</td>
                <td className="py-2 pr-4 text-muted">{stats.dtype}</td>
                <td className="py-2 pr-4 text-muted">{stats.dtype === "numeric" ? stats.mean?.toFixed(2) : stats.top_value}</td>
                <td className="py-2 pr-4 text-muted">{stats.dtype === "numeric" ? stats.std?.toFixed(2) : stats.unique_values}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
