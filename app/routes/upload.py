import os
import shutil
import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import UPLOAD_FOLDER
from app.database import get_db
from app.models.models import UploadedDocument
from app.services.file_service import extract_text

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX and TXT files are allowed."
        )

    document_id = str(uuid.uuid4())

    stored_filename = f"{document_id}{extension}"

    filepath = os.path.join(
        UPLOAD_FOLDER,
        stored_filename
    )

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = UploadedDocument(
        document_id=document_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        filepath=filepath
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Extract text (used for future RAG processing)
    text = extract_text(filepath)

    return {
        "message": "File uploaded successfully",
        "document_id": document.document_id,
        "filename": document.stored_filename
    }