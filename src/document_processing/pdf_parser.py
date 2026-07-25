import fitz  # PyMuPDF
from typing import List, Dict, Any
import re

class PDFParser:
    """Parses PDF documents into page-level text objects while preserving structural metadata."""
    
    def extract_pages(self, pdf_path: str, doc_id: str, file_name: str) -> List[Dict[str, Any]]:
        """Extracts text page-by-page from a PDF document."""
        doc = fitz.open(pdf_path)
        extracted_pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            
            # Basic text cleaning: collapse extra spaces and clean invisible control chars
            cleaned_text = re.sub(r'[ \t]+', ' ', text)
            cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
            
            if cleaned_text:
                extracted_pages.append({
                    "doc_id": doc_id,
                    "file_name": file_name,
                    "page_number": page_num + 1,
                    "text": cleaned_text
                })
        doc.close()
        return extracted_pages
