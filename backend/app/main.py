from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os
import shutil

app = FastAPI(
    title="CampusConnect AI Backend",
    description="Backend APIs for CampusConnect AI document assistant",
    version="1.0"
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
    return {
        "question": data.question,
        "answer": "AI module not connected yet."
    }

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):

    if not file.filename:
        return {"error": "No file selected."}

    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully!",
        "filename": file.filename
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