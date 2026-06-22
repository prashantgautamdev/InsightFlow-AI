"""
Celery application for offloading long-running tasks (large dataset EDA,
AutoML training) so API requests don't block. The synchronous endpoints in
this project run these operations inline for simplicity/demo purposes —
swap to `.delay()` calls + polling/websockets for very large datasets.
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "insightflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)


@celery_app.task(name="tasks.run_eda_async")
def run_eda_async(dataset_id: str):
    """
    Example async task: re-runs the EDA pipeline for a dataset by ID.
    Wire this up from the upload endpoint with `run_eda_async.delay(dataset_id)`
    if you want uploads to return immediately and poll for completion.
    """
    import os
    import pandas as pd
    from app.database.session import SessionLocal
    from app.models.dataset import Dataset
    from app.ml.eda_engine import run_full_eda
    from app.services.insight_service import generate_dataset_insights

    db = SessionLocal()
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            return {"error": "dataset not found"}

        ext = os.path.splitext(dataset.file_path)[1].lower()
        df = pd.read_csv(dataset.file_path) if ext == ".csv" else pd.read_excel(dataset.file_path)

        eda_report = run_full_eda(df)
        insights = generate_dataset_insights(eda_report, df.columns.tolist())

        dataset.eda_report = eda_report
        dataset.ai_insights = insights
        dataset.status = "completed"
        db.commit()
        return {"status": "completed", "dataset_id": dataset_id}
    except Exception as exc:
        db.rollback()
        return {"status": "failed", "error": str(exc)}
    finally:
        db.close()
