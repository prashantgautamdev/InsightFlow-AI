import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.chat import ChatSession, ChatMessage
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.data import ChatMessageRequest, ChatMessageOut
from app.services.rag_chat_service import query_dataset_rag

router = APIRouter(prefix="/chat", tags=["AI Dataset Chat Assistant"])


@router.post("/message", response_model=ChatMessageOut)
def send_chat_message(
    payload: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = None
    if payload.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == payload.session_id, ChatSession.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

    dataset = None
    if payload.dataset_id:
        dataset = db.query(Dataset).filter(
            Dataset.id == payload.dataset_id, Dataset.user_id == current_user.id
        ).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

    if not session:
        session = ChatSession(
            user_id=current_user.id,
            dataset_id=dataset.id if dataset else None,
            title=payload.message[:60],
            chroma_collection_name=f"dataset_{dataset.id}" if dataset else None,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    user_msg = ChatMessage(session_id=session.id, role="user", content=payload.message)
    db.add(user_msg)
    db.commit()

    eda_report = dataset.eda_report if dataset else {}
    collection_name = session.chroma_collection_name or ""
    answer = query_dataset_rag(collection_name, payload.message, eda_report, fallback_only=not collection_name)

    assistant_msg = ChatMessage(session_id=session.id, role="assistant", content=answer)
    db.add(assistant_msg)
    db.commit()

    return ChatMessageOut(session_id=session.id, role="assistant", content=answer)


@router.get("/sessions/{session_id}/history")
def get_chat_history(session_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at}
        for m in sorted(session.messages, key=lambda m: m.created_at)
    ]
