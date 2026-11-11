"""
Document Processor coordinator for ingestion, validation, hashing, and extraction.
"""
import os
import re
import uuid
import hashlib
import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.document import Document
from backend.app.models.vendor import Vendor
from backend.app.schemas.document import DocumentProcessResponse, DocumentPageExtract
from backend.app.services.ingestion.pdf_extractor import extract_pdf
from backend.app.services.ingestion.docx_extractor import extract_docx
from backend.app.services.ingestion.txt_extractor import extract_txt
from backend.app.services.ingestion.csv_extractor import extract_csv

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Validates, securely stores, hashes, and extracts content from vendor documents.
    """

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Removes path traversal characters and unsafe symbols from filenames.
        """
        base = os.path.basename(filename)
        # Strip null bytes and directory separators
        clean = re.sub(r"[^\w\.\-\_]", "_", base)
        return clean or "unnamed_document"

    @staticmethod
    def compute_sha256(content: bytes) -> str:
        """
        Computes SHA-256 hexadecimal digest for raw bytes.
        """
        hasher = hashlib.sha256()
        hasher.update(content)
        return hasher.hexdigest()

    @classmethod
    def validate_upload(cls, filename: str, content: bytes) -> Tuple[str, str]:
        """
        Validates file size, extension, and non-empty payload.
        Returns (clean_filename, extension).
        Raises ValueError on validation failure.
        """
        if not content or len(content) == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")

        if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
            max_mb = settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
            raise ValueError(f"File size exceeds maximum allowed limit of {max_mb:.1f} MB.")

        clean_name = cls.sanitize_filename(filename)
        _, ext = os.path.splitext(clean_name)
        ext = ext.lower()

        if ext not in settings.SUPPORTED_EXTENSIONS:
            allowed = ", ".join(settings.SUPPORTED_EXTENSIONS)
            raise ValueError(f"Unsupported file extension '{ext}'. Supported formats: {allowed}")

        return clean_name, ext

    @classmethod
    def store_file(cls, vendor_id: int, document_id: str, clean_filename: str, content: bytes) -> str:
        """
        Saves uploaded file into vendor directory under data/uploads/{vendor_id}/
        """
        vendor_dir = os.path.join(settings.UPLOAD_DIR, str(vendor_id))
        os.makedirs(vendor_dir, exist_ok=True)

        stored_name = f"{document_id}_{clean_filename}"
        stored_path = os.path.join(vendor_dir, stored_name)

        with open(stored_path, "wb") as f:
            f.write(content)

        return os.path.abspath(stored_path)

    @classmethod
    def check_duplicate(cls, db: Session, vendor_id: int, content_hash: str) -> Optional[Document]:
        """
        Checks if a document with the same content hash already exists for this vendor.
        """
        return db.query(Document).filter(
            Document.vendor_id == vendor_id,
            Document.content_hash == content_hash
        ).first()

    @classmethod
    def ingest_document(
        cls,
        db: Session,
        vendor_id: int,
        filename: str,
        content: bytes,
        auto_process: bool = True
    ) -> Document:
        """
        Ingests a document: validates, checks vendor existence, saves to disk,
        registers in DB, and optionally triggers extraction.
        """
        # Verify vendor exists
        vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
        if not vendor:
            raise LookupError(f"Vendor with id {vendor_id} does not exist.")

        clean_name, ext = cls.validate_upload(filename, content)
        content_hash = cls.compute_sha256(content)

        # Check exact duplicate
        existing = cls.check_duplicate(db, vendor_id, content_hash)
        if existing:
            logger.info(f"Duplicate document detected for vendor {vendor_id} (doc_id={existing.document_id})")
            return existing

        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        stored_path = cls.store_file(vendor_id, document_id, clean_name, content)

        doc_record = Document(
            document_id=document_id,
            vendor_id=vendor_id,
            original_filename=clean_name,
            stored_filepath=stored_path,
            file_type=ext.lstrip("."),
            file_size=len(content),
            content_hash=content_hash,
            processing_status="PENDING",
            page_count=1,
            extraction_method=None,
            extracted_text=None,
            error_message=None
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        if auto_process:
            cls.process_document(db, doc_record.document_id)
            db.refresh(doc_record)

        return doc_record

    @classmethod
    def process_document(cls, db: Session, document_id: str) -> DocumentProcessResponse:
        """
        Executes text extraction for an uploaded document and updates DB record.
        """
        doc = db.query(Document).filter(Document.document_id == document_id).first()
        if not doc:
            raise LookupError(f"Document {document_id} not found.")

        if not os.path.exists(doc.stored_filepath):
            doc.processing_status = "FAILED"
            doc.error_message = f"Stored file not found on disk at {doc.stored_filepath}"
            db.commit()
            raise FileNotFoundError(doc.error_message)

        ext = f".{doc.file_type.lower()}"
        try:
            if ext == ".pdf":
                pages, full_text, method, page_count = extract_pdf(doc.stored_filepath)
            elif ext == ".docx":
                pages, full_text, method, page_count = extract_docx(doc.stored_filepath)
            elif ext == ".txt":
                pages, full_text, method, page_count = extract_txt(doc.stored_filepath)
            elif ext == ".csv":
                pages, full_text, method, page_count = extract_csv(doc.stored_filepath)
            else:
                raise ValueError(f"No extractor registered for file type '{ext}'")

            doc.page_count = page_count
            doc.extraction_method = method
            doc.extracted_text = full_text
            doc.processing_status = "PROCESSED"
            doc.error_message = None
            db.commit()

            return DocumentProcessResponse(
                document_id=doc.document_id,
                vendor_id=doc.vendor_id,
                original_filename=doc.original_filename,
                file_type=doc.file_type,
                processing_status=doc.processing_status,
                page_count=doc.page_count,
                extraction_method=doc.extraction_method,
                total_characters=len(full_text),
                pages=pages,
                error_message=None
            )

        except Exception as exc:
            logger.error(f"Error processing document {document_id}: {exc}", exc_info=True)
            doc.processing_status = "FAILED"
            doc.error_message = str(exc)
            db.commit()
            return DocumentProcessResponse(
                document_id=doc.document_id,
                vendor_id=doc.vendor_id,
                original_filename=doc.original_filename,
                file_type=doc.file_type,
                processing_status="FAILED",
                page_count=doc.page_count or 1,
                extraction_method=doc.extraction_method or "UNKNOWN",
                total_characters=0,
                pages=[],
                error_message=str(exc)
            )

