import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Resume Analyzer
# ---------------------------------------------------------------------------
class ResumeAnalysisOut(BaseModel):
    id: uuid.UUID
    file_name: str
    extracted_skills: List[str]
    extracted_experience: List[Dict[str, Any]]
    extracted_education: List[Dict[str, Any]]
    extracted_technologies: List[str]
    ats_score: Optional[float]
    missing_skills: List[str]
    skill_gap_analysis: Dict[str, Any]
    career_suggestions: List[Dict[str, Any]]
    roadmap: Dict[str, Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Salary Prediction
# ---------------------------------------------------------------------------
class SalaryPredictionRequest(BaseModel):
    skills: List[str]
    experience_years: float
    degree: str
    location: str
    job_title: Optional[str] = None


class SalaryPredictionOut(BaseModel):
    predicted_salary_min: float
    predicted_salary_max: float
    predicted_salary_median: float
    industry_demand_score: float
    job_growth_pct: float
    currency: str = "USD"


# ---------------------------------------------------------------------------
# Career Recommendation
# ---------------------------------------------------------------------------
class CareerRecommendationRequest(BaseModel):
    skills: List[str]
    experience_years: float
    interests: Optional[List[str]] = None


class CareerRecommendationItem(BaseModel):
    role: str
    match_score: float
    required_skills: List[str]
    missing_skills: List[str]
    learning_path: List[str]
    avg_salary_usd: float
    demand_score: float


# ---------------------------------------------------------------------------
# Dataset / EDA
# ---------------------------------------------------------------------------
class DatasetOut(BaseModel):
    id: uuid.UUID
    file_name: str
    file_type: str
    n_rows: Optional[int]
    n_columns: Optional[int]
    columns_meta: Dict[str, Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class EDAReportOut(BaseModel):
    dataset_id: uuid.UUID
    summary: Dict[str, Any]
    missing_values: Dict[str, Any]
    outliers: Dict[str, Any]
    statistics: Dict[str, Any]
    correlation: Dict[str, Any]
    histograms: Dict[str, Any]
    boxplots: Dict[str, Any]
    ai_insights: List[str]


# ---------------------------------------------------------------------------
# Natural Language to Pandas
# ---------------------------------------------------------------------------
class NLQueryRequest(BaseModel):
    dataset_id: uuid.UUID
    question: str


class NLQueryResponse(BaseModel):
    question: str
    generated_code: str
    result_preview: Any
    explanation: str


# ---------------------------------------------------------------------------
# AutoML
# ---------------------------------------------------------------------------
class AutoMLRequest(BaseModel):
    dataset_id: uuid.UUID
    target_column: str
    task_type: str  # classification | regression | timeseries


class AutoMLResultOut(BaseModel):
    id: uuid.UUID
    task_type: str
    target_column: str
    models_trained: List[Dict[str, Any]]
    best_model: Optional[str]
    metrics: Dict[str, Any]
    feature_importance: Dict[str, Any]
    confusion_matrix: Optional[Any]
    roc_curve: Optional[Any]
    status: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# AI Chat Assistant
# ---------------------------------------------------------------------------
class ChatMessageRequest(BaseModel):
    session_id: Optional[uuid.UUID] = None
    dataset_id: Optional[uuid.UUID] = None
    message: str


class ChatMessageOut(BaseModel):
    session_id: uuid.UUID
    role: str
    content: str
    meta: Dict[str, Any] = {}
