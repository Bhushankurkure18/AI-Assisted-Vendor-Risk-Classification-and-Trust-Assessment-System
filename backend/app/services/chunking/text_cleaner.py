"""
Text Cleaning and Normalization Service for Phase 2.
Strips boilerplate headers and footers while strictly preserving tables, figures, and risk terminology.
"""
import re
from typing import Tuple, Optional


class TextCleaner:
    """
    Cleans and normalizes extracted text before chunking.
    """

    # Common document header/footer patterns
    HEADER_FOOTER_PATTERNS = [
        r"(?i)^\s*page\s+\d+\s+of\s+\d+\s*$",
        r"(?i)^\s*page\s+\d+\s*$",
        r"(?i)^\s*confidential\s*$",
        r"(?i)^\s*strictly\s+private\s+and\s+confidential\s*$",
        r"(?i)^\s*all\s+rights\s+reserved\s*$",
        r"(?i)^\s*draft\s*-\s*for\s+internal\s+use\s+only\s*$",
    ]

    # Section heading patterns
    HEADING_PATTERNS = [
        r"^(#{1,6}\s+.*)$",                                  # Markdown # Heading
        r"^([0-9]+(?:\.[0-9]+)*\s+[A-Z][A-Za-z0-9\s\-_]+)$", # 1.1 Section Title
        r"^(\[[A-Za-z0-9\s\-_]+\])$",                         # [Section Title]
        r"^([A-Z][A-Z0-9\s\-_]{3,50}:)$",                     # FINANCIAL AUDIT:
    ]

    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Normalizes whitespace and removes trivial repeating page boilerplate.
        Preserves tabular formatting and risk terms.
        """
        if not text:
            return ""

        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line_str = line.strip()
            # Check if line matches header/footer boilerplate
            is_boilerplate = any(re.match(p, line_str) for p in cls.HEADER_FOOTER_PATTERNS)
            if is_boilerplate:
                continue

            cleaned_lines.append(line)

        # Recombine and normalize consecutive newlines (max 2)
        combined = "\n".join(cleaned_lines)
        combined = re.sub(r"[ \t]+", " ", combined)
        combined = re.sub(r"\n{3,}", "\n\n", combined)
        return combined.strip()

    @classmethod
    def detect_heading(cls, line: str) -> Optional[str]:
        """
        Detects if a line represents a section heading.
        """
        line_clean = line.strip()
        if not line_clean or len(line_clean) > 80:
            return None

        for pattern in cls.HEADING_PATTERNS:
            match = re.match(pattern, line_clean)
            if match:
                return match.group(1).strip("# [] :")
        return None

