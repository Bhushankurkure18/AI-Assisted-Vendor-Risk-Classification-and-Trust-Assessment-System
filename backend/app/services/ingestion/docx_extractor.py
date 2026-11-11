"""
DOCX text and tabular data extractor.
"""
import logging
from typing import List, Tuple
import docx
from backend.app.schemas.document import DocumentPageExtract

logger = logging.getLogger(__name__)


def extract_docx(filepath: str) -> Tuple[List[DocumentPageExtract], str, str, int]:
    """
    Extracts text paragraphs and structured tables from a .docx document.

    Returns:
        (pages, full_text, extraction_method, page_count)
    """
    doc = docx.Document(filepath)
    content_lines: List[str] = []

    # Extract core properties if present
    try:
        props = doc.core_properties
        header_meta = []
        if props.title:
            header_meta.append(f"Title: {props.title}")
        if props.author:
            header_meta.append(f"Author: {props.author}")
        if header_meta:
            content_lines.append(f"[{'; '.join(header_meta)}]\n")
    except Exception:
        pass

    # Extract paragraphs
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt:
            content_lines.append(txt)

    # Extract tables
    for t_idx, table in enumerate(doc.tables, start=1):
        table_lines = [f"\n[Table {t_idx}]"]
        for row in table.rows:
            cell_texts = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            table_lines.append(" | ".join(cell_texts))
        if len(table_lines) > 1:
            content_lines.append("\n".join(table_lines))

    combined_text = "\n\n".join(content_lines).strip()
    char_count = len(combined_text)

    pages = [
        DocumentPageExtract(
            page_number=1,
            text=combined_text,
            char_count=char_count,
            has_text=char_count > 0,
            used_ocr=False
        )
    ]

    return pages, combined_text, "PYTHON_DOCX", 1

