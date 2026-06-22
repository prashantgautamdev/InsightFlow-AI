import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Float, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.session import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    raw_text = Column(Text, nullable=True)

    extracted_skills = Column(JSON, default=list)
    extracted_experience = Column(JSON, default=list)
    extracted_education = Column(JSON, default=list)
    extracted_technologies = Column(JSON, default=list)

    ats_score = Column(Float, nullable=True)
    missing_skills = Column(JSON, default=list)
    skill_gap_analysis = Column(JSON, default=dict)
    career_suggestions = Column(JSON, default=list)
    roadmap = Column(JSON, default=dict)

    target_role = Column(String, nullable=True)
    report_pdf_path = Column(String, nullable=True)

    status = Column(String, default="processing")  # processing | completed | failed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="resumes")
