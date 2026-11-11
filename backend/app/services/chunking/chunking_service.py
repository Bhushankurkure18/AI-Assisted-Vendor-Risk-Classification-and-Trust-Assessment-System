"""
Token-Aware Chunking Service with Sentence Preservation and Canonical Database Persistence.
"""
import re
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.document import Document
from backend.app.models.chunk import DocumentChunk
from backend.app.models.vendor import Vendor
from backend.app.services.chunking.text_cleaner import TextCleaner
from backend.app.services.chunking.deduplication import DeduplicationHandler

logger = logging.getLogger(__name__)

# Initialize tiktoken tokenizer if available
try:
    import tiktoken
    tokenizer = tiktoken.get_encoding("cl100k_base")
except Exception:
    tokenizer = None


class ChunkingService:
    """
    Splits cleaned text into semantic chunks with token constraints,
    sentence boundary preservation, page attribution, and database storage.
    """

    @staticmethod
    def count_tokens(text: str) -> int:
        """
        Counts tokens using tiktoken (cl100k_base) or fallback approximation (~4 chars/token).
        """
        if not text:
            return 0
        if tokenizer:
            try:
                return len(tokenizer.encode(text))
            except Exception:
                pass
        return max(1, len(text.split()))

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """
        Splits text along sentence and paragraph boundaries to prevent mid-sentence truncation.
        """
        # Split on double newlines (paragraphs) or sentence ending punctuation followed by space
        raw_parts = re.split(r"(?<=[.!?])\s+|\n\n+", text)
        sentences = [p.strip() for p in raw_parts if p.strip()]
        return sentences

    @classmethod
    def chunk_document_text(
        cls,
        document_id: str,
        vendor_id: int,
        filename: str,
        pages_data: Optional[List[Dict[str, Any]]] = None,
        raw_text: Optional[str] = None,
        chunk_size_tokens: Optional[int] = None,
        chunk_overlap_tokens: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates token-bounded chunks preserving page numbers, section headers, and sentence boundaries.
        """
        target_size = chunk_size_tokens or settings.CHUNK_SIZE_TOKENS
        overlap = chunk_overlap_tokens or settings.CHUNK_OVERLAP_TOKENS

        chunks: List[Dict[str, Any]] = []
        chunk_counter = 0

        # If page-by-page data is available, process page by page to guarantee exact page attribution
        if pages_data and len(pages_data) > 0:
            units = pages_data
        else:
            # Fallback to single unit
            cleaned = TextCleaner.clean_text(raw_text or "")
            units = [{"page_number": 1, "text": cleaned}]

        current_section = "General"

        for unit in units:
            page_num = unit.get("page_number", 1)
            page_text = TextCleaner.clean_text(unit.get("text", ""))
            if not page_text:
                continue

            sentences = cls.split_into_sentences(page_text)
            current_chunk_sentences: List[str] = []
            current_tokens = 0

            for sent in sentences:
                # Check for section header in sentence
                detected_heading = TextCleaner.detect_heading(sent)
                if detected_heading:
                    current_section = detected_heading

                sent_tokens = cls.count_tokens(sent)

                # If adding sentence exceeds target size and we already have content
                if current_tokens + sent_tokens > target_size and current_chunk_sentences:
                    chunk_text = " ".join(current_chunk_sentences)
                    content_hash = DeduplicationHandler.compute_chunk_hash(chunk_text)
                    chunk_id = f"chk_{document_id}_{chunk_counter:04d}"

                    chunks.append({
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "vendor_id": vendor_id,
                        "filename": filename,
                        "page_number": page_num,
                        "section": current_section,
                        "chunk_index": chunk_counter,
                        "token_count": current_tokens,
                        "content_hash": content_hash,
                        "text": chunk_text,
                    })
                    chunk_counter += 1

                    # Retain overlap sentences from tail
                    overlap_sentences: List[str] = []
                    overlap_tokens = 0
                    for prev_sent in reversed(current_chunk_sentences):
                        p_toks = cls.count_tokens(prev_sent)
                        if overlap_tokens + p_toks <= overlap:
                            overlap_sentences.insert(0, prev_sent)
                            overlap_tokens += p_toks
                        else:
                            break

                    current_chunk_sentences = overlap_sentences + [sent]
                    current_tokens = overlap_tokens + sent_tokens
                else:
                    current_chunk_sentences.append(sent)
                    current_tokens += sent_tokens

            # Add remaining sentences for this page
            if current_chunk_sentences:
                chunk_text = " ".join(current_chunk_sentences)
                content_hash = DeduplicationHandler.compute_chunk_hash(chunk_text)
                chunk_id = f"chk_{document_id}_{chunk_counter:04d}"

                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "vendor_id": vendor_id,
                    "filename": filename,
                    "page_number": page_num,
                    "section": current_section,
                    "chunk_index": chunk_counter,
                    "token_count": current_tokens,
                    "content_hash": content_hash,
                    "text": chunk_text,
                })
                chunk_counter += 1

        return chunks

    @classmethod
    def chunk_and_persist(
        cls,
        db: Session,
        document_id: str,
        vendor_id: Optional[int] = None,
        chunk_size_tokens: Optional[int] = None,
        chunk_overlap_tokens: Optional[int] = None,
    ) -> List[DocumentChunk]:
        """
        Chunks an extracted document and persists chunks to PostgreSQL / SQLite.
        Deletes any pre-existing chunks for the document to ensure idempotency.
        """
        query = db.query(Document).filter(Document.document_id == document_id)
        if vendor_id is not None:
            query = query.filter(Document.vendor_id == vendor_id)

        doc = query.first()
        if not doc:
            raise LookupError(f"Document {document_id} not found.")

        if not doc.extracted_text:
            raise ValueError(f"Document {document_id} has no extracted text. Process document first.")

        # Reconstruct page units from extracted text or page markers
        pages_data = []
        raw = doc.extracted_text
        if "--- Page " in raw:
            parts = re.split(r"--- Page (\d+) ---\n", raw)
            # parts has format: ['', '1', 'page 1 text', '2', 'page 2 text']
            for i in range(1, len(parts), 2):
                p_num = int(parts[i])
                p_text = parts[i + 1] if i + 1 < len(parts) else ""
                pages_data.append({"page_number": p_num, "text": p_text})
        else:
            pages_data.append({"page_number": 1, "text": raw})

        chunk_dicts = cls.chunk_document_text(
            document_id=doc.document_id,
            vendor_id=doc.vendor_id,
            filename=doc.original_filename,
            pages_data=pages_data,
            raw_text=raw,
            chunk_size_tokens=chunk_size_tokens,
            chunk_overlap_tokens=chunk_overlap_tokens,
        )

        # Clear existing chunks for this document
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
        db.commit()

        # Insert canonical chunks
        db_chunks = []
        for d in chunk_dicts:
            chk = DocumentChunk(
                chunk_id=d["chunk_id"],
                document_id=d["document_id"],
                vendor_id=d["vendor_id"],
                original_filename=d["filename"],
                page_number=d["page_number"],
                section=d.get("section", "General"),
                chunk_index=d["chunk_index"],
                token_count=d["token_count"],
                content_hash=d["content_hash"],
                chunk_text=d["text"],
            )
            db.add(chk)
            db_chunks.append(chk)

        db.commit()
        for chk in db_chunks:
            db.refresh(chk)

        return db_chunks

