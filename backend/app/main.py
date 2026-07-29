import sys
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os
import shutil
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(Path(__file__).resolve().parents[2]))

from document_processor.read_pdf import extract_pdf_text
from document_processor.clean_text import clean_text
from document_processor.chunk_text import chunk_text
from document_processor.metadata import add_metadata
from document_processor.embeddings import create_embeddings
from document_processor.vector_store import store_embeddings
from document_processor.retriever import retrieve_chunks
from document_processor.generator import generate_answer

app = FastAPI(
    title="CampusConnect AI Backend",
    description="Backend APIs for CampusConnect AI document assistant",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)

class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "SmartDoc AI Backend Running 🚀"
    }

@app.get("/about")
def about():
    return {
        "project": "CampusConnect AI",
        "version": "1.0",
        "developer": "Team SmartDoc"
    }

@app.get("/contact")
def contact():
    return{
        "email": "smartdoc@gmail.com",
        "phone": "+91XXXXXXXXXX"
    }

@app.post("/ask")
def ask_question(data: Question):
    uploads = Path("uploads")
    pdf_files=sorted(
        uploads.glob("*.pdf"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    if not pdf_files:
        return {
            "error": "No PDF uploaded."
        }
    pdf_path=str(pdf_files[0])
    text = extract_pdf_text(pdf_path)

    if not text.strip():
        return{
            "error": "Could not extract text from uploaded PDF."
        }
    cleaned_text = clean_text(text)
    chunks = chunk_text(cleaned_text)

    chunk_data = add_metadata(chunks, pdf_path)
    embedded_chunks = create_embeddings(chunk_data)
    store_embeddings(embedded_chunks)
    results = retrieve_chunks(data.question)
    retrieved_chunks = results.get("documents",[[]])[0]

    if not retrieved_chunks:
        return {
            "question": data.question,
            "answer":"No relevant information found in the uploaded document."
        }

    answer = generate_answer(data.question, retrieved_chunks)
    return {
        "question": data.question,
        "answer": answer
    }

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):

    if not file.filename:
        return {"error": "No file selected."}
    file_path=Path("uploads")/file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully!",
        "filename": file_path.name
    }

@app.get("/documents")
def list_documents():

    files = os.listdir("uploads")

    return {
        "documents": files
    }

@app.delete("/delete/{filename}")
def delete_document(filename: str):

    path = f"uploads/{filename}"

    if os.path.exists(path):

        os.remove(path)

        return {
            "message": f"{filename} deleted successfully."
        }

    return {
        "message": "File not found."
    }

@app.get("/health")
def health():
    return {
        "status": "Running"
    }