import os

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.data import NLQueryRequest, NLQueryResponse
from app.services.nl_query_service import generate_pandas_code, execute_pandas_code, explain_result

router = APIRouter(prefix="/nl-query", tags=["Natural Language Query"])


@router.post("", response_model=NLQueryResponse)
def nl_query(
    payload: NLQueryRequest,
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

    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    code = generate_pandas_code(payload.question, df.columns.tolist(), dtypes)
    result = execute_pandas_code(df, code)
    explanation = explain_result(payload.question, code, result)

    return NLQueryResponse(
        question=payload.question,
        generated_code=code,
        result_preview=result,
        explanation=explanation,
    )
