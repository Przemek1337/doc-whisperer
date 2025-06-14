import os
from typing import List, Dict
import PyPDF2
from docx import Document
from pathlib import Path

class FileHandler:

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        try:
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"[PDF] Failed to extract text from {file_path}: {e}")

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        try:
            docx_document = Document(file_path)
            text = ""
            for paragraph in docx_document.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"[DOCX] Failed to extract text from {file_path}: {e}")

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        try:
            with open(file_path, "rb") as txt_file:
                return txt_file.read()
        except Exception as e:
            raise Exception(f"[TXT] Failed to extract text from {file_path}: {e}")

    @classmethod
    def extract_text(cls, file_path: str) -> Dict[str, str]:
        file_extension = Path(file_path).suffix.lower() # load file extension and convert to lower

        extractors = {
            '.pdf' : cls.extract_text_from_pdf,
            '.docx' : cls.extract_text_from_docx,
            '.txt' : cls.extract_text_from_txt,
        }

        if file_extension not in extractors:
            raise ValueError(f"{file_extension} is not supported.")

        text = extractors[file_extension](file_path)

        return {
            "text" : text,
            "filename" : Path(file_path).name,
            "file_type" : file_extension,
        }