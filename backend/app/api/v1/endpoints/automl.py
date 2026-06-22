import os

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.ml.automl_engine import run_classification_automl, run_regression_automl
from app.models.dataset import Dataset, MLRun
from app.models.user import User
from app.schemas.data import AutoMLRequest, AutoMLResultOut

router = APIRouter(prefix="/automl", tags=["AutoML"])


@router.post("/run", response_model=AutoMLResultOut)
def run_automl(
    payload: AutoMLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dataset = db.query(Dataset).filter(
        Dataset.id == payload.dataset_id, Dataset.user_id == current_user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=410, detail="Dataset file is no longer available")

    ext = os.path.splitext(dataset.file_path)[1].lower()
    df = pd.read_csv(dataset.file_path) if ext == ".csv" else pd.read_excel(dataset.file_path)

    if payload.target_column not in df.columns:
        raise HTTPException(status_code=400, detail="target_column not found in dataset")

    run = MLRun(
        dataset_id=dataset.id,
        task_type=payload.task_type,
        target_column=payload.target_column,
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        if payload.task_type == "classification":
            result = run_classification_automl(df, payload.target_column)
        elif payload.task_type == "regression":
            result = run_regression_automl(df, payload.target_column)
        else:
            raise HTTPException(status_code=400, detail="task_type must be 'classification' or 'regression'")

        run.models_trained = result["models_trained"]
        run.best_model = result["best_model"]
        run.metrics = result["metrics"]
        run.feature_importance = result["feature_importance"]
        run.confusion_matrix = result["confusion_matrix"]
        run.roc_curve = result["roc_curve"]
        run.status = "completed"

    except HTTPException:
        run.status = "failed"
        db.commit()
        raise
    except Exception as exc:
        run.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"AutoML run failed: {exc}")

    db.commit()
    db.refresh(run)
    return run


@router.get("/runs/{dataset_id}", response_model=list[AutoMLResultOut])
def list_runs(dataset_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return db.query(MLRun).filter(MLRun.dataset_id == dataset_id).order_by(MLRun.created_at.desc()).all()
