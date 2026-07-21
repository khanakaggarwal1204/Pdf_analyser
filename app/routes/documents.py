from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import UploadedDocument

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.get("/")
async def get_documents(
    db: Session = Depends(get_db)
):
    documents = db.query(UploadedDocument).all()

    return [
        {
            "id": doc.id,
            "document_id": doc.document_id,
            "original_filename": doc.original_filename,
            "stored_filename": doc.stored_filename,
            "uploaded_at": doc.uploaded_at
        }
        for doc in documents
    ]


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    document = (
        db.query(UploadedDocument)
        .filter_by(document_id=document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully"
    }