"""
CSV tabular extractor converting structured rows into semantic retrieval representations.
"""
import pandas as pd
from typing import List, Tuple
from backend.app.schemas.document import DocumentPageExtract


def extract_csv(filepath: str) -> Tuple[List[DocumentPageExtract], str, str, int]:
    """
    Extracts tabular data from CSV files and formats rows into semantic text representations.

    Returns:
        (pages, full_text, extraction_method, page_count)
    """
    df = pd.read_csv(filepath)
    lines: List[str] = [
        f"CSV Table: {len(df)} rows across {len(df.columns)} columns.",
        f"Columns: {', '.join(df.columns.tolist())}\n"
    ]

    for idx, row in df.iterrows():
        row_fields = [f"{col}: {val}" for col, val in row.items() if pd.notna(val)]
        lines.append(f"Row {idx + 1} -> {'; '.join(row_fields)}")

    combined_text = "\n".join(lines).strip()
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
    return pages, combined_text, "PANDAS_CSV", 1

