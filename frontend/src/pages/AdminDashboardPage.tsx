import { useQuery } from "@tanstack/react-query";
import { Users, Database, FileText, Cpu, Activity } from "lucide-react";
import { api } from "@/api/client";

interface Overview {
  total_users: number;
  active_users: number;
  new_users_7d: number;
  total_datasets_uploaded: number;
  total_resumes_analyzed: number;
  total_ml_runs: number;
}

export default function AdminDashboardPage() {
  const { data: overview, isLoading } = useQuery<Overview>({
    queryKey: ["admin-overview"],
    queryFn: async () => (await api.get("/admin/overview")).data,
  });

  const { data: users } = useQuery({
    queryKey: ["admin-users"],
    queryFn: async () => (await api.get("/admin/users")).data,
  });

  const { data: apiUsage } = useQuery({
    queryKey: ["admin-api-usage"],
    queryFn: async () => (await api.get("/admin/api-usage")).data,
  });

  const stats = [
    { label: "Total Users", value: overview?.total_users, icon: Users, color: "text-primary-light" },
    { label: "Active Users", value: overview?.active_users, icon: Activity, color: "text-accent-green" },
    { label: "New Users (7d)", value: overview?.new_users_7d, icon: Users, color: "text-accent-cyan" },
    { label: "Datasets Uploaded", value: overview?.total_datasets_uploaded, icon: Database, color: "text-accent-cyan" },
    { label: "Resumes Analyzed", value: overview?.total_resumes_analyzed, icon: FileText, color: "text-accent-pink" },
    { label: "AutoML Runs", value: overview?.total_ml_runs, icon: Cpu, color: "text-primary-light" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold mb-1">Admin Dashboard</h1>
        <p className="text-muted text-sm">Platform-wide user, usage, and revenue analytics.</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="glass-card p-5 flex items-center gap-4">
            <div className="h-11 w-11 rounded-xl bg-white/5 flex items-center justify-center">
              <Icon className={color} size={20} />
            </div>
            <div>
              {isLoading ? <div className="skeleton h-7 w-12" /> : <p className="text-2xl font-bold">{value}</p>}
              <p className="text-muted text-xs">{label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4">Recent Users</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {users?.map((u: any) => (
              <div key={u.id} className="flex items-center justify-between text-sm py-2 border-b border-border/50">
                <div>
                  <p className="font-medium">{u.full_name}</p>
                  <p className="text-muted text-xs">{u.email}</p>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-md ${u.is_active ? "bg-accent-green/10 text-accent-green" : "bg-red-500/10 text-red-400"}`}>
                  {u.is_active ? "Active" : "Disabled"}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4">API Usage by Endpoint</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {apiUsage?.map((row: any) => (
              <div key={row.action} className="flex items-center justify-between text-sm py-2 border-b border-border/50">
                <span className="text-muted truncate">{row.action}</span>
                <span className="font-medium">{row.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
