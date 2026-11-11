"""
PyMuPDF PDF Text & OCR Extractor.
"""
import io
import logging
from typing import List, Tuple
from PIL import Image
import fitz  # PyMuPDF
from backend.app.schemas.document import DocumentPageExtract
from backend.app.services.ingestion.ocr_service import ocr_service

logger = logging.getLogger(__name__)

# Threshold below which a page is considered scanned or image-dominant
MIN_TEXT_CHARS_THRESHOLD = 40


def extract_pdf(filepath: str) -> Tuple[List[DocumentPageExtract], str, str, int]:
    """
    Extracts text from a PDF file page by page using PyMuPDF.
    Detects scanned pages and falls back to OCR where available.

    Returns:
        (pages, full_text, extraction_method, page_count)
    """
    doc = fitz.open(filepath)
    page_count = len(doc)
    pages: List[DocumentPageExtract] = []
    full_text_parts: List[str] = []
    used_any_ocr = False

    try:
        for idx in range(page_count):
            page = doc[idx]
            page_num = idx + 1
            text = page.get_text("text").strip()
            char_count = len(text)
            has_text = char_count >= MIN_TEXT_CHARS_THRESHOLD
            used_ocr = False

            # Fallback to OCR if page has little/no text and OCR is available
            if not has_text and ocr_service.is_available():
                try:
                    pix = page.get_pixmap(dpi=200)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    ocr_text = ocr_service.extract_text_from_image(img)
                    if ocr_text:
                        text = ocr_text
                        char_count = len(text)
                        has_text = char_count > 0
                        used_ocr = True
                        used_any_ocr = True
                except Exception as exc:
                    logger.warning(f"OCR failed for page {page_num} of {filepath}: {exc}")

            page_extract = DocumentPageExtract(
                page_number=page_num,
                text=text,
                char_count=char_count,
                has_text=has_text,
                used_ocr=used_ocr,
            )
            pages.append(page_extract)
            if text:
                full_text_parts.append(f"--- Page {page_num} ---\n{text}")

        method = "PYMUPDF+OCR" if used_any_ocr else "PYMUPDF"
        combined_text = "\n\n".join(full_text_parts)
        return pages, combined_text, method, page_count
    finally:
        doc.close()

