import os
import pdfplumber
import docx
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(layout=True)  # layout=True helps with columns
                if page_text:
                    text += page_text + "\n"
                
                # Also try extracting tables to preserve tabular data structures
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            text += " | ".join([str(cell) for cell in row if cell]) + "\n"
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {e}")
        raise ValueError(f"Failed to read PDF: {e}")
    return text.strip()

def extract_text_from_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
            
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join([cell.text for cell in row.cells])
                text += row_text + "\n"
    except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {e}")
        raise ValueError(f"Failed to read DOCX: {e}")
    return text.strip()

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        # Note: python-docx only supports .docx, .doc might fail, but let's try
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
