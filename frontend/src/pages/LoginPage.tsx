import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles, Mail, Lock, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";
import { useAuthStore } from "@/store/authStore";

export default function LoginPage() {
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", { email, password });
      setTokens(data.access_token, data.refresh_token);
      const me = await api.get("/auth/me", {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
      setUser(me.data);
      toast.success("Welcome back!");
      navigate("/dashboard");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md glass-panel p-8">
        <div className="flex items-center gap-2 justify-center mb-6">
          <Sparkles className="text-primary-light" size={22} />
          <span className="font-bold text-lg">InsightFlow <span className="gradient-text">AI</span></span>
        </div>
        <h1 className="text-2xl font-bold text-center mb-1">Welcome back</h1>
        <p className="text-muted text-center text-sm mb-8">Log in to your account</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label-text">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                className="input-field pl-9" placeholder="you@example.com" />
            </div>
          </div>
          <div>
            <div className="flex justify-between">
              <label className="label-text">Password</label>
              <Link to="/forgot-password" className="text-xs text-primary-light hover:underline">Forgot?</Link>
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
              <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                className="input-field pl-9" placeholder="••••••••" />
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
            {loading ? <Loader2 className="animate-spin" size={18} /> : "Log in"}
          </button>
        </form>

        <p className="text-center text-sm text-muted mt-6">
          Don't have an account?{" "}
          <Link to="/register" className="text-primary-light font-medium hover:underline">Sign up</Link>
        </p>
      </div>
    </div>
  );
}
