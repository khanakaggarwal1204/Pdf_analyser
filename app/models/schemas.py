from pydantic import BaseModel
from typing import List


# -------------------------
# Chat Schemas
# -------------------------

class ChatRequest(BaseModel):
    session_id: str
    question: str


class Source(BaseModel):
    document: str
    page: int


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


# -------------------------
# Upload Schema
# -------------------------

class UploadResponse(BaseModel):
    message: str
    document_id: int


# -------------------------
# Settings Schema
# -------------------------

class Settings(BaseModel):
    temperature: float
    chunk_size: int
    top_k: int