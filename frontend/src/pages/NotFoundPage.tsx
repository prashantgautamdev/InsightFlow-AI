import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-4">
      <p className="text-6xl font-extrabold gradient-text mb-4">404</p>
      <p className="text-muted mb-6">This page doesn't exist.</p>
      <Link to="/" className="btn-primary">Go home</Link>
    </div>
  );
}
