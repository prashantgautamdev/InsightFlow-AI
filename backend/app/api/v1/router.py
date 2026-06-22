from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, resume, career, datasets, nl_query, automl, chat, reports, admin,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(resume.router)
api_router.include_router(career.router)
api_router.include_router(datasets.router)
api_router.include_router(nl_query.router)
api_router.include_router(automl.router)
api_router.include_router(chat.router)
api_router.include_router(reports.router)
api_router.include_router(admin.router)
