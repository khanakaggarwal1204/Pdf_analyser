import os


UPLOAD_FOLDER = "uploads"


MAX_FILE_SIZE = 50 * 1024 * 1024


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}


DEFAULT_TEMPERATURE = 0.2
DEFAULT_CHUNK_SIZE = 500
DEFAULT_TOP_K = 5