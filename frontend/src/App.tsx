import { Routes, Route } from "react-router-dom";
import { ProtectedRoute, AdminRoute } from "@/components/layout/ProtectedRoute";
import { DashboardLayout } from "@/components/layout/DashboardLayout";

import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ForgotPasswordPage from "@/pages/ForgotPasswordPage";
import ResetPasswordPage from "@/pages/ResetPasswordPage";
import VerifyEmailPage from "@/pages/VerifyEmailPage";

import DashboardOverview from "@/pages/DashboardOverview";
import ResumeAnalyzerPage from "@/pages/ResumeAnalyzerPage";
import SalaryPredictionPage from "@/pages/SalaryPredictionPage";
import CareerRecommendationPage from "@/pages/CareerRecommendationPage";
import DatasetAnalyticsPage from "@/pages/DatasetAnalyticsPage";
import DatasetDetailPage from "@/pages/DatasetDetailPage";
import ChatAssistantPage from "@/pages/ChatAssistantPage";
import AutoMLPage from "@/pages/AutoMLPage";
import AdminDashboardPage from "@/pages/AdminDashboardPage";
import NotFoundPage from "@/pages/NotFoundPage";

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />

      {/* Protected (user) */}
      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<DashboardOverview />} />
          <Route path="/dashboard/resume" element={<ResumeAnalyzerPage />} />
          <Route path="/dashboard/salary" element={<SalaryPredictionPage />} />
          <Route path="/dashboard/career" element={<CareerRecommendationPage />} />
          <Route path="/dashboard/datasets" element={<DatasetAnalyticsPage />} />
          <Route path="/dashboard/datasets/:datasetId" element={<DatasetDetailPage />} />
          <Route path="/dashboard/chat" element={<ChatAssistantPage />} />
          <Route path="/dashboard/automl" element={<AutoMLPage />} />
        </Route>
      </Route>

      {/* Protected (admin) */}
      <Route element={<AdminRoute />}>
        <Route element={<DashboardLayout />}>
          <Route path="/admin" element={<AdminDashboardPage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
