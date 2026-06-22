import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, Loader2, Download, CheckCircle2 } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";

interface ResumeResult {
  id: string;
  file_name: string;
  ats_score: number;
  extracted_skills: string[];
  missing_skills: string[];
  skill_gap_analysis: { strengths?: string[]; gaps?: string[] };
  career_suggestions: { role: string; fit_reason: string }[];
  roadmap: { next_3_months?: string[]; next_6_months?: string[]; next_12_months?: string[] };
}

export default function ResumeAnalyzerPage() {
  const [targetRole, setTargetRole] = useState("Data Scientist");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResumeResult | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("target_role", targetRole);
      const { data } = await api.post("/resume/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(data);
      toast.success("Resume analyzed successfully!");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Analysis failed");
    } finally {
      setLoading(false);
    }
  }, [targetRole]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    disabled: loading,
  });

  async function downloadReport() {
    if (!result) return;
    const res = await api.get(`/reports/resume/${result.id}/pdf`, { responseType: "blob" });
    const url = URL.createObjectURL(new Blob([res.data]));
    const a = document.createElement("a");
    a.href = url;
    a.download = `${result.file_name}_report.pdf`;
    a.click();
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold mb-1">AI Resume Analyzer</h1>
        <p className="text-muted text-sm">Upload your resume to get an ATS score, skill-gap analysis, and a personalized roadmap.</p>
      </div>

      <div className="glass-card p-6">
        <label className="label-text">Target role</label>
        <input
          value={targetRole}
          onChange={(e) => setTargetRole(e.target.value)}
          className="input-field max-w-sm mb-5"
          placeholder="e.g. Data Scientist"
        />

        <div
          {...getRootProps()}
          className={`rounded-2xl border-2 border-dashed p-10 text-center cursor-pointer transition-colors ${
            isDragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
          }`}
        >
          <input {...getInputProps()} />
          {loading ? (
            <Loader2 className="animate-spin mx-auto text-primary-light mb-3" size={32} />
          ) : (
            <UploadCloud className="mx-auto text-muted mb-3" size={32} />
          )}
          <p className="font-medium">{loading ? "Analyzing your resume..." : "Drop your PDF resume here, or click to browse"}</p>
          <p className="text-muted text-xs mt-1">PDF only, max 25MB</p>
        </div>
      </div>

      {result && (
        <div className="space-y-5">
          <div className="glass-card p-6 flex items-center gap-6">
            <div className="relative h-24 w-24 shrink-0">
              <svg className="h-24 w-24 -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="44" stroke="rgba(255,255,255,0.08)" strokeWidth="8" fill="none" />
                <circle
                  cx="50" cy="50" r="44" stroke="url(#grad)" strokeWidth="8" fill="none"
                  strokeDasharray={`${(result.ats_score / 100) * 276} 276`}
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#7C3AED" />
                    <stop offset="100%" stopColor="#22D3EE" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex items-center justify-center font-bold text-xl">
                {result.ats_score}
              </div>
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-lg mb-1">ATS Score</h3>
              <p className="text-muted text-sm">{result.file_name}</p>
            </div>
            <button onClick={downloadReport} className="btn-secondary">
              <Download size={16} /> PDF Report
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-5">
            <div className="glass-card p-6">
              <h3 className="font-semibold mb-3">Detected Skills</h3>
              <div className="flex flex-wrap gap-2">
                {result.extracted_skills.map((s) => (
                  <span key={s} className="px-2.5 py-1 rounded-lg bg-accent-green/10 text-accent-green text-xs border border-accent-green/20">{s}</span>
                ))}
              </div>
            </div>
            <div className="glass-card p-6">
              <h3 className="font-semibold mb-3">Missing Skills</h3>
              <div className="flex flex-wrap gap-2">
                {result.missing_skills.length === 0 && <p className="text-muted text-sm">None detected — great coverage!</p>}
                {result.missing_skills.map((s) => (
                  <span key={s} className="px-2.5 py-1 rounded-lg bg-red-500/10 text-red-400 text-xs border border-red-500/20">{s}</span>
                ))}
              </div>
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="font-semibold mb-3">Career Suggestions</h3>
            <div className="space-y-3">
              {result.career_suggestions.map((c, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-white/5">
                  <CheckCircle2 className="text-primary-light shrink-0 mt-0.5" size={16} />
                  <div>
                    <p className="font-medium text-sm">{c.role}</p>
                    <p className="text-muted text-xs">{c.fit_reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="font-semibold mb-4">Personalized Roadmap</h3>
            <div className="grid sm:grid-cols-3 gap-4">
              {[
                { label: "Next 3 Months", items: result.roadmap.next_3_months },
                { label: "Next 6 Months", items: result.roadmap.next_6_months },
                { label: "Next 12 Months", items: result.roadmap.next_12_months },
              ].map(({ label, items }) => (
                <div key={label}>
                  <p className="text-xs font-semibold text-primary-light mb-2 uppercase tracking-wide">{label}</p>
                  <ul className="space-y-1.5">
                    {(items ?? []).map((item, i) => (
                      <li key={i} className="text-sm text-muted flex gap-2">
                        <FileText size={14} className="shrink-0 mt-0.5" /> {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
