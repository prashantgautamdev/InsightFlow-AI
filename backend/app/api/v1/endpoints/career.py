from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.ml.salary_model import predict_salary
from app.models.dataset import SalaryPrediction
from app.models.user import User
from app.schemas.data import (
    SalaryPredictionRequest, SalaryPredictionOut,
    CareerRecommendationRequest, CareerRecommendationItem,
)
from app.services.career_service import recommend_careers

router = APIRouter(tags=["Career Analytics"])


@router.post("/salary/predict", response_model=SalaryPredictionOut)
def predict_salary_endpoint(
    payload: SalaryPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s_min, s_max, s_median, demand, growth = predict_salary(
        skills=payload.skills,
        experience_years=payload.experience_years,
        degree=payload.degree,
        location=payload.location,
    )

    record = SalaryPrediction(
        user_id=current_user.id,
        skills=payload.skills,
        experience_years=payload.experience_years,
        degree=payload.degree,
        location=payload.location,
        job_title=payload.job_title,
        predicted_salary_min=s_min,
        predicted_salary_max=s_max,
        predicted_salary_median=s_median,
        industry_demand_score=demand,
        job_growth_pct=growth,
    )
    db.add(record)
    db.commit()

    return SalaryPredictionOut(
        predicted_salary_min=s_min,
        predicted_salary_max=s_max,
        predicted_salary_median=s_median,
        industry_demand_score=demand,
        job_growth_pct=growth,
    )


@router.get("/salary/history", response_model=list[SalaryPredictionOut])
def salary_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(SalaryPrediction)
        .filter(SalaryPrediction.user_id == current_user.id)
        .order_by(SalaryPrediction.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        SalaryPredictionOut(
            predicted_salary_min=r.predicted_salary_min,
            predicted_salary_max=r.predicted_salary_max,
            predicted_salary_median=r.predicted_salary_median,
            industry_demand_score=r.industry_demand_score,
            job_growth_pct=r.job_growth_pct,
        )
        for r in rows
    ]


@router.post("/career/recommend", response_model=list[CareerRecommendationItem])
def recommend_career_endpoint(
    payload: CareerRecommendationRequest,
    current_user: User = Depends(get_current_user),
):
    return recommend_careers(payload.skills, payload.experience_years)
