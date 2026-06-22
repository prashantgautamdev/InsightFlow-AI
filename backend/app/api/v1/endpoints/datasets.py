import os
import uuid

import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.database.session import get_db
from app.ml.eda_engine import run_full_eda, clean_dataset
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.data import DatasetOut, EDAReportOut
from app.services.insight_service import generate_dataset_insights
from app.services.rag_chat_service import index_dataset

router = APIRouter(prefix="/datasets", tags=["Dataset Analytics"])

DATASET_UPLOAD_DIR = os.path.join(settings.UPLOAD_DIR, "datasets")
os.makedirs(DATASET_UPLOAD_DIR, exist_ok=True)


def _read_dataframe(path: str, ext: str) -> pd.DataFrame:
    if ext == ".csv":
        return pd.read_csv(path)
    return pd.read_excel(path)


@router.post("/upload", response_model=DatasetOut)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_DATASET_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only CSV/Excel files are supported")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(DATASET_UPLOAD_DIR, f"{file_id}{ext}")
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    with open(file_path, "wb") as f:
        f.write(content)

    dataset = Dataset(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        file_type=ext.replace(".", ""),
        status="processing",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    try:
        df = _read_dataframe(file_path, ext)
        eda_report = run_full_eda(df)
        insights = generate_dataset_insights(eda_report, df.columns.tolist())

        dataset.n_rows = df.shape[0]
        dataset.n_columns = df.shape[1]
        dataset.columns_meta = {col: str(dtype) for col, dtype in df.dtypes.items()}
        dataset.eda_report = eda_report
        dataset.ai_insights = insights
        dataset.status = "completed"

        # Index into vector store for the RAG chat assistant
        index_dataset(f"dataset_{dataset.id}", df, eda_report)

    except Exception as exc:
        dataset.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Dataset processing failed: {exc}")

    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("", response_model=list[DatasetOut])
def list_datasets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Dataset)
        .filter(Dataset.user_id == current_user.id)
        .order_by(Dataset.created_at.desc())
        .all()
    )


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(dataset_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("/{dataset_id}/eda", response_model=EDAReportOut)
def get_eda_report(dataset_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.status != "completed":
        raise HTTPException(status_code=409, detail=f"Dataset is {dataset.status}")
    report = dataset.eda_report or {}
    return EDAReportOut(
        dataset_id=dataset.id,
        summary=report.get("summary", {}),
        missing_values=report.get("missing_values", {}),
        outliers=report.get("outliers", {}),
        statistics=report.get("statistics", {}),
        correlation=report.get("correlation", {}),
        histograms=report.get("histograms", {}),
        boxplots=report.get("boxplots", {}),
        ai_insights=dataset.ai_insights or [],
    )


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
    db.delete(dataset)
    db.commit()
    return {"message": "Dataset deleted"}
