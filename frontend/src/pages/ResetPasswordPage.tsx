import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Sparkles, Lock, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";

export default function ResetPasswordPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) {
      toast.error("Missing or invalid reset token");
      return;
    }
    setLoading(true);
    try {
      await api.post("/auth/reset-password", { token, new_password: password });
      toast.success("Password reset! Please log in.");
      navigate("/login");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Reset failed");
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
        <h1 className="text-2xl font-bold text-center mb-1">Set a new password</h1>
        <p className="text-muted text-center text-sm mb-8">Choose a strong new password for your account.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label-text">New password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
              <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)}
                className="input-field pl-9" placeholder="At least 8 characters" />
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
            {loading ? <Loader2 className="animate-spin" size={18} /> : "Reset password"}
          </button>
        </form>

        <p className="text-center text-sm text-muted mt-6">
          <Link to="/login" className="text-primary-light font-medium hover:underline">Back to login</Link>
        </p>
      </div>
    </div>
  );
}
