"""
Salary Prediction model.

For a portfolio project there's no proprietary salary dataset available,
so this module:
  1. Generates a realistic synthetic training dataset driven by sensible
     market-rate rules (skills premium, experience curve, location
     multiplier, degree multiplier) plus noise.
  2. Trains an XGBoost regressor on it once, caches it to disk (joblib).
  3. Serves predictions + a 90% interval as min/max range, plus a simple
     demand/growth score derived from the skill mix.

Swap `generate_synthetic_training_data()` for a real labeled dataset
(e.g. Kaggle "Data Science Salaries" or scraped job-board data) to make
this production-grade.
"""
import os
import random
from typing import List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "salary_model.joblib")

DEGREES = ["High School", "Bachelor's", "Master's", "PhD"]
LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
    "Bengaluru, India", "London, UK", "Remote", "Toronto, Canada",
]
HIGH_VALUE_SKILLS = {
    "machine learning": 18000, "deep learning": 20000, "xgboost": 9000,
    "tensorflow": 12000, "pytorch": 13000, "aws": 10000, "kubernetes": 11000,
    "nlp": 12000, "computer vision": 13000, "spark": 9000, "airflow": 7000,
    "react": 6000, "fastapi": 5000, "sql": 4000, "python": 5000,
}
DEGREE_PREMIUM = {"High School": 0, "Bachelor's": 8000, "Master's": 18000, "PhD": 32000}
LOCATION_MULTIPLIER = {
    "San Francisco, CA": 1.35, "New York, NY": 1.25, "Seattle, WA": 1.2,
    "Austin, TX": 1.05, "Bengaluru, India": 0.45, "London, UK": 1.0,
    "Remote": 1.0, "Toronto, Canada": 0.9,
}
BASE_SALARY = 65000


def _generate_synthetic_training_data(n: int = 4000, seed: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    skills_pool = list(HIGH_VALUE_SKILLS.keys())
    for _ in range(n):
        n_skills = rng.randint(1, 8)
        skills = rng.sample(skills_pool, n_skills)
        exp = round(rng.uniform(0, 18), 1)
        degree = rng.choice(DEGREES)
        location = rng.choice(LOCATIONS)

        skill_value = sum(HIGH_VALUE_SKILLS[s] for s in skills)
        exp_value = 4200 * exp - (exp ** 2 * 60)  # diminishing returns
        salary = (
            BASE_SALARY + skill_value + exp_value + DEGREE_PREMIUM[degree]
        ) * LOCATION_MULTIPLIER[location]
        salary += rng.gauss(0, 6000)  # noise
        salary = max(salary, 25000)

        rows.append({
            "n_skills": n_skills,
            "skill_value": skill_value,
            "experience_years": exp,
            "degree": degree,
            "location": location,
            "salary": salary,
        })
    return pd.DataFrame(rows)


def _build_pipeline() -> Pipeline:
    categorical = ["degree", "location"]
    numeric = ["n_skills", "skill_value", "experience_years"]
    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ], remainder="passthrough")
    model = XGBRegressor(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, random_state=42,
    )
    return Pipeline([("prep", preprocessor), ("model", model)])


def train_and_save_model() -> Pipeline:
    df = _generate_synthetic_training_data()
    X = df[["n_skills", "skill_value", "experience_years", "degree", "location"]]
    y = df["salary"]
    pipeline = _build_pipeline()
    pipeline.fit(X, y)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


def load_or_train_model() -> Pipeline:
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return train_and_save_model()


def _skill_value(skills: List[str]) -> int:
    return sum(HIGH_VALUE_SKILLS.get(s.lower().strip(), 2500) for s in skills)


def predict_salary(
    skills: List[str], experience_years: float, degree: str, location: str
) -> Tuple[float, float, float, float, float]:
    """Returns (min, max, median, demand_score, growth_pct)."""
    pipeline = load_or_train_model()

    degree = degree if degree in DEGREES else "Bachelor's"
    location = location if location in LOCATIONS else "Remote"

    row = pd.DataFrame([{
        "n_skills": len(skills),
        "skill_value": _skill_value(skills),
        "experience_years": experience_years,
        "degree": degree,
        "location": location,
    }])
    median_pred = float(pipeline.predict(row)[0])
    salary_min = round(median_pred * 0.88, -2)
    salary_max = round(median_pred * 1.15, -2)
    median_pred = round(median_pred, -2)

    # Demand score: more high-value / in-demand skills => higher score (0-100)
    matched_high_value = sum(1 for s in skills if s.lower().strip() in HIGH_VALUE_SKILLS)
    demand_score = round(min(100, 40 + matched_high_value * 8 + min(experience_years, 10) * 2), 1)

    # Growth: AI/ML-heavy skill sets get a higher projected YoY growth
    ai_skill_overlap = len({"machine learning", "deep learning", "nlp", "computer vision"} &
                            {s.lower().strip() for s in skills})
    growth_pct = round(6 + ai_skill_overlap * 3.5 + np.random.uniform(-0.5, 0.5), 1)

    return salary_min, salary_max, median_pred, demand_score, growth_pct
