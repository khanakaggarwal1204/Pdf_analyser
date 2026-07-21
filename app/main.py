from fastapi import FastAPI

from app.database import Base, engine
from app.models.models import ChatHistory, UploadedDocument
from app.routes.upload import router as upload_router

from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agentic RAG Backend",
    description="Backend for AI Document Chat System",
    version="1.0.0"
)


app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(documents_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to the Agentic RAG Backend!"
    }


@app.get("/health")
def health():
    return {
        "status": "running"
    }