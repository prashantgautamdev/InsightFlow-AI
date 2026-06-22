import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  FileText, DollarSign, Compass, Database, MessagesSquare,
  Cpu, Sparkles, ArrowRight, BarChart3,
} from "lucide-react";

const FEATURES = [
  { icon: FileText, title: "AI Resume Analyzer", desc: "Upload your resume and get an ATS score, skill-gap analysis, and a personalized roadmap." },
  { icon: DollarSign, title: "Salary Prediction", desc: "ML-powered salary range predictions based on skills, experience, degree, and location." },
  { icon: Compass, title: "Career Recommendations", desc: "Discover the best-fit data & AI roles with learning paths and demand insights." },
  { icon: Database, title: "Auto EDA Generator", desc: "Upload a CSV/Excel file and instantly get missing values, outliers, correlations, and more." },
  { icon: MessagesSquare, title: "AI Dataset Chat", desc: "Ask your dataset questions in plain English using RAG-powered chat." },
  { icon: Cpu, title: "AutoML", desc: "Train and compare Logistic Regression, Random Forest, and XGBoost in one click." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <nav className="flex items-center justify-between px-6 lg:px-12 py-5">
        <div className="flex items-center gap-2">
          <Sparkles className="text-primary-light" size={24} />
          <span className="font-bold text-xl">InsightFlow <span className="gradient-text">AI</span></span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="btn-secondary">Log in</Link>
          <Link to="/register" className="btn-primary">Get Started <ArrowRight size={16} /></Link>
        </div>
      </nav>

      <section className="px-6 lg:px-12 pt-20 pb-24 text-center max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 rounded-full glass-card px-4 py-1.5 text-sm text-muted mb-6"
        >
          <BarChart3 size={14} className="text-accent-cyan" />
          AI-Powered Career Analytics & Data Science Platform
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-6xl font-extrabold tracking-tight mb-6"
        >
          Turn your <span className="gradient-text">resume & data</span> into career-changing insights
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-muted text-lg mb-10 max-w-2xl mx-auto"
        >
          Resume analysis, salary prediction, automated EDA, AutoML, and a natural-language
          data assistant — all in one premium, AI-powered platform.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex items-center justify-center gap-4"
        >
          <Link to="/register" className="btn-primary text-base px-7 py-3">
            Start Free <ArrowRight size={18} />
          </Link>
          <Link to="/login" className="btn-secondary text-base px-7 py-3">Log in</Link>
        </motion.div>
      </section>

      <section className="px-6 lg:px-12 pb-24 max-w-6xl mx-auto">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map(({ icon: Icon, title, desc }, i) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.05 }}
              className="glass-card p-6 hover:border-primary/40 transition-colors"
            >
              <div className="h-11 w-11 rounded-xl bg-gradient-hero flex items-center justify-center mb-4">
                <Icon size={20} />
              </div>
              <h3 className="font-semibold text-lg mb-2">{title}</h3>
              <p className="text-muted text-sm leading-relaxed">{desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <footer className="px-6 lg:px-12 py-8 border-t border-border text-center text-muted text-sm">
        © {new Date().getFullYear()} InsightFlow AI. Built with React, FastAPI & a lot of XGBoost.
      </footer>
    </div>
  );
}
