import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.data import ResumeAnalysisOut
from app.services.resume_service import (
    extract_text_from_pdf, extract_skills, extract_education,
    extract_experience_years, analyze_resume_with_ai,
)
from app.services.report_service import generate_pdf_report, REPORTS_DIR

router = APIRouter(prefix="/resume", tags=["Resume Analyzer"])

RESUME_UPLOAD_DIR = os.path.join(settings.UPLOAD_DIR, "resumes")
os.makedirs(RESUME_UPLOAD_DIR, exist_ok=True)


@router.post("/analyze", response_model=ResumeAnalysisOut)
async def analyze_resume(
    file: UploadFile = File(...),
    target_role: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(RESUME_UPLOAD_DIR, f"{file_id}.pdf")
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    with open(file_path, "wb") as f:
        f.write(content)

    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        target_role=target_role,
        status="processing",
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    try:
        text = extract_text_from_pdf(file_path)
        skills = extract_skills(text)
        education = extract_education(text)
        ai_result = analyze_resume_with_ai(text, skills, target_role)

        resume.raw_text = text[:20000]
        resume.extracted_skills = skills
        resume.extracted_experience = [{"years_detected": extract_experience_years(text)}]
        resume.extracted_education = education
        resume.extracted_technologies = skills
        resume.ats_score = ai_result.get("ats_score")
        resume.missing_skills = ai_result.get("missing_skills", [])
        resume.skill_gap_analysis = ai_result.get("skill_gap_analysis", {})
        resume.career_suggestions = ai_result.get("career_suggestions", [])
        resume.roadmap = ai_result.get("roadmap", {})
        resume.status = "completed"

        # Generate downloadable PDF report
        report_path = os.path.join(REPORTS_DIR, f"resume_report_{resume.id}.pdf")
        generate_pdf_report(
            title=f"Resume Analysis Report — {file.filename}",
            sections={
                "ATS Score": f"{resume.ats_score}/100",
                "Detected Skills": skills,
                "Missing Skills": resume.missing_skills,
                "Career Suggestions": [c.get("role", "") for c in resume.career_suggestions],
                "12-Month Roadmap": resume.roadmap.get("next_12_months", []),
            },
            output_path=report_path,
        )
        resume.report_pdf_path = report_path

    except Exception as exc:
        resume.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {exc}")

    db.commit()
    db.refresh(resume)
    return resume


@router.get("/history", response_model=list[ResumeAnalysisOut])
def resume_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )


@router.get("/{resume_id}", response_model=ResumeAnalysisOut)
def get_resume(resume_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
