from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.database.session import get_db
from app.models.chat import ActivityLog
from app.models.dataset import Dataset, MLRun
from app.models.resume import Resume
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/overview")
def admin_overview(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar()
    total_datasets = db.query(func.count(Dataset.id)).scalar()
    total_resumes = db.query(func.count(Resume.id)).scalar()
    total_ml_runs = db.query(func.count(MLRun.id)).scalar()

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    new_users_7d = db.query(func.count(User.id)).filter(User.created_at >= seven_days_ago).scalar()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "new_users_7d": new_users_7d,
        "total_datasets_uploaded": total_datasets,
        "total_resumes_analyzed": total_resumes,
        "total_ml_runs": total_ml_runs,
    }


@router.get("/users")
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": u.id, "full_name": u.full_name, "email": u.email,
            "role": u.role.value, "is_active": u.is_active,
            "is_email_verified": u.is_email_verified, "created_at": u.created_at,
            "last_login_at": u.last_login_at,
        }
        for u in users
    ]


@router.patch("/users/{user_id}/toggle-active")
def toggle_user_active(user_id: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = not user.is_active
        db.commit()
    return {"id": user_id, "is_active": user.is_active if user else None}


@router.get("/activity-logs")
def activity_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": log.id, "user_id": log.user_id, "action": log.action,
            "endpoint": log.endpoint, "status_code": log.status_code,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@router.get("/api-usage")
def api_usage_analytics(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = (
        db.query(ActivityLog.action, func.count(ActivityLog.id))
        .group_by(ActivityLog.action)
        .order_by(func.count(ActivityLog.id).desc())
        .limit(20)
        .all()
    )
    return [{"action": action, "count": count} for action, count in rows]
