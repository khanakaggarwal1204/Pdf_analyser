from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import ChatHistory
from app.models.schemas import ChatRequest, ChatResponse, Source
from app.services.rag_service import ask_rag

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    
    rag_result = ask_rag(
    question=request.question,
    session_id=request.session_id
)

    answer = rag_result["answer"]
    
    chat = ChatHistory(
        session_id=request.session_id,
        question=request.question,
        answer=answer
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return ChatResponse(
    answer=answer,
    sources=[
        Source(
            document=source["document"],
            page=source["page"]
        )
        for source in rag_result["sources"]
    ]
)

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .all()
    )

    return [
        {
            "question": chat.question,
            "answer": chat.answer
        }
        for chat in chats
    ]
