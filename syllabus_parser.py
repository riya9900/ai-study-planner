import io
import os
from typing import Dict, Any, Tuple
import pypdf
import docx
from pptx import Presentation

def extract_text_from_upload(uploaded_file) -> Tuple[str, Dict[str, Any]]:
    """Extracts text content and metadata from an uploaded file (PDF, PPTX, DOCX, TXT).

    Args:
        uploaded_file: Streamlit UploadedFile object or file-like object with .name and .read().

    Returns:
        Tuple of (extracted_text, metadata_dict)
    """
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()
    
    extracted_text = ""
    metadata = {
        "filename": filename,
        "extension": ext,
        "page_or_slide_count": 0,
        "word_count": 0,
        "status": "success",
        "error": None
    }

    try:
        # 1. PDF Files
        if ext == ".pdf":
            reader = pypdf.PdfReader(uploaded_file)
            metadata["page_or_slide_count"] = len(reader.pages)
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(f"--- [Page {i+1}] ---\n{text.strip()}")
            extracted_text = "\n\n".join(pages_text)

        # 2. PowerPoint Presentations (PPTX)
        elif ext in [".pptx", ".ppt"]:
            prs = Presentation(uploaded_file)
            metadata["page_or_slide_count"] = len(prs.slides)
            slides_text = []
            for i, slide in enumerate(prs.slides):
                slide_content = []
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_content.append(shape.text.strip())
                if slide_content:
                    slides_text.append(f"--- [Slide {i+1}] ---\n" + "\n".join(slide_content))
            extracted_text = "\n\n".join(slides_text)

        # 3. Word Documents (DOCX)
        elif ext in [".docx", ".doc"]:
            doc = docx.Document(uploaded_file)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            
            # Also capture table text if present
            table_texts = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        table_texts.append(" | ".join(row_text))
            
            combined = paragraphs + (["--- Tables ---"] + table_texts if table_texts else [])
            metadata["page_or_slide_count"] = len(paragraphs)
            extracted_text = "\n\n".join(combined)

        # 4. Plain Text or Markdown
        elif ext in [".txt", ".md"]:
            content = uploaded_file.read()
            if isinstance(content, bytes):
                extracted_text = content.decode("utf-8", errors="replace")
            else:
                extracted_text = str(content)
            metadata["page_or_slide_count"] = 1

        else:
            raise ValueError(f"Unsupported file format '{ext}'. Please upload a PDF, PPTX, DOCX, or TXT file.")

        extracted_text = extracted_text.strip()
        if not extracted_text:
            raise ValueError("The uploaded file was empty or no readable text could be extracted.")

        metadata["word_count"] = len(extracted_text.split())
        return extracted_text, metadata

    except Exception as err:
        metadata["status"] = "error"
        metadata["error"] = str(err)
        return "", metadata

if __name__ == "__main__":
    print("Syllabus parser module ready.")

