from pypdf import PdfReader
from docx import Document
from typing import IO

def extract_text_from_file(file: IO, filename: str) -> str:
    """
    Extract text from PDF or DOCX file (no OCR).
    """
    text = ""

    if filename.lower().endswith(".pdf"):
        reader = PdfReader(file)
        for page in reader.pages:
            t = page.extract_text() or ""
            text += t + "\n"

    elif filename.lower().endswith(".docx"):
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"

    else:
        raise ValueError("Unsupported file type")

    return text
