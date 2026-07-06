import os
import uuid
import json
from fpdf import FPDF
from docx import Document
from app.core.logger import system_logger

class ApplicationPackageGenerator:
    STORAGE_DIR = "storage/packages"

    @classmethod
    def ensure_storage(cls):
        if not os.path.exists(cls.STORAGE_DIR):
            os.makedirs(cls.STORAGE_DIR)

    @classmethod
    def generate_pdf(cls, content: str, filename: str) -> str:
        cls.ensure_storage()
        filepath = os.path.join(cls.STORAGE_DIR, filename)
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            # Replace unsupported characters for basic FPDF
            safe_content = content.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, safe_content)
            pdf.output(filepath)
            return filepath
        except Exception as e:
            system_logger.error(f"Failed to generate PDF {filename}: {e}")
            return ""

    @classmethod
    def generate_docx(cls, content: str, filename: str) -> str:
        cls.ensure_storage()
        filepath = os.path.join(cls.STORAGE_DIR, filename)
        try:
            doc = Document()
            doc.add_paragraph(content)
            doc.save(filepath)
            return filepath
        except Exception as e:
            system_logger.error(f"Failed to generate DOCX {filename}: {e}")
            return ""

    @classmethod
    def save_summary(cls, data: dict, filename: str) -> str:
        cls.ensure_storage()
        filepath = os.path.join(cls.STORAGE_DIR, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return filepath
        except Exception as e:
            system_logger.error(f"Failed to generate JSON {filename}: {e}")
            return ""

    @classmethod
    def create_package(cls, optimized_resume: str, cover_letter: str, summary_data: dict) -> dict:
        package_id = str(uuid.uuid4())[:8]
        
        resume_pdf = cls.generate_pdf(optimized_resume, f"optimized_resume_{package_id}.pdf")
        resume_docx = cls.generate_docx(optimized_resume, f"optimized_resume_{package_id}.docx")
        
        cl_pdf = cls.generate_pdf(cover_letter, f"cover_letter_{package_id}.pdf")
        cl_docx = cls.generate_docx(cover_letter, f"cover_letter_{package_id}.docx")
        
        summary_file = cls.save_summary(summary_data, f"summary_{package_id}.json")
        
        return {
            "resume_pdf": resume_pdf,
            "resume_docx": resume_docx,
            "cover_letter_pdf": cl_pdf,
            "cover_letter_docx": cl_docx,
            "summary_json": summary_file
        }
