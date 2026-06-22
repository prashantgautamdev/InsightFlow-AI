import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.session import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # csv | xlsx

    n_rows = Column(Integer, nullable=True)
    n_columns = Column(Integer, nullable=True)
    columns_meta = Column(JSON, default=dict)   # dtypes, null counts, etc.

    eda_report = Column(JSON, default=dict)     # full EDA result blob
    ai_insights = Column(JSON, default=list)    # AI-generated narrative insights

    status = Column(String, default="processing")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="datasets")
    ml_runs = relationship("MLRun", back_populates="dataset", cascade="all, delete-orphan")


class MLRun(Base):
    """A single AutoML training run against a dataset."""
    __tablename__ = "ml_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    task_type = Column(String, nullable=False)     # classification | regression | timeseries
    target_column = Column(String, nullable=False)

    models_trained = Column(JSON, default=list)    # list of {name, metrics}
    best_model = Column(String, nullable=True)
    metrics = Column(JSON, default=dict)            # accuracy, precision, recall, f1, rmse, mae...
    feature_importance = Column(JSON, default=dict)
    confusion_matrix = Column(JSON, nullable=True)
    roc_curve = Column(JSON, nullable=True)

    model_artifact_path = Column(String, nullable=True)
    status = Column(String, default="queued")        # queued | running | completed | failed

    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="ml_runs")


class SalaryPrediction(Base):
    __tablename__ = "salary_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    skills = Column(JSON, default=list)
    experience_years = Column(Float, nullable=False)
    degree = Column(String, nullable=False)
    location = Column(String, nullable=False)
    job_title = Column(String, nullable=True)

    predicted_salary_min = Column(Float, nullable=True)
    predicted_salary_max = Column(Float, nullable=True)
    predicted_salary_median = Column(Float, nullable=True)
    industry_demand_score = Column(Float, nullable=True)
    job_growth_pct = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="salary_predictions")
