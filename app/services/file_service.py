from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_text(file_path: str) -> str:
    """
    Extract text from PDF, DOCX or TXT files.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".txt":
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    elif extension == ".pdf":
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

        return text

    elif extension == ".docx":
        document = Document(file_path)

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    else:
        raise ValueError("Unsupported file type.")