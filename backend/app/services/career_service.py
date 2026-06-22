"""
Career Recommendation System.

Matches a user's skill set against a curated catalogue of data/AI/eng
roles, scores fit, and surfaces missing skills + a learning path.
Demand/salary figures reuse the salary model for consistency.
"""
from typing import List

from app.ml.salary_model import predict_salary

ROLE_CATALOG = {
    "Data Scientist": {
        "required_skills": ["python", "sql", "machine learning", "statistics", "pandas", "scikit-learn"],
        "learning_path": [
            "Master statistics & probability",
            "Build 3 end-to-end ML projects",
            "Learn SQL for data extraction",
            "Practice Kaggle competitions",
        ],
    },
    "ML Engineer": {
        "required_skills": ["python", "tensorflow", "pytorch", "docker", "kubernetes", "aws", "machine learning"],
        "learning_path": [
            "Deepen software engineering fundamentals",
            "Learn model deployment (Docker, K8s)",
            "Build an MLOps pipeline project",
            "Get cloud certification (AWS/GCP)",
        ],
    },
    "Data Analyst": {
        "required_skills": ["sql", "excel", "tableau", "power bi", "statistics", "data visualization"],
        "learning_path": [
            "Master SQL joins & window functions",
            "Learn a BI tool deeply (Tableau or Power BI)",
            "Build a portfolio dashboard project",
            "Practice business storytelling with data",
        ],
    },
    "AI Engineer": {
        "required_skills": ["python", "nlp", "deep learning", "pytorch", "langchain", "rest api"],
        "learning_path": [
            "Learn transformer architectures",
            "Build a RAG application",
            "Practice prompt engineering & fine-tuning",
            "Ship an LLM-powered product end to end",
        ],
    },
    "Full Stack Developer": {
        "required_skills": ["javascript", "react", "node.js", "sql", "rest api", "git"],
        "learning_path": [
            "Master React + TypeScript",
            "Learn backend framework (FastAPI/Express)",
            "Build and deploy 2 full-stack apps",
            "Learn CI/CD & Docker basics",
        ],
    },
}


def recommend_careers(skills: List[str], experience_years: float) -> List[dict]:
    user_skills = {s.lower().strip() for s in skills}
    recommendations = []

    for role, meta in ROLE_CATALOG.items():
        required = set(meta["required_skills"])
        matched = user_skills & required
        missing = required - user_skills
        match_score = round(len(matched) / len(required) * 100, 1) if required else 0.0

        salary_min, salary_max, median, demand, growth = predict_salary(
            skills=list(skills), experience_years=experience_years,
            degree="Bachelor's", location="Remote",
        )

        recommendations.append({
            "role": role,
            "match_score": match_score,
            "required_skills": sorted(required),
            "missing_skills": sorted(missing),
            "learning_path": meta["learning_path"],
            "avg_salary_usd": median,
            "demand_score": demand,
        })

    recommendations.sort(key=lambda r: r["match_score"], reverse=True)
    return recommendations
