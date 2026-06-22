import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Loader2, TrendingUp, Briefcase } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";

interface SalaryResult {
  predicted_salary_min: number;
  predicted_salary_max: number;
  predicted_salary_median: number;
  industry_demand_score: number;
  job_growth_pct: number;
}

const DEGREES = ["High School", "Bachelor's", "Master's", "PhD"];
const LOCATIONS = [
  "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
  "Bengaluru, India", "London, UK", "Remote", "Toronto, Canada",
];

export default function SalaryPredictionPage() {
  const [skillsInput, setSkillsInput] = useState("python, machine learning, sql");
  const [experience, setExperience] = useState(3);
  const [degree, setDegree] = useState("Bachelor's");
  const [location, setLocation] = useState("Remote");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SalaryResult | null>(null);

  async function handlePredict() {
    setLoading(true);
    try {
      const skills = skillsInput.split(",").map((s) => s.trim()).filter(Boolean);
      const { data } = await api.post("/salary/predict", {
        skills, experience_years: experience, degree, location,
      });
      setResult(data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Prediction failed");
    } finally {
      setLoading(false);
    }
  }

  const chartData = result
    ? [
        { name: "Min", salary: result.predicted_salary_min },
        { name: "Median", salary: result.predicted_salary_median },
        { name: "Max", salary: result.predicted_salary_max },
      ]
    : [];

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold mb-1">Salary Prediction</h1>
        <p className="text-muted text-sm">ML-powered salary estimate based on your skills, experience, degree, and location.</p>
      </div>

      <div className="glass-card p-6 grid sm:grid-cols-2 gap-5">
        <div className="sm:col-span-2">
          <label className="label-text">Skills (comma-separated)</label>
          <input value={skillsInput} onChange={(e) => setSkillsInput(e.target.value)} className="input-field" />
        </div>
        <div>
          <label className="label-text">Experience (years)</label>
          <input type="number" min={0} max={40} step={0.5} value={experience}
            onChange={(e) => setExperience(parseFloat(e.target.value))} className="input-field" />
        </div>
        <div>
          <label className="label-text">Degree</label>
          <select value={degree} onChange={(e) => setDegree(e.target.value)} className="input-field">
            {DEGREES.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
        <div className="sm:col-span-2">
          <label className="label-text">Location</label>
          <select value={location} onChange={(e) => setLocation(e.target.value)} className="input-field">
            {LOCATIONS.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <button onClick={handlePredict} disabled={loading} className="btn-primary sm:col-span-2 mt-2">
          {loading ? <Loader2 className="animate-spin" size={18} /> : "Predict Salary"}
        </button>
      </div>

      {result && (
        <div className="grid md:grid-cols-2 gap-5">
          <div className="glass-card p-6">
            <h3 className="font-semibold mb-4">Predicted Salary Range (USD)</h3>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="#94A3B8" fontSize={12} />
                <YAxis stroke="#94A3B8" fontSize={12} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(v: number) => [`$${v.toLocaleString()}`, "Salary"]}
                  contentStyle={{ background: "#13131A", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12 }}
                />
                <Bar dataKey="salary" fill="#7C3AED" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-4">
            <div className="glass-card p-5 flex items-center gap-4">
              <div className="h-11 w-11 rounded-xl bg-accent-cyan/10 flex items-center justify-center">
                <TrendingUp className="text-accent-cyan" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{result.industry_demand_score}/100</p>
                <p className="text-muted text-sm">Industry Demand Score</p>
              </div>
            </div>
            <div className="glass-card p-5 flex items-center gap-4">
              <div className="h-11 w-11 rounded-xl bg-accent-green/10 flex items-center justify-center">
                <Briefcase className="text-accent-green" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">+{result.job_growth_pct}%</p>
                <p className="text-muted text-sm">Projected Job Growth (YoY)</p>
              </div>
            </div>
            <div className="glass-card p-5">
              <p className="text-muted text-sm mb-1">Median Estimate</p>
              <p className="text-3xl font-bold gradient-text">
                ${result.predicted_salary_median.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
