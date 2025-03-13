import os
import logging
import fitz  # PyMuPDF for PDF parsing
from django.core.files.storage import default_storage

# Configure logger
logger = logging.getLogger(__name__)

def save_uploaded_file(uploaded_file, folder):
    """Saves the uploaded file and returns the full path"""
    file_path = default_storage.save(f"{folder}/{uploaded_file.name}", uploaded_file)
    return os.path.join(default_storage.location, file_path)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF using PyMuPDF"""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}", exc_info=True)
    return text.strip()
