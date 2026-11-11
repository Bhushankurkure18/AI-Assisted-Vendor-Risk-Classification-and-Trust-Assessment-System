"""
Plain text extractor with robust encoding detection and whitespace normalization.
"""
import re
from typing import List, Tuple
from backend.app.schemas.document import DocumentPageExtract


def extract_txt(filepath: str) -> Tuple[List[DocumentPageExtract], str, str, int]:
    """
    Extracts text from a plain .txt file, attempting UTF-8 with latin-1 fallback.

    Returns:
        (pages, full_text, extraction_method, page_count)
    """
    raw_content = ""
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                raw_content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    # Normalize whitespace: collapse 3+ consecutive newlines to 2, strip trailing spaces
    cleaned = re.sub(r"[ \t]+", " ", raw_content)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    char_count = len(cleaned)
    pages = [
        DocumentPageExtract(
            page_number=1,
            text=cleaned,
            char_count=char_count,
            has_text=char_count > 0,
            used_ocr=False
        )
    ]
    return pages, cleaned, "PLAIN_TEXT", 1

