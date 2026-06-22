import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Sparkles, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { api } from "@/api/client";

export default function VerifyEmailPage() {
  const [params] = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    const token = params.get("token");
    if (!token) {
      setStatus("error");
      return;
    }
    api.post("/auth/verify-email", { token })
      .then(() => setStatus("success"))
      .catch(() => setStatus("error"));
  }, [params]);

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md glass-panel p-8 text-center">
        <div className="flex items-center gap-2 justify-center mb-6">
          <Sparkles className="text-primary-light" size={22} />
          <span className="font-bold text-lg">InsightFlow <span className="gradient-text">AI</span></span>
        </div>

        {status === "loading" && <Loader2 className="animate-spin mx-auto text-primary-light" size={32} />}
        {status === "success" && (
          <>
            <CheckCircle2 className="mx-auto text-accent-green mb-4" size={40} />
            <h1 className="text-xl font-bold mb-2">Email verified!</h1>
            <p className="text-muted text-sm mb-6">Your email has been verified successfully.</p>
          </>
        )}
        {status === "error" && (
          <>
            <XCircle className="mx-auto text-red-400 mb-4" size={40} />
            <h1 className="text-xl font-bold mb-2">Verification failed</h1>
            <p className="text-muted text-sm mb-6">This link is invalid or has expired.</p>
          </>
        )}

        <Link to="/login" className="btn-primary inline-flex">Go to login</Link>
      </div>
    </div>
  );
}
