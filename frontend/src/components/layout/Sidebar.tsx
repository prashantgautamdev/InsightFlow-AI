import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, FileText, DollarSign, Compass, Database,
  MessagesSquare, Cpu, ShieldCheck, LogOut, Sparkles,
} from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import clsx from "clsx";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/dashboard/resume", label: "Resume Analyzer", icon: FileText },
  { to: "/dashboard/salary", label: "Salary Prediction", icon: DollarSign },
  { to: "/dashboard/career", label: "Career Recommendations", icon: Compass },
  { to: "/dashboard/datasets", label: "Dataset Analytics", icon: Database },
  { to: "/dashboard/chat", label: "AI Data Assistant", icon: MessagesSquare },
  { to: "/dashboard/automl", label: "AutoML", icon: Cpu },
];

export function Sidebar() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  return (
    <aside className="hidden lg:flex w-64 flex-col gap-1 border-r border-border bg-surface/40 backdrop-blur-xl p-4">
      <div className="flex items-center gap-2 px-2 py-3 mb-4">
        <Sparkles className="text-primary-light" size={22} />
        <span className="font-bold text-lg">InsightFlow <span className="gradient-text">AI</span></span>
      </div>

      <nav className="flex-1 flex flex-col gap-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/15 text-primary-light border border-primary/30"
                  : "text-muted hover:bg-white/5 hover:text-white"
              )
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}

        {user?.role === "admin" && (
          <NavLink
            to="/admin"
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors mt-2 border-t border-border pt-4",
                isActive ? "text-accent-cyan" : "text-muted hover:text-white"
              )
            }
          >
            <ShieldCheck size={18} />
            Admin Dashboard
          </NavLink>
        )}
      </nav>

      <button
        onClick={() => { logout(); navigate("/login"); }}
        className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-muted hover:bg-white/5 hover:text-red-400 transition-colors"
      >
        <LogOut size={18} />
        Sign out
      </button>
    </aside>
  );
}
