import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { useAuthStore } from "@/store/authStore";

export function DashboardLayout() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center justify-between border-b border-border bg-surface/30 backdrop-blur-xl px-6 py-4">
          <div>
            <p className="text-sm text-muted">Welcome back,</p>
            <p className="font-semibold">{user?.full_name ?? "there"} 👋</p>
          </div>
          <div className="h-9 w-9 rounded-full bg-gradient-hero flex items-center justify-center text-sm font-bold">
            {user?.full_name?.[0]?.toUpperCase() ?? "U"}
          </div>
        </header>
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
