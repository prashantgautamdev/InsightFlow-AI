import { useState } from "react";
import { Loader2, Target, ArrowUpRight } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";

interface CareerRec {
  role: string;
  match_score: number;
  required_skills: string[];
  missing_skills: string[];
  learning_path: string[];
  avg_salary_usd: number;
  demand_score: number;
}

export default function CareerRecommendationPage() {
  const [skillsInput, setSkillsInput] = useState("python, sql, pandas");
  const [experience, setExperience] = useState(2);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<CareerRec[]>([]);

  async function handleRecommend() {
    setLoading(true);
    try {
      const skills = skillsInput.split(",").map((s) => s.trim()).filter(Boolean);
      const { data } = await api.post("/career/recommend", { skills, experience_years: experience });
      setResults(data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Recommendation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold mb-1">Career Recommendation System</h1>
        <p className="text-muted text-sm">Find the best-fit data & AI roles based on your current skill set.</p>
      </div>

      <div className="glass-card p-6 grid sm:grid-cols-3 gap-5">
        <div className="sm:col-span-2">
          <label className="label-text">Your skills (comma-separated)</label>
          <input value={skillsInput} onChange={(e) => setSkillsInput(e.target.value)} className="input-field" />
        </div>
        <div>
          <label className="label-text">Experience (years)</label>
          <input type="number" min={0} max={40} step={0.5} value={experience}
            onChange={(e) => setExperience(parseFloat(e.target.value))} className="input-field" />
        </div>
        <button onClick={handleRecommend} disabled={loading} className="btn-primary sm:col-span-3">
          {loading ? <Loader2 className="animate-spin" size={18} /> : "Get Recommendations"}
        </button>
      </div>

      <div className="space-y-4">
        {results.map((rec) => (
          <div key={rec.role} className="glass-card p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-semibold text-lg">{rec.role}</h3>
                <p className="text-muted text-sm">
                  ${rec.avg_salary_usd.toLocaleString()} avg salary · Demand {rec.demand_score}/100
                </p>
              </div>
              <div className="text-right shrink-0">
                <div className="flex items-center gap-1 text-primary-light font-bold text-lg">
                  <Target size={16} /> {rec.match_score}%
                </div>
                <p className="text-muted text-xs">match</p>
              </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs font-semibold text-muted uppercase mb-2">Required Skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {rec.required_skills.map((s) => (
                    <span key={s} className="px-2 py-0.5 rounded-md bg-white/5 text-xs">{s}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs font-semibold text-muted uppercase mb-2">Missing Skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {rec.missing_skills.length === 0
                    ? <span className="text-xs text-accent-green">You have them all!</span>
                    : rec.missing_skills.map((s) => (
                        <span key={s} className="px-2 py-0.5 rounded-md bg-red-500/10 text-red-400 text-xs">{s}</span>
                      ))}
                </div>
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-muted uppercase mb-2">Learning Path</p>
              <ul className="space-y-1">
                {rec.learning_path.map((step, i) => (
                  <li key={i} className="text-sm text-muted flex gap-2">
                    <ArrowUpRight size={14} className="text-primary-light shrink-0 mt-0.5" /> {step}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
