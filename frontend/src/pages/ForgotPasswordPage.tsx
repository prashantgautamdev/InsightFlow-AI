import { useState } from "react";
import { Link } from "react-router-dom";
import { Sparkles, Mail, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/auth/forgot-password", { email });
      setSent(true);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Something went wrong");
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
        <h1 className="text-2xl font-bold text-center mb-1">Reset your password</h1>
        <p className="text-muted text-center text-sm mb-8">
          {sent ? "Check your inbox for a reset link." : "Enter your email and we'll send you a reset link."}
        </p>

        {!sent && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label-text">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
                <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                  className="input-field pl-9" placeholder="you@example.com" />
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
              {loading ? <Loader2 className="animate-spin" size={18} /> : "Send reset link"}
            </button>
          </form>
        )}

        <p className="text-center text-sm text-muted mt-6">
          <Link to="/login" className="text-primary-light font-medium hover:underline">Back to login</Link>
        </p>
      </div>
    </div>
  );
}
