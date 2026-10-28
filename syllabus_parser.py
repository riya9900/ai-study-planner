import io
import os
import time
from typing import Dict, Any, Tuple
from dotenv import load_dotenv
import pypdf
import docx
from pptx import Presentation

# Load environment variables
load_dotenv()

def _ocr_with_gemini(file_bytes: bytes, mime_type: str = "application/pdf") -> str:
    """Uses Google Gemini Multimodal Vision to extract text from scanned/image-based documents."""
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "This document appears to be a scanned or image-based PDF. "
            "To OCR scanned documents, please ensure your GEMINI_API_KEY is configured in .env."
        )

    client = genai.Client(api_key=api_key)
    part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
    prompt = (
        "You are an expert academic document transcriber. "
        "Extract all syllabus units, course titles, module topics, learning outcomes, chapters, "
        "and detailed headings from this scanned document. "
        "Preserve the exact unit names, numbers, and technical terms as written."
    )

    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest"]
    last_err = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[part, prompt]
            )
            if response and response.text and response.text.strip():
                return response.text.strip()
        except Exception as e:
            last_err = e
            time.sleep(1.5)
            continue

    raise RuntimeError(f"AI OCR failed to extract text from scanned document: {last_err}")


def extract_text_from_upload(uploaded_file) -> Tuple[str, Dict[str, Any]]:
    """Extracts text content and metadata from an uploaded file (PDF, PPTX, DOCX, TXT, Images).
    Automatically falls back to Gemini Multimodal AI OCR if the PDF is scanned or image-based.

    Args:
        uploaded_file: Streamlit UploadedFile or file-like object with .name, .read(), and .seek().

    Returns:
        Tuple of (extracted_text, metadata_dict)
    """
    filename = getattr(uploaded_file, "name", "uploaded_document")
    ext = os.path.splitext(filename)[1].lower()

    # Read bytes safely
    file_bytes = uploaded_file.read()
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    metadata = {
        "filename": filename,
        "extension": ext,
        "page_or_slide_count": 0,
        "word_count": 0,
        "extraction_method": "digital_text",
        "status": "success",
        "error": None
    }

    try:
        extracted_text = ""

        # -----------------------------------------------------
        # 1. PDF Files (Digital text first, AI OCR fallback)
        # -----------------------------------------------------
        if ext == ".pdf":
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            metadata["page_or_slide_count"] = len(reader.pages)
            pages_text = []

            for i, page in enumerate(reader.pages):
                txt = page.extract_text() or ""
                if txt.strip():
                    pages_text.append(f"--- [Page {i+1}] ---\n{txt.strip()}")

            raw_combined = "\n\n".join(pages_text).strip()

            # Check if digital extraction succeeded with sufficient content
            if len(raw_combined) >= 50:
                extracted_text = raw_combined
                metadata["extraction_method"] = "digital_pdf_text"
            else:
                # Scanned or image-based PDF detected -> Use AI Multimodal OCR
                metadata["extraction_method"] = "scanned_pdf_ai_ocr"
                extracted_text = _ocr_with_gemini(file_bytes, mime_type="application/pdf")

        # -----------------------------------------------------
        # 2. PowerPoint Presentations (PPTX, PPT)
        # -----------------------------------------------------
        elif ext in [".pptx", ".ppt"]:
            prs = Presentation(io.BytesIO(file_bytes))
            metadata["page_or_slide_count"] = len(prs.slides)
            slides_text = []
            for i, slide in enumerate(prs.slides):
                slide_content = []
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_content.append(shape.text.strip())
                if slide_content:
                    slides_text.append(f"--- [Slide {i+1}] ---\n" + "\n".join(slide_content))
            extracted_text = "\n\n".join(slides_text).strip()
            metadata["extraction_method"] = "pptx_slides"

        # -----------------------------------------------------
        # 3. Word Documents (DOCX, DOC)
        # -----------------------------------------------------
        elif ext in [".docx", ".doc"]:
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            
            table_texts = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        table_texts.append(" | ".join(row_text))

            combined = paragraphs + (["--- Tables ---"] + table_texts if table_texts else [])
            metadata["page_or_slide_count"] = len(paragraphs)
            extracted_text = "\n\n".join(combined).strip()
            metadata["extraction_method"] = "docx_document"

        # -----------------------------------------------------
        # 4. Images (PNG, JPG, JPEG)
        # -----------------------------------------------------
        elif ext in [".png", ".jpg", ".jpeg"]:
            mime_type = "image/png" if ext == ".png" else "image/jpeg"
            metadata["page_or_slide_count"] = 1
            metadata["extraction_method"] = "image_ai_ocr"
            extracted_text = _ocr_with_gemini(file_bytes, mime_type=mime_type)

        # -----------------------------------------------------
        # 5. Plain Text or Markdown
        # -----------------------------------------------------
        elif ext in [".txt", ".md"]:
            if isinstance(file_bytes, bytes):
                extracted_text = file_bytes.decode("utf-8", errors="replace").strip()
            else:
                extracted_text = str(file_bytes).strip()
            metadata["page_or_slide_count"] = 1
            metadata["extraction_method"] = "plain_text"

        else:
            raise ValueError(f"Unsupported file format '{ext}'. Please upload a PDF, PPTX, DOCX, TXT, or Image file.")

        extracted_text = extracted_text.strip()
        if not extracted_text:
            raise ValueError(
                "No readable text or syllabus content could be extracted from this file. "
                "Please verify the file contains syllabus information or upload a clear copy."
            )

        metadata["word_count"] = len(extracted_text.split())
        return extracted_text, metadata

    except Exception as err:
        metadata["status"] = "error"
        metadata["error"] = str(err)
        return "", metadata

if __name__ == "__main__":
    import sys
    print("Testing syllabus_parser with Doc1.pdf...")
    with open("Doc1.pdf", "rb") as f:
        txt, meta = extract_text_from_upload(f)
    print("Status:", meta["status"])
    print("Method:", meta["extraction_method"])
    print("Words:", meta["word_count"])
    print("Preview:\n", txt[:300])
