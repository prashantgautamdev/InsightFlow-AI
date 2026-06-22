import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { FileText, DollarSign, Database, Cpu, ArrowRight } from "lucide-react";
import { api } from "@/api/client";

async function fetchOverviewData() {
  const [resumes, datasets, salary] = await Promise.allSettled([
    api.get("/resume/history"),
    api.get("/datasets"),
    api.get("/salary/history"),
  ]);
  return {
    resumes: resumes.status === "fulfilled" ? resumes.value.data : [],
    datasets: datasets.status === "fulfilled" ? datasets.value.data : [],
    salaryPredictions: salary.status === "fulfilled" ? salary.value.data : [],
  };
}

const QUICK_LINKS = [
  { to: "/dashboard/resume", icon: FileText, title: "Analyze a Resume", desc: "Get your ATS score & roadmap" },
  { to: "/dashboard/salary", icon: DollarSign, title: "Predict Salary", desc: "ML-powered salary range" },
  { to: "/dashboard/datasets", icon: Database, title: "Upload a Dataset", desc: "Instant Auto EDA report" },
  { to: "/dashboard/automl", icon: Cpu, title: "Run AutoML", desc: "Compare ML models in one click" },
];

export default function DashboardOverview() {
  const { data, isLoading } = useQuery({ queryKey: ["overview"], queryFn: fetchOverviewData });

  const stats = [
    { label: "Resumes Analyzed", value: data?.resumes?.length ?? 0 },
    { label: "Datasets Uploaded", value: data?.datasets?.length ?? 0 },
    { label: "Salary Predictions", value: data?.salaryPredictions?.length ?? 0 },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-1">Overview</h1>
        <p className="text-muted text-sm">Here's a snapshot of your career & data analytics activity.</p>
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        {stats.map((s) => (
          <div key={s.label} className="glass-card p-5">
            {isLoading ? (
              <div className="skeleton h-8 w-16 mb-2" />
            ) : (
              <p className="text-3xl font-bold gradient-text">{s.value}</p>
            )}
            <p className="text-muted text-sm mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      <div>
        <h2 className="font-semibold mb-3">Quick actions</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {QUICK_LINKS.map(({ to, icon: Icon, title, desc }) => (
            <Link key={to} to={to} className="glass-card p-5 group hover:border-primary/40 transition-colors">
              <div className="h-10 w-10 rounded-xl bg-gradient-hero flex items-center justify-center mb-3">
                <Icon size={18} />
              </div>
              <p className="font-semibold text-sm mb-1">{title}</p>
              <p className="text-muted text-xs mb-3">{desc}</p>
              <span className="text-xs text-primary-light inline-flex items-center gap-1 group-hover:gap-2 transition-all">
                Go <ArrowRight size={12} />
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
