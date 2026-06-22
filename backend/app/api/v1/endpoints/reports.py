import os
import uuid

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.dataset import Dataset
from app.models.resume import Resume
from app.models.user import User
from app.services.report_service import generate_pdf_report, generate_csv_export, REPORTS_DIR

router = APIRouter(prefix="/reports", tags=["Report Generator"])


@router.get("/resume/{resume_id}/pdf")
def download_resume_pdf(resume_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume or not resume.report_pdf_path or not os.path.exists(resume.report_pdf_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(resume.report_pdf_path, media_type="application/pdf", filename=f"{resume.file_name}_report.pdf")


@router.get("/dataset/{dataset_id}/pdf")
def download_dataset_pdf(dataset_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset or dataset.status != "completed":
        raise HTTPException(status_code=404, detail="Dataset report not available")

    report = dataset.eda_report or {}
    output_path = os.path.join(REPORTS_DIR, f"dataset_report_{dataset.id}.pdf")
    generate_pdf_report(
        title=f"Dataset Analytics Report — {dataset.file_name}",
        sections={
            "Dataset Summary": report.get("summary", {}),
            "AI Insights": dataset.ai_insights or [],
            "Missing Values": {k: v["missing_pct"] for k, v in report.get("missing_values", {}).items()},
        },
        output_path=output_path,
    )
    return FileResponse(output_path, media_type="application/pdf", filename=f"{dataset.file_name}_report.pdf")


@router.get("/dataset/{dataset_id}/csv")
def download_dataset_csv(dataset_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")
    ext = os.path.splitext(dataset.file_path)[1].lower()
    df = pd.read_csv(dataset.file_path) if ext == ".csv" else pd.read_excel(dataset.file_path)
    csv_bytes = generate_csv_export(df)
    return StreamingResponse(
        iter([csv_bytes]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={dataset.file_name}_export.csv"},
    )
