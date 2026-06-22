import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles, Mail, Lock, User, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/auth/register", { full_name: fullName, email, password });
      toast.success("Account created! Check your email to verify, then log in.");
      navigate("/login");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Registration failed");
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
        <h1 className="text-2xl font-bold text-center mb-1">Create your account</h1>
        <p className="text-muted text-center text-sm mb-8">Start analyzing your career & data for free</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label-text">Full name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
              <input required value={fullName} onChange={(e) => setFullName(e.target.value)}
                className="input-field pl-9" placeholder="Jane Doe" />
            </div>
          </div>
          <div>
            <label className="label-text">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                className="input-field pl-9" placeholder="you@example.com" />
            </div>
          </div>
          <div>
            <label className="label-text">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
              <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)}
                className="input-field pl-9" placeholder="At least 8 characters" />
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
            {loading ? <Loader2 className="animate-spin" size={18} /> : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-muted mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-primary-light font-medium hover:underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}
